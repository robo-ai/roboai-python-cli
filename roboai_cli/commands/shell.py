import click
import os
from os.path import join, abspath
import glob

from roboai_cli.util.helpers import check_installed_packages


@click.command(name="shell", help="Start a shell to interact with the required bot.")
@click.argument("language", nargs=1,)
@click.option("--nlu", "-n", "nlu", is_flag=True, default=False, help="Launch nlu shell.")
@click.option("--response-timeout", "response_timeout", default=3600,
              help="Maximum time a response can take to process (sec). (default: 3600)")
@click.option("--debug", "-d", "debug", is_flag=True,
              help="Prints debugging statements. Sets logging level to DEBUG.")
def command(language: str, nlu: bool, debug: bool, response_timeout: int):
    """
    Wrapper of rasa shell for a multi-language bot.

    Args:
        language (str): language code of the bot for rasa shell to be run
        nlu (bool): flag indicating whether nlu shell should be launched.
        debug (bool): launch shell in debug mode
        response_timeout (int): maximum time a response can take to process (sec.) (default: 3600)
    """
    path = abspath(".")
    if check_installed_packages(path):
        start_shell(language, nlu, debug, response_timeout)


def start_shell(language: str, nlu: bool, debug: bool, response_timeout: int):
    from rasa.cli.utils import get_validated_path
    from rasa.cli.shell import shell, shell_nlu
    import uuid
    conversation_id = uuid.uuid4().hex


    # list_of_models = glob.glob(join(abspath("."), "languages", language, "models", "*.tar.gz"))
    # latest_file = max(list_of_models, key=os.path.getctime)
    model = get_validated_path(None, "model", join(abspath("."), "languages", language, "models"))


    endpoints_path = join(abspath("."), "endpoints.yml")

    if nlu:
        import rasa.nlu.run
        rasa.nlu.run.run_cmdline(model)
        # os.system(f"rasa shell nlu --model {latest_file} {'--debug' if debug else ''}")
    else:
        import rasa.api
        rasa.api.run(
            model,
            endpoints_path,
            "cmdline",
            None
        )
        # os.system(f"rasa shell --model {latest_file} \
        #           --response-timeout {response_timeout} \
        #           {'--debug' if debug else ''} --endpoints {endpoints_path}")


if __name__ == "__main__":
    command()
