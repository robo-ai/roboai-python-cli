from os.path import abspath, join, exists

import click
from roboai_cli.util.cli import loading_indicator, print_info, print_message, print_error
from roboai_cli.util.robo import (
    get_current_bot_uuid,
    get_runtime_logs,
    validate_robo_session
)
import roboai_cli.util.report_helper


@click.command(name='report', help='Create a Robo.AI Report from a Conversation log file.')
@click.argument('file', nargs=-1,)
@click.option('--file-format',
              type=str,
              default="roboai_csv",
              help='The format of the conversation Log')
@click.option('--nlu-threshold',
              type=float,
              default=0.5,
              help='Minimum threshold for NLU confidence')
@click.option('--ambiguity-threshold',
              type=float,
              default=0.1,
              help='Threshold for minimum difference between confidences of the top two predictions')


def command(file: tuple, file_format: str, nlu_threshold: float, ambiguity_threshold: float):
    """
    Create a Report from the conversational log file

    Args:
        language: language code of the bot to get logs from
        bot_uuid (str): optional argument stating the ID of the bot to get logs from
    """

    print_error("🚨 🛑 THIS FEATURE IS EXPERIMENTAL 🛑 🚨")

    if len(file) == 0:
        file_dir = abspath(join('.', "logs.csv"))
    elif len(file) == 1:
        file_dir = abspath(join('.', file[0]))
    else:
        print_message('Please select one conversation log at a time.')
        exit(0)

    report_tool = roboai_cli.util.report_helper.Report(file_dir, file_format, nlu_threshold, ambiguity_threshold)
    report_tool.run()
