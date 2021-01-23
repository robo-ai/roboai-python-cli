from os.path import abspath, join

import click
from roboai_cli.util.cli import loading_indicator, print_info, print_message
from roboai_cli.util.robo import (
    get_current_bot_uuid,
    get_runtime_logs,
    validate_robo_session
)


@click.command(name='logs', help='Display selected bot runtime logs.')
@click.argument('language', nargs=-1,)
@click.option('--bot-uuid',
              type=str,
              default=None,
              help='The bot UUID to use, it overrides the bot UUID configured \
              in the manifest.')
def command(language: tuple, bot_uuid: str):
    """
    display selected bot runtime logs.

    Args:
        language: language code of the bot to get logs from
        bot_uuid (str): optional argument stating the ID of the bot to get logs from
    """
    validate_robo_session()

    if len(language) == 0:
        bot_dir = abspath('.')
    elif len(language) == 1:
        bot_dir = abspath(join('.', 'languages', language[0]))
    else:
        print_message('Please select only one bot to check the logs.')
        exit(0)

    if not bot_uuid:
        bot_uuid = get_current_bot_uuid(bot_dir)

    # validate_bot(bot_uuid)

    with loading_indicator('Fetching logs from server...'):
        logs = get_runtime_logs(bot_uuid)

    print_info("Displaying logs for bot '{0}'\n".format(bot_uuid))
    print_message(logs + "\n")
