import os
from os.path import join
import zipfile
from fnmatch import fnmatch
from time import sleep
from shutil import copyfile, rmtree
from distutils.dir_util import copy_tree
import glob
import ntpath

import click
import polling
from roboai_cli.config.bot_manifest import BotManifest
from roboai_cli.config.tool_settings import ToolSettings
from roboai_cli.config.environment_settings import Environment
from roboai_cli.util.cli import loading_indicator, print_warning
from robo_ai.exception.invalid_credentials_error import InvalidCredentialsError
from robo_ai.exception.invalid_token_error import InvalidTokenError
from robo_ai.exception.not_found_error import NotFoundError
from robo_ai.model.assistant_runtime.assistant_runtime_status import AssistantRuntimeStatus
from robo_ai.model.config import Config
from robo_ai.robo_ai import RoboAi


SUPPORTED_BOT_TYPE = "RASA"

PACKAGE_FILE_NAME = "package.zip"
BUILD_DIR = "build"
TEMP_DIR = "temp_dir"
SUPPORTED_RUNTIME_BASE_VERSIONS = [
    {
        "version": "rasa-1.10.0",
        "label": "Rasa v1.10.0",
    },
]


def get_robo_client(environment: Environment = None, config: Config = None) -> RoboAi:
    # global_settings = ToolSettings()
    if not config:
        base_endpoint = environment.base_url
        http_username = environment.api_auth_setting.username
        http_password = environment.api_auth_setting.password
        config = Config(base_endpoint, http_auth={
            "username": http_username,
            "password": http_password
        })
    robo_ai = RoboAi(config)
    if not environment:
        access_token = ""
    else:
        access_token = environment.api_auth_token
    if access_token:
        robo_ai.set_session_token(access_token)

    return robo_ai


def validate_robo_session():
    settings = ToolSettings()
    current_environment = settings.get_current_environment()
    if not current_environment:
        raise click.UsageError("No environment is currently activated.\nRun 'roboai environment activate <env-name>' to activate"
                               "an environment.")
    api_key = current_environment.api_key
    robo_client = get_robo_client(environment=current_environment)

    # an API key must be set
    if not api_key:
        raise click.UsageError("You are not authenticated, please login using the login command.")

    # if a session isn't started yet, starts a new one
    token = current_environment.api_auth_token
    if not token:
        try:
            robo_client.oauth.authenticate(api_key)
        except InvalidCredentialsError:
            raise click.UsageError("Your current credentials or endpoint configuration are not valid.")
    else:
        # checks if the current token is valid
        try:
            robo_client.oauth.get_token_info(token)
        except InvalidTokenError:
            raise click.UsageError("Your current credentials or endpoint configuration are not valid.")


def validate_bot(bot_uuid: str):
    settings = ToolSettings()
    current_environment = settings.get_current_environment()
    robo = get_robo_client(current_environment)
    try:
        with loading_indicator("Validating bot..."):
            bot = robo.assistants.get_assistant(bot_uuid)
            bot_type = bot.content.assistantService
            if bot_type != SUPPORTED_BOT_TYPE:
                raise click.UsageError(
                    "The selected bot engine is invalid: {0}".format(bot_type))
    except NotFoundError:
        raise click.UsageError("The bot UUID is not valid.")


def does_the_runtime_exist(bot_uuid: str) -> bool:
    settings = ToolSettings()
    current_environment = settings.get_current_environment()
    robo = get_robo_client(current_environment)
    try:
        robo.assistants.runtimes.get(bot_uuid)
        return True
    except NotFoundError:
        return False


def wait_for_runtime_status(bot_uuid: str, status: AssistantRuntimeStatus):
    settings = ToolSettings()
    current_environment = settings.get_current_environment()
    robo = get_robo_client(current_environment)
    polling.poll(
        lambda: robo.assistants.runtimes.get(bot_uuid).content.status == status,
        step=5,
        poll_forever=True,
    )


