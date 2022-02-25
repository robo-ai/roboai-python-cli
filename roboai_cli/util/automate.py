import os.path
from os.path import exists, join
from typing import List

from roboai_cli.util.cli import loading_indicator, print_success, print_error
from roboai_cli.util.parsing import start_parsing

DOMAIN_FILE_NAME = "domain.yml"


def automate(domain_path: str, paths: List[str]):
    domain_file_path = join(domain_path, DOMAIN_FILE_NAME)
    while len(paths):

        path = paths.pop()

        if os.path.isdir(path):
            paths = paths + [os.path.join(path, name) for name in os.listdir(path)]

        elif path.endswith(".yml"):

            if paths_exist(domain_file_path, path):
                start_parsing(domain_file_path, path)
            else:
                paths_not_exist(domain_file_path, path)


def paths_exist(domain: str, template: str):
    return exists(domain) and exists(template)


def paths_not_exist(domain: str, template: str):
    if not exists(domain) and not exists(template):
        print_error(f"\nDomain path not found: {domain}")
        print_error(f"Template path not found: {template}")

    elif not exists(domain):
        print_error(f"\nDomain path not found: {domain}")

    elif not exists(template):
        print_error(f"\nTemplate path not found: {template}")

    print_error('Unable to create all tests')
    quit()


if __name__ == "__main__":
    automate('roboai_cli/util/', ["../roboai_tests/tests_templates/"])
