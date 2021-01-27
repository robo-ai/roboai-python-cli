from os.path import abspath, dirname, join

import click
from roboai_cli.util.cli import print_message, print_success
from roboai_cli.util.robo import (
    create_package,
    create_runtime,
    does_the_runtime_exist,
    get_current_bot_base_version,
    get_current_bot_uuid,
    get_default_package_path,
    update_runtime,
    validate_package_file,
    validate_robo_session,
)


@click.command(name="deploy", help="Deploy the current bot into the ROBO.AI platform.")
@click.argument(
    "language",
    nargs=-1,
)
@click.option(
    "--skip-packaging",
    is_flag=True,
    type=bool,
    default=False,
    help="Skips the packaging process, assuming the package is already built.",
)
@click.option(
    "--package-file",
    type=str,
    default=None,
    help="Path to the package file to be deployed, " "setting this option will skip the packaging process.",
)
@click.option("--bot-uuid", type=str, default=None, help="Overrides the bot UUID from the current bot manifest file.")
@click.option(
    "--runtime-base-version",
    type=str,
    default=None,
    help="Overrides the runtime base version from the current bot manifest file.",
)
@click.option(
    "--model",
    type=click.Path(),
    default=None,
    help="Path to the model to be packaged. If no model is passed then the latest one is picked up.",
)
def command(
    language: tuple, skip_packaging: bool, package_file: str, bot_uuid: str, runtime_base_version: str, model: str
):
    """
    Deploy a bot into the ROBO.AI platform.

    Args:
        language: language code of the bot to be deployed
        skip_packaging (bool): optional flag indicating whether packaging should be skipped
        package_file (str): optional flag stating where the package file is stored
        bot_uuid (str): optional argument stating the ID of the bot
        runtime_base_version (str): optional argument stating the runtime version
        model (str): optional argument with the path to the model to be packaged.
                    If no model is passed then the latest one is picked up.
    """
    validate_robo_session()

    if len(language) == 0:
        bot_dir = bot_ignore_dir = abspath(".")
    elif len(language) == 1:
        bot_dir = abspath(join(".", "languages", language[0]))
        bot_ignore_dir = dirname(dirname(bot_dir))
    else:
        print_message("Please select only one bot to deploy.\n")
        exit(0)

    if not bot_uuid:
        bot_uuid = get_current_bot_uuid(bot_dir)

    if not runtime_base_version:
        runtime_base_version = get_current_bot_base_version(bot_dir)

    if package_file:
        validate_package_file(package_file)
    elif not skip_packaging:
        package_file = create_package(bot_dir, bot_ignore_dir, model)
    elif not package_file:
        package_file = get_default_package_path()

    validate_package_file(package_file)

    if does_the_runtime_exist(bot_uuid):
        update_runtime(bot_uuid, package_file, runtime_base_version)
    else:
        create_runtime(bot_uuid, package_file, runtime_base_version)

    print_success("Deployment complete.\n")


if __name__ == "__main__":
    command()
