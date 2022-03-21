import os

import click
from roboai_cli.util.automate import automate, paths_exist
from os.path import abspath, join, exists
from roboai_cli.util.cli import print_error, print_info, print_success, loading_indicator

from roboai_cli.util.parsing import TEMPLATES_FOLDER_NAME
TEST_FOLDER_NAME = os.path.join("roboai_tests", TEMPLATES_FOLDER_NAME)


@click.command(name="create_tests", help="Create tests in the desired format")
@click.argument("languages", nargs=-1)
@click.option("--domain-path", default=None, type=str, help="Specifies the domain path")
@click.option("--templates-path", "-t", multiple=True, default=None, type=str, help="Specifies the templates path")
@click.option("--template", default=None, type=list, help="Specifies the template name")
def command(languages: tuple, domain_path: str, templates_path: tuple, template: str):
    if not domain_path and not templates_path:
        with loading_indicator("Creating true files..."):
            if exists(join(abspath("."), "languages")):
                list_domain_dir = get_all_languages(path=abspath("."), languages=languages)

                while list_domain_dir:
                    lang_domain_dir = list_domain_dir.pop()
                    template_dir = [join(lang_domain_dir, TEST_FOLDER_NAME)]

                    if paths_exist(lang_domain_dir, template_dir): # and not len([template_dir])
                        automate(lang_domain_dir, template_dir)

            else:
                domain_dir = abspath(".")
                template_dir = [join(abspath("."), TEST_FOLDER_NAME)]

                if paths_exist(domain_dir, template_dir):
                    automate(domain_dir, template_dir)

        print_success("Tests created successfully")

    elif domain_path and templates_path:
        with loading_indicator("Creating true files..."):

            template_path = list(templates_path)

            if paths_exist(domain_path, template_path):
                automate(domain_path, template_path)

        print_success("Tests created successfully")

    elif domain_path is None:
        print_error("Domain path not inserted")

    else:
        print_error("Templates path not inserted")


def get_all_languages(path: str, languages: tuple) -> list:
    if len(languages) == 0:
        _inform_language()
        languages_paths = [
            join(path, "languages", folder)
            for folder in os.listdir(join(path, "languages"))
            if os.path.isdir(os.path.join(path, "languages", folder))
        ]
    else:
        languages_paths = [
            join(path, "languages", folder)
            for folder in os.listdir(join(path, "languages"))
            if os.path.isdir(os.path.join(path, "languages", folder)) and folder in languages
        ]
    return languages_paths


def _inform_language() -> None:
    """
    Auxiliary method to inform the user no languages were passed when executing the test command.
    """
    print_info(
        "No language was provided but a bot was detected."
        "Will test all available languages inside provided bot folder.\n"
    )


if __name__ == "__main__":
    command()
