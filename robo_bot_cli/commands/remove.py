from os.path import abspath, join

import click

from robo_bot_cli.util.cli import print_message, print_success
from robo_bot_cli.util.robo import (
    get_current_bot_uuid,
    remove_runtime,
    validate_bot,
    validate_robo_session,
)


@click.command(
    name="remove", help="Remove a deployed bot from the ROBO.AI platform."
)
@click.argument(
    "language",
    nargs=-1,
)
@click.option(
    "--bot-uuid",
    type=str,
    default=None,
    help="The bot UUID to use, \
              it overrides the bot UUID configured in the manifest.",
)
def command(language: tuple, bot_uuid: str):
    """
    Remove a deployed bot from the ROBO.AI platform

    Args:
        language (tuple): language code of the bot to be removed
        bot_uuid (str): optional argument stating the ID of the bot to be removed
    """
    validate_robo_session()
    if len(language) == 0:
        bot_dir = abspath(".")
    elif len(language) == 1:
        bot_dir = abspath(join(".", "languages", language[0]))
    else:
        print_message("Please select only one bot to remove.")
        exit(0)
    if not bot_uuid:
        bot_uuid = get_current_bot_uuid(bot_dir)

    validate_bot(bot_uuid)
    remove_runtime(bot_uuid)
    print_success("The bot runtime was successfully removed.")
