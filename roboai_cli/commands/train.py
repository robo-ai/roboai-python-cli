import click
import os
from os.path import join
from datetime import datetime

from roboai_cli.util.cli import print_info


@click.command(name="train", help="Train Rasa models for the required bots.")
@click.argument("languages", nargs=-1,)
@click.option("--path", default=".", type=click.Path(), help="Directory of your bot to be trained.")
@click.option("--dev-config", default="config.yml", type=str,
              help="Name of the config file to be used. If this is not passed, default 'config.yml' is used.")
@click.option("--nlu", "-n", "nlu", is_flag=True,
              help="Train exclusively the RASA nlu model for the given languages")
@click.option("--core", "-c", "core", is_flag=True,
              help="Train exclusively the RASA core model for the given languages")
@click.option("--augmentation", "augmentation", default=50, help="How much data augmentation to use during training. \
              (default: 50)")
@click.option("--force", "-f", "force", is_flag=True, default=False,
              help="Force a model training even if the data has not changed. (default: False)")
@click.option("--debug", "-vv", "debug", is_flag=True, default=False,
              help="Print lots of debugging statements. Sets logging level")
def command(languages: tuple, path: str, dev_config: str, nlu: bool, core: bool, augmentation: int, force: bool, debug: bool):
    """
    Wrapper of rasa train for multi-language bots.

    Args:
        languages: language code of the bots to be trained
        path: path where the bot is stored
        dev_config (str): Name of the config file to be used. If this is not passed, default config.yml is used.
        nlu (bool): flag indicating whether only NLU should be trained
        core (bool): flag indicating whether only core should be trained
        augmentation (int): augmentation option
    """

    languages_paths = get_all_languages(path=path, languages=languages)

    if nlu:
        train_nlu(path, languages_paths, dev_config, force, debug)
    elif core:
        train_core(path, languages_paths, augmentation, dev_config, force, debug)
    else:
        train(path, languages_paths, augmentation, dev_config, force, debug)

    # print_success("All training tasks completed")


def _inform_language() -> None:
    """
    Inform the user no languages were passed when executing the train command.
    """
    print_info("No language was provided. Will train all available languages inside provided bot folder.")


def get_all_languages(path: str, languages: tuple):
    if len(languages) == 0:
        _inform_language()
        languages_paths = [join(path, "languages", folder) for folder in os.listdir(join(path, "languages"))
                           if os.path.isdir(os.path.join(path, "languages", folder))]
    else:
        languages_paths = [join(path, "languages", folder) for folder in os.listdir(join(path, "languages"))
                           if os.path.isdir(os.path.join(path, "languages", folder)) and folder in languages]
    return languages_paths


def train(path: str, languages_paths: list, augmentation: int, dev_config: str, force: bool, debug: bool):
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    stories_path = join(path, "languages", "stories.md")
    for language_path in languages_paths:
        lang = os.path.basename(language_path)  # os.path.split(os.path.dirname(language_path))
        os.system(f"rasa train --config {join(language_path, dev_config)} --domain {join(language_path, 'domain.yml')} \
        --data {join(language_path, 'data')} {stories_path} --augmentation {augmentation} {'--force' if force else ''} \
        {'--debug' if debug else ''} --out {join(language_path, 'models')} --fixed-model-name model-{lang}-{timestamp}")


def train_nlu(path: str, languages_paths: list, dev_config: str, force: bool, debug: bool):
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    for language_path in languages_paths:
        lang = os.path.basename(language_path)  # os.path.split(os.path.dirname(language_path))
        os.system(f"rasa train nlu --nlu {join(language_path, 'data')} --config {join(language_path, dev_config)} \
                  {'--debug' if debug else ''} --out {join(language_path, 'models')} --fixed-model-name nlu-model-{lang}-{timestamp}")


def train_core(path: str, languages_paths: list, augmentation: int, dev_config: str, force: bool, debug: bool):
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    stories_path = join(path, 'languages', 'stories.md')
    for language_path in languages_paths:
        lang = os.path.basename(language_path)  # os.path.split(os.path.dirname(language_path))
        os.system(f"rasa train core --domain {join(language_path, 'domain.yml')} --stories {stories_path} \
                  --augmentation {augmentation} --config {join(language_path, dev_config)} {'--force' if force else ''} \
                  {'--debug' if debug else ''} --out {join(language_path, 'models')} --fixed-model-name core-model-{lang}-{timestamp}")


if __name__ == "__main__":
    command()
