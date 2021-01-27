import click

from os.path import abspath, join, dirname

from roboai_cli.util.cli import print_success, print_message
from roboai_cli.util.robo import create_package


@click.command(name="package",
               help="Package the required bot and make it ready for deployment.")
@click.argument("language", nargs=-1,)
@click.option("--model", type=click.Path(), default=None,
              help="Path to the model to be packaged. If no model is passed then the latest one is picked up.")
def command(language: tuple, model: str):
    """

    Package the required bot and make it ready for deployment.

    Args:
        language (tuple): language code of the bot to create a package of.
    """
    if len(language) == 0:
        bot_dir = bot_ignore_dir = abspath(".")
    elif len(language) == 1:
        bot_dir = abspath(join(".", "languages", language[0]))
        bot_ignore_dir = dirname(dirname(bot_dir))
    else:
        print_message("Please select only one bot to package.")
        exit(0)

    package_path = create_package(bot_dir, bot_ignore_dir, model)
    print_message("Package file: {0}".format(package_path))
    print_success("The packaging is complete.\n")


if __name__ == "__main__":
    command()
