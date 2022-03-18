import os.path
from os.path import exists, join
from typing import List

from roboai_cli.util.cli import loading_indicator, print_success, print_error
from roboai_cli.util.parsing import start_parsing

DOMAIN_FILE_NAME = "domain.yml"


def automate(domain_path: str, paths: List[str]):
    if domain_path.endswith(DOMAIN_FILE_NAME):
        domain_file_path = domain_path
    else:
        domain_file_path = join(domain_path, DOMAIN_FILE_NAME)

    while len(paths):

        path = paths.pop()

        if os.path.isdir(path):
            paths = paths + [os.path.join(path, name) for name in os.listdir(path)]

        elif path.endswith(".yml"):
            start_parsing(domain_file_path, path)


def paths_exist(domain: str, templates: list):

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


"""
def paths_not_exist(domain: str, templates: list):
    
    if not exists(domain):
        print_error(f"\nDomain path not found: {domain}")

    for template in templates
        
        
    print_error(f"\nTemplate path not found: {template}")

    print_error('Unable to create all tests')
    quit()
"""


if __name__ == "__main__":
    automate('roboai_cli/util/', ["../roboai_tests/tests_templates/"])