def wait_for_runtime_non_existence(bot_uuid: str):
    polling.poll(
        lambda: not does_the_runtime_exist(bot_uuid),
        step=5,
        poll_forever=True,
    )


def update_runtime(bot_uuid: str, package_file: str, base_version: str):
    settings = ToolSettings()
    current_environment = settings.get_current_environment()
    robo = get_robo_client(current_environment)
    runtime = robo.assistants.runtimes.get(bot_uuid)
    if runtime.content.status == AssistantRuntimeStatus.RUNNING:
        with loading_indicator("The bot runtime is running, stopping..."):
            robo.assistants.runtimes.stop(bot_uuid)
            wait_for_runtime_status(bot_uuid, AssistantRuntimeStatus.STOPPED)

    total_file_size = os.path.getsize(package_file)
    with click.progressbar(length=total_file_size, label="Uploading package", show_eta=False) as bar:
        robo.assistants.runtimes.update(bot_uuid, package_file, base_version,
                                        progress_callback=lambda bytes_read: bar.update(bytes_read - bar.pos))

    with loading_indicator("Waiting for the bot runtime to start..."):
        wait_for_runtime_status(bot_uuid, AssistantRuntimeStatus.RUNNING)


def create_runtime(bot_uuid: str, package_file: str, base_version: str):
    settings = ToolSettings()
    current_environment = settings.get_current_environment()
    robo = get_robo_client(current_environment)
    total_file_size = os.path.getsize(package_file)
    with click.progressbar(length=total_file_size, label="Uploading package", show_eta=False) as bar:
        robo.assistants.runtimes.create(bot_uuid, package_file, base_version,
                                        progress_callback=lambda bytes_read: bar.update(bytes_read - bar.pos))

    with loading_indicator("Waiting for the bot runtime to be ready (it may take several minutes)..."):
        wait_for_runtime_status(bot_uuid, AssistantRuntimeStatus.CREATED)

    with loading_indicator("Waiting for the bot runtime to start..."):
        robo.assistants.runtimes.start(bot_uuid)
        wait_for_runtime_status(bot_uuid, AssistantRuntimeStatus.RUNNING)


def remove_runtime(bot_uuid: str):
    settings = ToolSettings()
    current_environment = settings.get_current_environment()
    robo = get_robo_client(current_environment)

    if not does_the_runtime_exist(bot_uuid):
        print_warning("The bot runtime does not exist.")
        return

    runtime = robo.assistants.runtimes.get(bot_uuid)
    assert_status_transition(runtime.content.status, AssistantRuntimeStatus.REMOVED, "removed")

    with loading_indicator("Requesting bot runtime deletion..."):
        robo.assistants.runtimes.remove(bot_uuid)

    with loading_indicator("Waiting for the bot runtime to be removed..."):
        wait_for_runtime_non_existence(bot_uuid)


def stop_runtime(bot_uuid: str):
    settings = ToolSettings()
    current_environment = settings.get_current_environment()
    robo = get_robo_client(current_environment)

    runtime = robo.assistants.runtimes.get(bot_uuid)
    assert_status_transition(runtime.content.status, AssistantRuntimeStatus.STOPPED, "stopped")

    with loading_indicator("Requesting bot runtime stop..."):
        robo.assistants.runtimes.stop(bot_uuid)

    with loading_indicator("Waiting for the bot runtime to stop..."):
        wait_for_runtime_status(bot_uuid, AssistantRuntimeStatus.STOPPED)


def start_runtime(bot_uuid: str):
    settings = ToolSettings()
    current_environment = settings.get_current_environment()
    robo = get_robo_client(current_environment)

    if not does_the_runtime_exist(bot_uuid):
        raise click.UsageError("The bot runtime does not exist.")

    runtime = robo.assistants.runtimes.get(bot_uuid)
    assert_status_transition(runtime.content.status, AssistantRuntimeStatus.RUNNING, "started")

    with loading_indicator("Requesting bot runtime start..."):
        robo.assistants.runtimes.start(bot_uuid)

    with loading_indicator("Waiting for the bot runtime to start..."):
        wait_for_runtime_status(bot_uuid, AssistantRuntimeStatus.RUNNING)


