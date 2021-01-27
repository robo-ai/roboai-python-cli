import click
from os.path import abspath, join
from datetime import datetime

from roboai_cli.util.cli import print_message
from roboai_cli.util.robo import (
    does_the_runtime_exist,
    validate_robo_session,
    get_current_bot_uuid,
    get_bot_runtime
)


@click.command(name="status", help="Display the bot status.")
@click.argument("language", nargs=-1,)
@click.option("--bot-uuid", type=str, default=None,
              help="The bot UUID to use, it overrides the bot UUID configured in the manifest.")
def command(language: tuple, bot_uuid: str):
    """
    Display the bot status

    Args:
        language (tuple): language code of the bot for the status to be shown
        bot_uuid (str): optional argument stating the bot ID for the status to be shown
    """
    validate_robo_session()

    if len(language) == 0:
        bot_dir = abspath(".")
    elif len(language) == 1:
        bot_dir = abspath(join(".", "languages", language[0]))
    else:
        print_message("Please select only one bot to check the status.\n")
        exit(0)

    if not bot_uuid:
        bot_uuid = get_current_bot_uuid(bot_dir)

    print_message("Bot UUID: {0}".format(bot_uuid))

    if does_the_runtime_exist(bot_uuid):
        runtime = get_bot_runtime(bot_uuid)
        print_message("Bot runtime status: {0}".format(runtime.status.value))
        if runtime.createdAt != "None":
            print_message("Runtime created at: {0}".format(
                datetime.strptime(runtime.createdAt, "%Y-%m-%dT%H:%M:%S.%f%z").strftime("%b %d %Y %H:%M:%S")))
    else:
        print_message("Bot runtime status: Not Created\n")


if __name__ == "__main__":
    command()
