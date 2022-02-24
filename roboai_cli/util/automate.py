import os.path
from typing import List

from roboai_cli.util.parsing import start_parsing


def automate(domain_path: str, paths: List[str]):

    while len(paths):

        path = paths.pop()

        if os.path.isdir(path):
            paths = paths + [os.path.join(path, name) for name in os.listdir(path)]
        elif path.endswith(".yml"):
            start_parsing(domain_path, path)


if __name__ == "__main__":
    automate(["../roboai_tests/tests_templates/"])