def assert_status_transition(current_status: AssistantRuntimeStatus, new_status: AssistantRuntimeStatus, verb: str):
    allowed_transitions = {
        AssistantRuntimeStatus.RUNNING: [
            AssistantRuntimeStatus.STOPPED,
            AssistantRuntimeStatus.REMOVED,
        ],
        AssistantRuntimeStatus.STOPPED: [
            AssistantRuntimeStatus.RUNNING,
            AssistantRuntimeStatus.REMOVED,
        ],
        AssistantRuntimeStatus.CREATED: [
            AssistantRuntimeStatus.RUNNING,
            AssistantRuntimeStatus.REMOVED,
        ],
    }

    if current_status not in allowed_transitions or new_status not in allowed_transitions[current_status]:
        raise click.UsageError("The bot cannot be {0} when in the '{1}' status".format(verb, current_status.value))


def path_leaf(path: str) -> str:
    """
    Taken from https://stackoverflow.com/questions/8384737/extract-file-name-from-path-no-matter-what-the-os-path-format
    (1) There's one caveat: Linux filenames may contain backslashes. So on linux, r'a/b\c' always refers to the file b\c in the a folder, while on Windows,
    it always refers to the c file in the b subfolder of the a folder. So when both forward and backward slashes are used in a path,
    you need to know the associated platform to be able to interpret it correctly.
    In practice it's usually safe to assume it's a windows path since backslashes are seldom used in Linux filenames,
    but keep this in mind when you code so you don't create accidental security holes.

    Args:
        path (str): path to get the basename

    Returns:
        [str]: basename
    """
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def copy_directories(bot_language_dir: str, bot_root_dir: str, model: str):
    """
    Copy files to a temporary directory
    """
    copy_dir(join(bot_root_dir, "actions"), join(TEMP_DIR, "actions"))
    copy_dir(join(bot_language_dir, "data"), join(TEMP_DIR, "data"))
    copy_file(join(bot_root_dir, "languages", "stories.md"), join(TEMP_DIR, "data", "stories.md"))
    os.makedirs(join(TEMP_DIR, "models"), exist_ok=True)
    if model:
        model_name = path_leaf(model)
        copy_file(join(bot_language_dir, "models", model_name), join(TEMP_DIR, "models", model_name))
    else:
        list_of_models = glob.glob(join(bot_language_dir, "models", "*.tar.gz"))
        latest_file = max(list_of_models, key=os.path.getctime)
        model_name = path_leaf(latest_file)
        copy_file(latest_file, join(TEMP_DIR, "models", model_name))
    copy_dir(join(bot_root_dir, "custom"), join(TEMP_DIR, "custom"))
    copy_file(join(bot_language_dir, "config.yml"), join(TEMP_DIR, "config.yml"))
    copy_file(join(bot_root_dir, "credentials.yml"), join(TEMP_DIR, "credentials.yml"))
    copy_file(join(bot_language_dir, "domain.yml"), join(TEMP_DIR, "domain.yml"))
    copy_file(join(bot_root_dir, "endpoints.yml"), join(TEMP_DIR, "endpoints.yml"))
    copy_file(join(bot_root_dir, "__init__.py"), join(TEMP_DIR, "__init__.py"))
    copy_file(join(bot_root_dir, "requirements.txt"), join(TEMP_DIR, "requirements.txt"))
    copy_file(join(bot_root_dir, ".botignore"), join(TEMP_DIR, ".botignore"))
    copy_file(join(bot_language_dir, "robo-manifest.json"), join(TEMP_DIR, "robo-manifest.json"))


def copy_dir(source_path: str, dest_path: str):
    try:
        # print("Trying to copy tree from {} to {}".format(source_path, dest_path))
        copy_tree(source_path, dest_path)
    except Exception:
        print("Couldn't copy tree from {} to {}".format(source_path, dest_path))


