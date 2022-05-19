import os
import click

from os.path import exists, join, abspath
from roboai_cli.commands.create_tests import get_all_languages
from roboai_cli.commands.create_tests import _inform_language
from roboai_cli.util.cli import loading_indicator, print_success, print_error
from roboai_cli.util.request_reply import TRUE_FILES_FOLDER_NAME
from roboai_cli.util.request_reply import Tests
from roboai_cli.util.request_reply import RESULTS_FOLDER_NAME

TESTS_FOLDER_NAME = os.path.join("roboai_tests", TRUE_FILES_FOLDER_NAME)
TESTS_RESULTS_FOLDER_NAME = os.path.join("roboai_tests", RESULTS_FOLDER_NAME)
COMMANDS_DIR = "roboai_cli"


@click.command(name="check_tests", help="Test Chatbot based on True Files")
@click.argument("languages", nargs=-1)
@click.option("--endpoint", default="http://localhost:5005", type=str,
              help="Request URL (Default: http://localhost:5005)")
@click.option("--headers", default={}, type=dict, help="Request headers (Default: {})")
@click.option("--true-files-path", default=None, type=str, help="Specifies the true files path")
@click.option("--export-all/--export-only-failed", default=False, type=bool, help="Include the tests passed on the report")
@click.option("--chatbot-version", "--v", default='Not available', type=str, help="Include the chatbot version")
def command(languages: tuple, endpoint: str, headers: dict, true_files_path: str, export_all: bool, chatbot_version: str):
    if not true_files_path:
        # with loading_indicator("Checking tests..."):
        if exists(join(abspath("."), "languages")):
            list_true_files_dir = get_all_languages(path=abspath("."), languages=languages)

            while list_true_files_dir:
                current_dir = list_true_files_dir.pop()
                results_dir = join(current_dir, TESTS_RESULTS_FOLDER_NAME)

                if not exists(results_dir):

                    create_results_dir(results_dir)

                true_files_dir = join(current_dir, TESTS_FOLDER_NAME)
                check_path_and_run_tests(true_files_dir, endpoint, headers, export_all, chatbot_version)
        else:
            current_dir = abspath(".")

            if not current_dir.endswith(COMMANDS_DIR):
                print_error("Wrong directory")

            else:
                results_dir = join(current_dir, TESTS_RESULTS_FOLDER_NAME)

                if not exists(results_dir):
                    create_results_dir(results_dir)

                true_files_dir = join(current_dir, TESTS_FOLDER_NAME)
                check_path_and_run_tests(true_files_dir, endpoint, headers, export_all, chatbot_version)
        # end of loading

    else:
        # with loading_indicator("Checking tests..."):
        dir_path_index = true_files_path.rfind('/')
        results_dir = join(true_files_path[:dir_path_index], RESULTS_FOLDER_NAME)

        check_path_and_run_tests(true_files_path, endpoint, headers, export_all, chatbot_version)

        if not exists(results_dir):
            create_results_dir(results_dir)

    print_success("Tests ended successfully")


def check_path_and_run_tests(path, endpoint, headers, passed, chatbot_version):
    """
    Checks if the true files path exists and if it does, run the tests
    Args:

        path: true files path
        endpoint: message endpoint
        headers: message headers
        passed: boolean to check which command was run (export-all or export-only-failed (default) )
        chatbot_version: version of chatbot

    """
    if exists(path):
        tests = Tests(
            true_files_path=path,
            endpoint=endpoint,
            headers=headers,
            passed=passed,
            version=chatbot_version
        )
        tests.run_tests()
    else:
        print_error(f"True files path not found: {path}")
        quit()


def create_results_dir(path):
    os.makedirs(path)


if __name__ == "__main__":
    command()
