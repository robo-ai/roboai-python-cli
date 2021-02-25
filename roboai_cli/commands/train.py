import click
import os
from os.path import join, abspath
from datetime import datetime

from roboai_cli.util.cli import print_info
from roboai_cli.util.helpers import check_installed_packages


@click.command(name="train", help="Train Rasa models for the required bots.")
@click.argument("languages", nargs=-1,)
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
@click.option("--training-data-path", default=None, type=click.Path(), help="Path to where training data is stored.")
def command(languages: tuple,
            dev_config: str,
            nlu: bool, core: bool,
            augmentation: int,
            force: bool,
            debug: bool,
            training_data_path: str):
    """
    Wrapper of rasa train for multi-language bots.

    Args:
        languages: language code of the bots to be trained
        dev_config (str): Name of the config file to be used. If this is not passed, default config.yml is used.
        nlu (bool): flag indicating whether only NLU should be trained
        core (bool): flag indicating whether only core should be trained
        augmentation (int): augmentation option
        force (bool): flag indicating whether training should be forced
        debug (bool): flag indicating whether debug mode is enabled
        training_data_path (str): Path to training data in case you have split it before.
    """
    path = abspath(".")

    if check_installed_packages(path):
        languages_paths = get_all_languages(path=path, languages=languages)

        if nlu:
            train_nlu(path, languages_paths, dev_config, force, debug, training_data_path)
        elif core:
            train_core(path, languages_paths, augmentation, dev_config, force, debug)
        else:
            train(path, languages_paths, augmentation, dev_config, force, debug, training_data_path)


def train(path: str, languages_paths: list, augmentation: int, dev_config: str, force: bool, debug: bool, training_data_path: str):
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    stories_path = join(path, "languages", "stories.md")
    for language_path in languages_paths:
        lang = os.path.basename(language_path)
        os.system(f"rasa train --config {join(language_path, dev_config)} --domain {join(language_path, 'domain.yml')} \
                  --data {join(language_path, 'data') if not training_data_path else join(language_path, training_data_path)} {stories_path} \
                  --augmentation {augmentation} {'--force' if force else ''} \
                  {'--debug' if debug else ''} --out {join(language_path, 'models')} \
                  --fixed-model-name model-{lang}-{timestamp}")


def train_nlu(path: str, languages_paths: list, dev_config: str, force: bool, debug: bool, training_data_path: str):
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    for language_path in languages_paths:
        lang = os.path.basename(language_path)
        os.system(f"rasa train nlu --nlu {join(language_path, 'data') if not training_data_path else join(language_path, training_data_path)} \
                  --config {join(language_path, dev_config)} \
                  {'--debug' if debug else ''} --out {join(language_path, 'models')} \
                  --fixed-model-name nlu-model-{lang}-{timestamp}")


def train_core(path: str, languages_paths: list, augmentation: int, dev_config: str, force: bool, debug: bool):
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    stories_path = join(path, 'languages', 'stories.md')
    for language_path in languages_paths:
        lang = os.path.basename(language_path)
        os.system(f"rasa train core --domain {join(language_path, 'domain.yml')} --stories {stories_path} \
                  --augmentation {augmentation} --config {join(language_path, dev_config)} {'--force' if force else ''} \
                  {'--debug' if debug else ''} --out {join(language_path, 'models')} --fixed-model-name core-model-{lang}-{timestamp}")


def get_all_languages(path: str, languages: tuple):
    if len(languages) == 0:
        print_info("No language was provided. Will train all available languages inside provided bot folder.")
        languages_paths = [join(path, "languages", folder) for folder in os.listdir(join(path, "languages"))
                           if os.path.isdir(os.path.join(path, "languages", folder))]
    else:
        languages_paths = [join(path, "languages", folder) for folder in os.listdir(join(path, "languages"))
                           if os.path.isdir(os.path.join(path, "languages", folder)) and folder in languages]
    return languages_paths


if __name__ == "__main__":
    command()