def copy_file(source_path: str, dest_path: str):
    try:
        # print("Trying to copy file from {} to {}".format(source_path, dest_path))
        copyfile(source_path, dest_path)
    except Exception:
        print("Couldn't copy file from {} to {}".format(source_path, dest_path))


def create_package(bot_language_dir: str, bot_root_dir: str, model: str) -> str:
    exclusions, exceptions = get_bot_ignore_content(bot_root_dir)
    os.makedirs(BUILD_DIR, exist_ok=True)
    package_file_path = get_default_package_path()

    package_zip = zipfile.ZipFile(package_file_path, "w", zipfile.ZIP_DEFLATED)
    os.makedirs(TEMP_DIR, exist_ok=True)
    copy_directories(bot_language_dir, bot_root_dir, model)
    all_artifacts = []
    for root, dirs, files in os.walk(TEMP_DIR, topdown=True):
        dirs[:] = [directory for directory in dirs
                   if not any(fnmatch(directory, exclusion) for exclusion in exclusions) or any(fnmatch(directory, exception) for exception in exceptions)]
        actual_files = [os.path.join(root, file) for file in files
                        if not any(fnmatch(file, exclusion) for exclusion in exclusions) or any(fnmatch(file, exception) for exception in exceptions)]
        actual_dirs = [os.path.join(root, directory) for directory in dirs
                       if not any(fnmatch(directory, exclusion) for exclusion in exclusions) or any(fnmatch(directory, exception) for exception in exceptions)]
        all_artifacts.extend(actual_files)
        all_artifacts.extend(actual_dirs)

    with click.progressbar(all_artifacts, label="Creating bot runtime package") as bar:
        for artifact in bar:
            package_zip.write(artifact, os.path.relpath(artifact, TEMP_DIR))
            sleep(0.05)  # hack to display the bar, if the process is too fast, the bar does not display

    package_zip.close()
    rmtree(TEMP_DIR)
    return package_file_path


def get_bot_ignore_content(bot_ignore_dir: str):
    with open(join(bot_ignore_dir, ".botignore"), "r") as f:
        bot_ignore = f.read().splitlines()
        return ["%s" % s for s in bot_ignore if not s.startswith("!")], ["%s" % s.replace("!", "").strip() for s in bot_ignore if s.startswith("!")]


def get_default_package_path() -> str:
    return os.path.join(BUILD_DIR, PACKAGE_FILE_NAME)


def validate_package_file(path: str):
    if not os.path.exists(path):
        raise click.UsageError("The package file does not exist.")


def get_current_bot_uuid(bot_dir: str):
    manifest = BotManifest(bot_dir)
    bot_uuid = manifest.get_bot_id()
    if not bot_uuid:
        raise click.UsageError("The bot UUID could not be found. Please verify if the bot is properly initialized and "
                               "your current directory is the bot root directory.")
    return bot_uuid


def get_current_bot_base_version(bot_dir: str):
    manifest = BotManifest(bot_dir)
    base_version = manifest.get_base_version()
    if not base_version:
        raise click.UsageError("The bot runtime base version could not be found.")
    return base_version


def get_bot_runtime(bot_uuid: str):
    settings = ToolSettings()
    current_environment = settings.get_current_environment()
    robo = get_robo_client(current_environment)
    return robo.assistants.runtimes.get(bot_uuid).content


def get_runtime_logs(bot_uuid: str) -> str:
    settings = ToolSettings()
    current_environment = settings.get_current_environment()
    robo = get_robo_client(current_environment)

    if not does_the_runtime_exist(bot_uuid):
        raise click.UsageError("The bot runtime does not exist.")

    logs = robo.assistants.runtimes.get_logs(bot_uuid)
    lines = logs.content.lines
    return "\n".join(lines)


def get_supported_base_versions():
    return SUPPORTED_RUNTIME_BASE_VERSIONS
