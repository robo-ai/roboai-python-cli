import os
import shutil

import click

from robo_bot_cli.util.cli import loading_indicator, print_message, print_success
from robo_bot_cli.util.robo import BUILD_DIR


@click.command(name='clean', help='Clean the last package')
def command():
    """
    Clean (removes) the package if this is available in the bot dir.
    """
    print_message("Cleaning the packaging...")
    with loading_indicator("Cleaning package files..."):
        if os.path.isdir(BUILD_DIR):
            shutil.rmtree(BUILD_DIR)
    print_success("Successfully cleaned")
