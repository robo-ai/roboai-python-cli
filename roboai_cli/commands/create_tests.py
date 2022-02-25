import os

import click
from roboai_cli.util.automate import automate
from os.path import abspath, join, exists
from roboai_cli.util.cli import print_error, print_info, print_success

TEST_FOLDER_NAME = "roboai_tests"


@click.command(name="create_tests", help="Create tests in the desired format")
@click.argument("languages", nargs=-1)
@click.option("--domain-path", default=None, type=str, help="Specifies the domain path")
@click.option("--template-path", default=None, type=str, help="Specifies the templates path")
def command(languages: tuple, domain_path: str, template_path: str):

    if domain_path is None and template_path is None:
        if exists(join(abspath("."), "languages")):
            list_domain_dir = get_all_languages(path=abspath("."), languages=languages)

            while list_domain_dir:
                lang_domain_dir = list_domain_dir.pop()
                template_dir = join(lang_domain_dir, TEST_FOLDER_NAME)

                if paths_exist(lang_domain_dir, template_dir):
                    automate(lang_domain_dir, [template_dir])

        else:
            domain_dir = abspath(".")
            template_dir = join(abspath("."), TEST_FOLDER_NAME)

            if paths_exist(domain_dir, template_dir):
                automate(domain_dir, [template_dir])

        print_success("Creating true files process completed")

    elif domain_path is not None and template_path is not None:

        if paths_exist(domain_path, template_path):
            automate(domain_path, [template_path])

        print_success("Creating true files process completed")

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
        "No language was provided but a multi-language bot was detected. "
        "Will test all available languages inside provided bot folder.\n"
    )


def paths_exist(domain: str, templates: str):

    if not exists(domain):
        print_error(f"Domain path not found: {domain}")

    if not exists(templates):
        print_error(f"Templates path not found: {templates}")

    return exists(domain) and exists(templates)


if __name__ == "__main__":
    command()
