import os
import click

from roboai_cli.util.parsing import create_true_files
from os.path import abspath, join, exists
from roboai_cli.util.cli import print_error, print_info, print_success, loading_indicator
from roboai_cli.util.parsing import TEMPLATES_FOLDER_NAME

TEST_FOLDER_NAME = os.path.join("roboai_tests", TEMPLATES_FOLDER_NAME)


@click.command(name="create_tests", help="Create the true files in the desired format.")
@click.argument("languages", nargs=-1)
@click.option("--domain-path", default=None, type=str, help="Specifies the domain path")
@click.option("--template-path", "--tp", multiple=True, default=None, type=str, help="Specifies the templates path")
@click.option("--template", "--t", multiple=True, default=None, type=str, help="Specifies the template name")
def command(languages: tuple, domain_path: str, template_path: tuple, template: tuple):

    if not template:

        if not domain_path and not template_path:
            if exists(join(abspath("."), "languages")):
                list_domain_dir = get_all_languages(path=abspath("."), languages=languages)

                while list_domain_dir:
                    lang_domain_dir = list_domain_dir.pop()
                    template_dir = [join(lang_domain_dir, TEST_FOLDER_NAME)]

                    if path_exist(lang_domain_dir, template_dir): # and not len([template_dir])
                        with loading_indicator("Creating true files..."):
                            create_true_files(lang_domain_dir, template_dir)

            else:
                domain_dir = abspath(".")
                template_dir = [join(abspath("."), TEST_FOLDER_NAME)]

                if path_exist(domain_dir, template_dir):
                    with loading_indicator("Creating true files..."):
                        create_true_files(domain_dir, template_dir)

            print_success("Tests created successfully")

        elif domain_path and template_path:
            with loading_indicator("Creating true files..."):

                template_path = list(template_path)

                if path_exist(domain_path, template_path):
                    create_true_files(domain_path, template_path)

            print_success("Tests created successfully")

        elif domain_path is None:
            print_error("Domain path not inserted")

        else:
            print_error("Templates path not inserted")

    else:
        if not domain_path and not template_path:
            with loading_indicator("Creating true files..."):
                if exists(join(abspath("."), "languages")):
                    list_domain_dir = get_all_languages(path=abspath("."), languages=languages)

                    while list_domain_dir:
                        lang_domain_dir = list_domain_dir.pop()
                        template = list(template)
                        template_full_path = []

                        for path in template:
                            template_full_path.append(join(lang_domain_dir, TEST_FOLDER_NAME, path))

                        if path_exist(lang_domain_dir, template_full_path):
                            create_true_files(lang_domain_dir, template_full_path)
                else:
                    domain_dir = abspath(".")
                    template = list(template)
                    template_full_path = []

                    for path in template:
                        template_full_path.append(join(domain_dir, TEST_FOLDER_NAME, path))

                    if path_exist(domain_dir, template_full_path):
                        create_true_files(domain_dir, template_full_path)

                print_success("Tests created successfully")

        elif domain_path:
            print_error("Template command does not need domain specification")

        elif template_path:
            print_error("Template command does not need template_path specification")


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


def path_exist(domain: str, templates: list):

    if not exists(domain):
        print_error(f"\nDomain path not found: {domain}")
        print_error('Unable to create all tests')
        quit()

    for template in templates:
        if not exists(template):
            print_error(f"\nTemplate path not found: {template}")
            print_error('Unable to create all tests')
            quit()

    return True


def _inform_language() -> None:
    """
    Auxiliary method to inform the user no languages were passed when executing the test command.
    """
    print_info(
        "No language was provided but a bot was detected.\n"
        "Will test all available languages inside provided bot folder.\n"
    )


if __name__ == "__main__":
    command()
