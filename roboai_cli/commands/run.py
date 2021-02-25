import os
from os.path import abspath

import click

from roboai_cli.util.helpers import check_installed_packages


@click.command(name="run", help="Start the action server.")
@click.argument("actions", nargs=1,)
@click.option("--debug", "-d", "debug",
              is_flag=True,
              help="Prints debugging statements. \
              Sets logging level to DEBUG.")
def command(debug: bool, actions: str):
    """
    Wrapper of rasa run actions

    Args:
        debug (bool): optional flag on whether to start the action server on debug
        actions (str): argument refering to the action server
    """
    path = abspath(".")
    if check_installed_packages(path):
        start_actions(debug, actions)


def start_actions(debug: bool, actions: str):
    os.system(f"rasa run {actions} {'--debug' if debug else ''}")


if __name__ == "__main__":
    command()
