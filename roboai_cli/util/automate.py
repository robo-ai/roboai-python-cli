import os.path
from parsing import start_parsing


def automate(paths: list[str]):

    while len(paths):

        path = paths.pop()

        if os.path.isdir(path):
            paths = paths + [os.path.join(path, name) for name in os.listdir(path)]
        elif path.endswith(".yml"):
            start_parsing(path)


if __name__ == "__main__":
    automate(["../roboai_tests/tests_templates/"])
