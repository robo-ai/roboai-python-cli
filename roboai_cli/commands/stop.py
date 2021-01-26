import click
from os.path import abspath, join

from roboai_cli.util.cli import print_success, print_message
from roboai_cli.util.robo import validate_robo_session, get_current_bot_uuid, stop_runtime


@click.command(name="stop", help="Stop a bot running in the ROBO.AI platform.")
@click.argument("language", nargs=-1,)
@click.option("--bot-uuid", type=str, default=None,
              help="The bot UUID to use, it overrides the bot UUID configured in the manifest.")
def command(language: tuple, bot_uuid: str):
    """
    Stop a bot running in the ROBO.AI platform.

    Args:
        language: language code of the bot to be stopped
        bot_uuid (str): optional argument stating the bot ID to be stopped.
    """
    validate_robo_session()

    if len(language) == 0:
        bot_dir = abspath(".")
    elif len(language) == 1:
        bot_dir = abspath(join(".", "languages", language[0]))
    else:
        print_message("Please select only one bot runtime to be stopped.\n")
        exit(0)

    if not bot_uuid:
        bot_uuid = get_current_bot_uuid(bot_dir)

    # validate_bot(bot_uuid)
    stop_runtime(bot_uuid)
    print_success("The bot runtime was successfully stopped.\n")
