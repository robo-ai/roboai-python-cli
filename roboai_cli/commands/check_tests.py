import os
import click

from os.path import exists, join, abspath
from roboai_cli.commands.create_tests import get_all_languages
from roboai_cli.commands.create_tests import _inform_language
from roboai_cli.util.cli import loading_indicator, print_success, print_error
from roboai_cli.util.request_reply import TRUE_FILES_FOLDER_NAME
from roboai_cli.util.request_reply import Tests

TESTS_FOLDER_NAME = os.path.join("roboai_tests", TRUE_FILES_FOLDER_NAME)


@click.command(name="check_tests", help="Test Chatbot based on True Files")
@click.argument("languages", nargs=-1)
@click.option("--endpoint", default="http://localhost:5005", type=str, help="Request URL (Default: http://localhost:5005)")
@click.option("--headers", default={}, type=dict, help="Request headers (Default: {})")
@click.option("--true-files-path", default=None, type=str, help="Specifies the true files path")
def command(languages: tuple, endpoint: str, headers: dict, true_files_path: str):
    if true_files_path is None:
        # with loading_indicator("Checking tests..."):
        if exists(join(abspath("."), "languages")):
            _inform_language()
            list_true_files_dir = get_all_languages(path=abspath("."), languages=languages)

            while list_true_files_dir:
                true_files_dir = join(list_true_files_dir.pop(), TESTS_FOLDER_NAME)
                check_path_and_run_tests(true_files_dir, endpoint, headers)
        else:
            _inform_language()
            true_files_dir = join(abspath("."), TESTS_FOLDER_NAME)
            check_path_and_run_tests(true_files_dir, endpoint, headers)
        # end of loading

    else:
        with loading_indicator("Checking tests..."):
            check_path_and_run_tests(true_files_path, endpoint, headers)

    print_success("Tests ended successfully")


def check_path_and_run_tests(path, endpoint, headers):
    if exists(path):
        tests = Tests(
            true_files_path=path,
            endpoint=endpoint,
            headers=headers
        )
        tests.run_tests()
    else:
        print_error(f"True files path not found: {path}")
        quit()


if __name__ == "__main__":
    command()
