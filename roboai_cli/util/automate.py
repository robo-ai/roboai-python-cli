import os.path
from os.path import exists, join
from typing import List

from roboai_cli.util.cli import loading_indicator, print_success, print_error
from roboai_cli.util.parsing import start_parsing

DOMAIN_FILE_NAME = "domain.yml"


def automate(domain_path: str, paths: List[str]):

    with loading_indicator("Creating true files...\n"):

        domain_file_path = join(domain_path, DOMAIN_FILE_NAME)
        while len(paths):

            path = paths.pop()

            if os.path.isdir(path):
                paths = paths + [os.path.join(path, name) for name in os.listdir(path)]

            elif path.endswith(".yml"):

                if file_exits(domain_file_path, path):
                    start_parsing(domain_file_path, path)
                else:
                    if not exists(domain_file_path):
                        print_error(f"Domain file not found: {domain_file_path}")

                    if not exists(path):
                        print_error(f"Template file not found: {path}")

                    print_error('Unable to create all tests')
                    quit()


def file_exits(domain: str, template: str):
    return exists(domain) and exists(template)


if __name__ == "__main__":
    automate('roboai_cli/util/', ["../roboai_tests/tests_templates/"])
