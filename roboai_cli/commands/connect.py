import math
import os
from os.path import dirname, isfile, join
from shutil import copyfile

import click
import pkg_resources
from questionary import Choice, prompt
from robo_ai.model.assistant.assistant import Assistant
from robo_ai.model.assistant.assistant_list_response import (
    AssistantListResponse,
)

from roboai_cli.config.bot_manifest import BotManifest
from roboai_cli.config.tool_settings import ToolSettings
from roboai_cli.util.cli import (
    loading_indicator,
    print_message,
    print_success,
)
from roboai_cli.util.robo import (
    get_robo_client,
    get_supported_base_versions,
    validate_robo_session,
)


@click.command(name="connect", help="Connect a local bot to a ROBO.AI server bot instance.",)
@click.argument("language", nargs=-1,)
@click.option("--bot-uuid", default=None, type=str, help="The bot UUID to assign to the bot implementation.",)
@click.option("--target-dir", default=None, type=str, help="The target directory where the bot will be setup.",)
def command(
    language: tuple,
    bot_uuid: str,
    target_dir: str,
    base_version: str = "rasa-1.10.0",
):
    """
    Connect a local bot to a ROBO.AI server bot instance.
    This instance must be already created in the ROBO.AI platform.
    This command will generate a JSON file (robo-manifest) with metadata about the bot to be deployed.

    Args:
        language: language code of the bot to be connected.
        bot_uuid (str): optional argument stating the ID of the bot.
        target_dir (str): optional argument stating where the robo-manifest file should be stored.
        base_version (str): optional argument stating the engine base version. Defaults to 'rasa-1.10.0'
    """
    validate_robo_session()

    if not bot_uuid:
        bot_uuid = get_bot_uuid()

    # validate_bot(bot_uuid)

    if len(language) == 0:
        bot_dir = bot_ignore_dir = (
            os.path.abspath(target_dir) if target_dir else create_implementation_directory(bot_uuid)
        )
    elif len(language) == 1:
        bot_dir = (
            os.path.abspath(join(target_dir, "languages", language[0]))
            if target_dir
            else create_implementation_directory(bot_uuid)
        )  # TODO check what this does
        bot_ignore_dir = join(dirname(dirname(bot_dir)))
    else:
        print_message("Please select only one bot to connect to.")
        exit(0)

    print_message("Bot target directory: {0}".format(bot_dir))

    create_bot_manifest(bot_dir, bot_uuid, base_version)
    create_bot_ignore(bot_ignore_dir)
    print_success("The bot was successfully initialized.")


def get_bots(page: int) -> AssistantListResponse:
    """
    Retrieves the list of bots from the ROBO.AI platform.

    Args:
        page (int): current page.

    Returns:
        AssistantListResponse: list of bots available in the current page.
    """
    settings = ToolSettings()
    current_environment = settings.get_current_environment()
    robo = get_robo_client(current_environment)
    return robo.assistants.get_list(page)


def get_bot_choice(bot: Assistant) -> dict:
    """
    Get bot name and ID in a dictionary.

    Args:
        bot (Assistant): Assistant object to get details from.

    Returns:
        dict: dictionary with assistant's name and ID.
    """
    return {
        "name": bot.name,
        "value": bot.uuid,
    }


def get_bot_uuid() -> str:
    """
    Show bot options to the user, returns the selected bot ID.

    Returns:
        bot_uuid (str): ID of the selected bot.
    """
    NEXT_PAGE = "__NEXT_PAGE__"
    PREV_PAGE = "__PREV_PAGE__"
    NONE = "__NONE__"
    META_RESPONSES = [NEXT_PAGE, PREV_PAGE, NONE]

    bot_uuid = NONE
    page = 0
    while bot_uuid in META_RESPONSES:
        if bot_uuid == NEXT_PAGE:
            page += 1

        if bot_uuid == PREV_PAGE:
            page -= 1

        with loading_indicator("Loading bot list..."):
            bots = get_bots(page)
        bot_choices = list(map(get_bot_choice, bots.content))
        page_count = math.ceil(bots.totalElements / bots.size)
        if page < page_count - 1:
            bot_choices.append({"name": "> Next page...", "value": NEXT_PAGE})

        if page > 0:
            bot_choices.append({"name": "> Previous page...", "value": PREV_PAGE})

        questions = [
            {
                "type": "list",
                "name": "bot_id",
                "message": "Please select the bot you would like to implement:",
                "choices": [
                    Choice(title=bot["name"], value=bot["value"])
                    if (bot["value"] == NEXT_PAGE or bot["value"] == PREV_PAGE)
                    else Choice(
                        title=str(bot["name"] + " (" + bot["value"] + ")"),
                        value=bot["value"],
                    )
                    for bot in bot_choices
                ],
            },
        ]

        answers = prompt(questions)
        bot_uuid = answers["bot_id"]

    return bot_uuid


def get_base_version() -> str:
    """
    Show runtime options to the user.

    Returns:
        base_version (str): selected base version
    """
    with loading_indicator("Loading base version list..."):
        versions = get_supported_base_versions()

    version_choices = [{"value": base_version["version"], "name": base_version["label"]} for base_version in versions]

    questions = [
        {
            "type": "list",
            "name": "base_version",
            "message": "Please select the bot runtime version:",
            "choices": version_choices,
        },
    ]
    answers = prompt(questions)
    base_version = answers["base_version"]

    return base_version


def create_implementation_directory(bot_uuid: str) -> str:
    cwd = os.getcwd()
    bot_dir = cwd + "/" + bot_uuid
    os.mkdir(bot_dir)
    return bot_dir


def create_bot_manifest(bot_dir: str, bot_uuid: str, base_version: str):
    with loading_indicator("Creating bot manifest file..."):
        manifesto = BotManifest(bot_dir)
        manifesto.set_bot_id(bot_uuid)
        manifesto.set_base_version(base_version)


def create_bot_ignore(bot_ignore_dir: str):
    if not isfile(join(bot_ignore_dir, ".botignore")):
        copyfile(get_bot_ignore_path(), join(bot_ignore_dir, ".botignore"))


def get_bot_ignore_path() -> str:
    return pkg_resources.resource_filename(__name__, "../initial_structure/initial_project/.botignore")


if __name__ == "__main__":
    command()
