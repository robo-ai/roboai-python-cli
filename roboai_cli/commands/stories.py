import click
import os
from os.path import abspath, join, exists, isfile, basename
from os import listdir

from roboai_cli.util.cli import print_info, print_error
from roboai_cli.util.input_output import load_md, load_yaml
from roboai_cli.util.helpers import clean_intents


@click.command(name="stories", help="Generate stories for a Rasa bot.")
@click.argument("languages", nargs=-1,)
@click.option("-cci", "--check-covered-intents", "covered_intents", is_flag=True,
              help="Checks covered intents in stories file.")
def command(languages: tuple, covered_intents: bool):
    """Generates stories for a rasa bot

    Args:
        languages (tuple): languages (bots) to be tested. If no language is passed
                           it checks if the current bot is a multi-language bot. If so
                           all bots will be tested. Otherwise the single-language bot will
                           be tested.
        covered_intents (bool): flag to check which intents are being covered in the stories file.
    """
    if len(languages) == 0:
        if exists(join(abspath("."), "languages")):
            # it means it's a multi language bot
            multi_language = True
            bot_dir = get_all_languages(path=abspath("."), languages=languages)
        else:
            # it means it's a single language bot
            multi_language = False
            bot_dir = [abspath(".")]
    else:
        multi_language = True
        bot_dir = get_all_languages(path=abspath("."), languages=languages)

    if covered_intents:
        check_covered_intents(bot_dir, multi_language)
    else:
        generate_stories(bot_dir, multi_language)


def generate_stories(languages_path: list, multi_language_bot: bool) -> None:
    for language in languages_path:
        lang = basename(language) if basename(language) != "bot" else "the"

        if multi_language_bot:
            stories_dir_path = join(abspath("."), "languages")
        else:
            stories_dir_path = join(language, "data")

        stories_exist = False
        # check if there's already a stories file - ask if it should be overriden?
        for filename in listdir(join(stories_dir_path)):
            if isfile(join(stories_dir_path, filename)):
                if "stories" in filename:
                    stories_exist = True
                    break
        if stories_exist:
            overwrite = click.confirm(
                "Stories file already exists. This action will overwrite it. Continue?"
            )
            if overwrite:
                generate_stories_md(language, multi_language_bot)
            else:
                exit(0)
        else:
            generate_stories_md(language, multi_language_bot)

        print_info(f"Generated stories for {lang} bot")


def check_covered_intents(language_path: list, multi_language_bot: bool):
    for language in language_path:
        intents = load_yaml(join(language, "domain.yml")).get("intents", None)
        if intents is None:
            print_error("No intents were found.\n")
            exit(0)
        else:
            intents = clean_intents(intents)
            check_specific_stories = False
            if multi_language_bot:
                stories_dir_path = join(abspath("."), "languages")
                check_specific_stories = True
            else:
                stories_dir_path = join(language, "data")
            for filename in listdir(stories_dir_path):
                if isfile(join(stories_dir_path, filename)):
                    if "stories" in filename:
                        lines = load_md(join(stories_dir_path, filename))
                        for line in lines:
                            for intent in intents:
                                if intent in line:
                                    intents.remove(intent)
                                    break
            if check_specific_stories:
                lang = basename(language)
                for filename in listdir(join(stories_dir_path, lang, "data")):
                    if isfile(join(stories_dir_path, lang, "data", filename)):
                        if "stories" in filename:
                            lines = load_md(join(stories_dir_path, lang, "data", filename))
                            for line in lines:
                                for intent in intents:
                                    if intent in line:
                                        intents.remove(intent)
                                        break
            if intents:
                print("The following intents are not covered in your stories:")
                print(*intents, sep="\n")


def generate_stories_md(path_to_language: str, multi_language_bot: bool):
    domain = load_yaml(join(path_to_language, "domain.yml"))
    intents_list = domain.get("intents", None)
    if not intents_list:
        print_error("No intents were found.")
        exit(0)
    elif intents_list:
        intents_list = clean_intents(intents_list)
        if multi_language_bot:
            output_path = join(abspath("."), "languages", "stories.md")
        else:
            output_path = join(path_to_language, "data", "stories.md")

        with open(output_path, "w", encoding="utf-8") as out_f:
            for intent in intents_list:
                out_f.write(f"## {intent}\n")
                out_f.write(f"* {intent}\n")
                out_f.write(f"  - utter_{intent}\n")
                out_f.write("\n")


def get_all_languages(path: str, languages: tuple) -> list:
    if len(languages) == 0:
        _inform_language()
        languages_paths = [join(path, "languages", folder) for folder in os.listdir(join(path, "languages"))
                           if os.path.isdir(os.path.join(path, "languages", folder))]
    else:
        languages_paths = [join(path, "languages", folder) for folder in os.listdir(join(path, "languages"))
                           if os.path.isdir(os.path.join(path, "languages", folder)) and folder in languages]
    return languages_paths


def _inform_language() -> None:
    """
    Auxiliary method to inform the user no languages were passed when executing the test command.
    """
    print_info("No language was provided but a multi-language bot was detected. "
               "Please choose one of the bots for the stories to be generated.\n")
    exit(0)


if __name__ == "__main__":
    command()
