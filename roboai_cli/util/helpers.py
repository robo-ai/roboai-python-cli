from os.path import join
import subprocess
import sys

import click

from roboai_cli.util.cli import print_info


def get_index(lista: list, value: str) -> int:
    """
    Get the list index of a given value if it exists.

    Args:
        lista (list): list to get the index from
        value (str): value to search in the list

    Returns:
        i: index of the value in the list
    """
    i = 0
    length = len(lista)
    while i < length and lista[i]["name"] != value:
        i = i + 1
    if i == length:
        raise("value not found")
    else:
        return i


def clean_intents(intents: list) -> list:
    """
    Some intents may trigger actions which means they will be dict instead of strings.
    This method parses those dicts and returns the list of intents.

    Args:
        intents (list): list of intents taken from the domain
    Example: [{"start_dialogue": {"triggers": "action_check_Bot_Introduced"}}, "greeting", ]

    Returns:
        list: list of intents without dicts
    Example: ["start_dialogue", "greeting", ]
    """

    for i, intent in enumerate(intents):
        if isinstance(intent, dict):
            intents[i] = list(intent.keys())[0]

    return intents


def user_proceed(message: str):
    return click.confirm(message)


def check_installed_packages(path: str) -> bool:
    """
    Check for installed packages.
    The caveat of this method is that for instance, packages installed from a git repo may not match the ones in the requirements file.
    The user is asked if they want to continue with the process or double check their packages.

    Args:
        path (str): bot root dir

    Returns:
        bool: flag indicating whether process should continue or not
    """
    try:
        with open(join(path, "requirements.txt"), "r") as f:
            bot_requirements = f.readlines()
        print_info("Checking if packages in requirements.txt are installed.")
    except Exception:
        return True

    bot_requirements = [r.split("==")[0] for r in bot_requirements]

    reqs = subprocess.check_output([sys.executable, "-m", "pip", "freeze"])
    installed_packages = [r.decode().split("==")[0] for r in reqs.split()]

    if all(item in installed_packages for item in bot_requirements):
        return True
    else:
        missing_packages = [item for item in bot_requirements if item not in installed_packages]
        print("Couldn't find the following packages: \n")
        print(*missing_packages, sep="\n")
        print("This might be because it's a package installed from a git repo and it doesn't match the requirements.")
        return user_proceed("Do you want to proceed?\n")
