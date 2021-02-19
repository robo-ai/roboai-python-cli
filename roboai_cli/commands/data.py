from os import listdir, system
from os.path import abspath, join, exists, isdir

import click
import pandas as pd

from roboai_cli.util.cli import print_info


@click.command(name="data", help="Utility command to split, export and import data.")
@click.argument("utility", nargs=1)
@click.argument("option", nargs=1)
@click.argument("languages", nargs=-1)
@click.option("--input-path", default=".", type=click.Path(), help="Optional input path")
@click.option("--output-path", default=".", type=click.Path(), help="Optional output path")
def command(utility: tuple, option: tuple, languages: tuple, input_path: str, output_path: str):
    """
    Utility command to split, export and import data.

    Args:
        utility (tuple): can be 'split' to split data, 'export' to export data and 'import' to import data
        option (tuple): can be 'nlu', 'domain' or 'all'. It depends on the utility argument.
        languages (tuple): bot language to split, export or import data from.
        input_path (str): optional input path where files are stored.
        output_path (str): optional output path where files are to be stored.
    """

    if option == "export":
        path = input_path
    elif option == "import":
        path = output_path
    else:
        path = "."  # TODO not sure ...

    if len(languages) == 0:
        if exists(join(abspath(path), "languages")):
            bot_dir = get_all_languages(path=abspath(path), languages=languages)
            multi_language_bot = True
        else:
            bot_dir = [abspath(".")]
            multi_language_bot = False
    else:
        bot_dir = get_all_languages(path=abspath(path), languages=languages)
        multi_language_bot = True

    if utility == "split":
        if option == "nlu":
            split_nlu(bot_dir, multi_language_bot)
        else:
            print("Please select a valid option.")
            exit(0)
    elif utility == "export":
        if option == "all":
            export_all(bot_dir, output_path, multi_language_bot)
        if option == "nlu":
            export_nlu(bot_dir, output_path, multi_language_bot)
        elif option == "domain":
            export_domain(bot_dir, output_path, multi_language_bot)
        else:
            print("Please select a valid element to export. It can be either 'nlu', 'domain' or 'all' to export both.")
    elif utility == "import":
        if option == "all":
            import_all(output_path, bot_dir, multi_language_bot)
        elif option == "nlu":
            import_nlu(output_path, bot_dir, multi_language_bot)
        elif option == "domain":
            import_domain(output_path, bot_dir, multi_language_bot)
        else:
            print("Please select a valid element to import. It can be either 'nlu', 'domain' or 'all' to import both.")
    else:
        print("Please select a valid utility option.")
        exit(0)


def split_nlu(bot_dir: list, multi_language_bot: bool):
    for language in bot_dir:
        if multi_language_bot:
            system(f"rasa data split nlu -u {join(language, 'data')} --out {join(language, 'train_test_split')}")
        else:
            system(f"rasa data split nlu -u {join(language, 'data')}")


def convert_nlu_to_df(input_path: str) -> pd.DataFrame:
    pass


def convert_domain_to_df(input_path: str) -> pd.DataFrame:
    pass


def export_nlu(bot_dir: list, output_path: str):
    pass


def export_domain(input_path: str, output_path: str):
    pass


def export_all(output_path: str):
    pass


def import_nlu(input_path: str) -> pd.DataFrame:
    pass


def import_domain(input_path: str) -> pd.DataFrame:
    pass


def import_all():
    pass


def convert_domain_df_to_yaml(domain_df: pd.DataFrame) -> dict:
    pass


def convert_nlu_df_to_md(nlu_df: pd.DataFrame) -> list:  # TODO not sure it's a list!
    pass


def get_all_languages(path: str, languages: tuple) -> list:
    if len(languages) == 0:
        _inform_language()
        languages_paths = [
            join(path, "languages", folder)
            for folder in listdir(join(path, "languages"))
            if isdir(join(path, "languages", folder))
        ]
    else:
        languages_paths = [
            join(path, "languages", folder)
            for folder in listdir(join(path, "languages"))
            if isdir(join(path, "languages", folder)) and folder in languages
        ]
    return languages_paths


def _inform_language() -> None:
    """
    Auxiliary method to inform the user no languages were passed when executing the data command.
    """
    print_info(
        "No language was provided but a multi-language bot was detected. "
        "Will gather all available languages inside provided bot folder.\n"
    )


if __name__ == "__main__":
    command()
