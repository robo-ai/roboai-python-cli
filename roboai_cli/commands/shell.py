import click
import os
from os.path import join, abspath
import glob


@click.command(name="shell", help="Start a shell to interact with the required bot.")
@click.argument("language", nargs=1,)
@click.option("--response-timeout", "response_timeout", default=3600,
              help="Maximum time a response can take to process (sec). (default: 3600)")
@click.option("--debug", "-d", "debug", is_flag=True,
              help="Prints debugging statements. Sets logging level to DEBUG.")
def command(language: str, debug: bool, response_timeout: int):
    """
    Wrapper of rasa shell for a multi-language bot.

    Args:
        language (str): language code of the bot for rasa shell to be run
        debug (bool): launch shell in debug mode
        response_timeout (int): maximum time a response can take to process (sec.) (default: 3600)
    """
    start_shell(language, debug, response_timeout)


def start_shell(language: str, debug: bool, response_timeout: int):

    list_of_models = glob.glob(join(abspath("."), "languages", language, "models", "*.tar.gz"))
    latest_file = max(list_of_models, key=os.path.getctime)

    endpoints_path = join(abspath("."), "endpoints.yml")

    os.system(f"rasa shell --model {latest_file} --response-timeout {response_timeout} \
              {'--debug' if debug else ''} --endpoints {endpoints_path}")


if __name__ == "__main__":
    command()
