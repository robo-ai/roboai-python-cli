import click
import os
from os.path import join

from robo_bot_cli.util.cli import print_info


@click.command(name='train', help='Train Rasa models for the required bots.')
@click.argument('languages', nargs=-1,)
@click.option('--path', default='.', type=click.Path(), help="Directory of your bot to be trained.")
@click.option('--nlu', '-n', 'nlu', is_flag=True,
              help="Train exclusively the RASA nlu model for the given languages")
@click.option('--core', '-c', 'core', is_flag=True,
              help="Train exclusively the RASA core model for the given languages")
@click.option('--augmentation', 'augmentation', default=50, help="How much data augmentation to use during training. \
              (default: 50)")
def command(languages: tuple, path: str, nlu: bool, core: bool, augmentation: int):
    """
    Wrapper of rasa train for multi-language bots.

    Args:
        languages: language code of the bots to be trained
        path: path where the bot is stored
        nlu (bool): flag indicating whether only NLU should be trained
        core (bool): flag indicating whether only core should be trained
        augmentation (int): augmentation option
    """

    languages_paths = get_all_languages(path=path, languages=languages)

    if nlu:
        train_nlu(path, languages_paths)
    if core:
        train_core(path, languages_paths, augmentation)
    else:
        train(path, languages_paths, augmentation)

    # print_success("All training tasks completed")


def _inform_language() -> None:
    """
    Auxiliary method to inform the user no languages were passed when executing the train command.
    """
    print_info("No language was provided. Will train all available languages inside provided bot folder.")


def get_all_languages(path: str, languages: tuple):
    if len(languages) == 0:
        _inform_language
        languages_paths = [join(path, 'languages', folder) for folder in os.listdir(join(path, 'languages'))
                           if os.path.isdir(os.path.join(path, 'languages', folder))]
    else:
        languages_paths = [join(path, 'languages', folder) for folder in os.listdir(join(path, 'languages'))
                           if os.path.isdir(os.path.join(path, 'languages', folder)) and folder in languages]
    return languages_paths


def train(path: str, languages_paths: list, augmentation: int):
    stories_path = join(path, 'languages', 'stories.md')
    for language_path in languages_paths:
        lang = os.path.basename(language_path)  # os.path.split(os.path.dirname(language_path))
        os.system(f"rasa train --config {join(language_path,'config.yml')} --domain {join(language_path,'domain.yml')} \
        --data {join(language_path,'data')} {stories_path} --augmentation {augmentation} \
        --out {join(language_path, 'models')} --fixed-model-name model-{lang}")
        # print_success(f"Bot \'{lang}\' successfully trained!")


def train_nlu(path: str, languages_paths: list):
    for language_path in languages_paths:
        lang = os.path.basename(language_path)  # os.path.split(os.path.dirname(language_path))
        os.system(f"rasa train nlu --nlu {join(language_path,'data')} --config {join(language_path,'config.yml')} \
                  --out {join(language_path, 'models')} --fixed-model-name nlu-model-{lang}")
        # print_success(f"Bot \'{lang}\' successfully trained!")


def train_core(path: str, languages_paths: list, augmentation: int):
    stories_path = join(path, 'languages', 'stories.md')
    for language_path in languages_paths:
        lang = os.path.basename(language_path)  # os.path.split(os.path.dirname(language_path))
        os.system(f"rasa train core --domain {join(language_path,'domain.yml')} --stories {stories_path} \
                  --augmentation {augmentation} --config {join(language_path,'config.yml')} \
                  --out {join(language_path, 'models')} --fixed-model-name core-model-{lang}")
        # print_success(f"Bot \'{lang}\' successfully trained!")


if __name__ == "__main__":
    command()
