import click
import itertools
import difflib
import sys
import os
from os.path import join

from roboai_cli.util.cli import print_info, print_success
from roboai_cli.util.input_output import load_yaml


@click.command(name="diff", help="Check for structural differences between languages for the same multi-language bot.")
@click.argument("languages", nargs=-1,)
@click.option("--path", default=".", type=click.Path(), help="Path to the root directory of your multi-language bot.")
def command(languages: tuple, path: str):
    """
    Checks for differences in bots under the same multi-lingual
    structure.
    Args:
        languages: language code of the bots to be checked.
        path (str): optional argument stating the root directory of the bot.
    """
    languages_paths = get_all_languages(path=path, languages=languages)
    comparisons_list = itertools.combinations(languages_paths, 2)
    print_info(f"Starting diff comparison for the following bots: \n{languages_paths}\n\n ***   ***   ***\n")
    for path_a, path_b in comparisons_list:
        domain_a_json = load_yaml(join(path_a, "domain.yml"))
        domain_b_json = load_yaml(join(path_b, "domain.yml"))
        print_info(f"Comparing {os.path.basename(path_a)} and {os.path.basename(path_b)} bots:\n ------")
        is_diff = diff(domain_a_json, domain_b_json)
        print_info(f" ------\nEnd of {os.path.basename(path_a)} \
                   and {os.path.basename(path_b)} bots comparison.\n *** \n")
        if not is_diff:
            print_info(f"No differences found between {os.path.basename(path_a)} \
                       and {os.path.basename(path_b)} bots.\n")
    print_success("*** Difference comparison succeded! ***")


def diff(domain_a: dict, domain_b: dict):
    def print_diff_list(first_list, second_list):
        sys.stdout.writelines(difflib.unified_diff([item + "\n" if isinstance(item, str) else list(item.keys())[0] + "\n" for item in first_list],
                                                   [item + "\n" if isinstance(item, str) else list(item.keys())[0] + "\n" for item in second_list]))

    def print_diff_keys(first_dict, second_dict):
        sys.stdout.writelines(difflib.unified_diff([key + "\n" for key in first_dict.keys()],
                                                   [key + "\n" for key in second_dict.keys()]))

    def print_diff_items(first_dict, second_dict):
        sys.stdout.writelines(difflib.unified_diff([str(item) + "\n" for item in first_dict.items()],
                                                   [str(item) + "\n" for item in second_dict.items()]))

    # --- all comparisons are explicit to enable future exception handeling if needed --- #
    # Compare the intents:
    domain_diff_q = False
    if domain_a.get("intents", None) != domain_b.get("intents", None):
        domain_diff_q = True
        print_info(" -- The intents differ by:")
        print_diff_list(domain_a.get("intents", []), domain_b.get("intents", []))
    # Compare the actions:
    if domain_a.get("actions", None) != domain_b.get("actions", None):
        domain_diff_q = True
        print_info(" -- The actions differ by:")
        print_diff_list(domain_a.get("actions", []), domain_b.get("actions", []))
    # Compare the forms:
    if domain_a.get("forms", None) != domain_b.get("forms", None):
        domain_diff_q = True
        print_info(" -- The forms differ by:")
        print_diff_list(domain_a.get("forms", []), domain_b.get("forms", []))
    # Compare the entities:
    if domain_a.get("entities", None) != domain_b.get("entities", None):
        domain_diff_q = True
        print_info(" -- The entities differ by:")
        print_diff_list(domain_a.get("entities", []), domain_b.get("entities", []))
    # Compare the slots
    if domain_a.get("slots", None) != domain_b.get("slots", None):
        domain_diff_q = True
        print_info(" -- The slots differ by:")
        print_diff_keys(domain_a["slots"], domain_b["slots"])
    # Compare the responses
    if domain_a.get("responses", None) != domain_b.get("responses", None):
        domain_diff_q = True
        print_info(" -- The responses differ by:")
        print_diff_keys(domain_a["responses"], domain_b["responses"])
    # Compare session config
    if domain_a.get("session_config", None) != domain_b.get("session_config", None):
        domain_diff_q = True
        print_info(" -- The session_config differ by:")
        print_diff_items(domain_a["session_config"], domain_b["session_config"])

    return domain_diff_q


def get_all_languages(path: str, languages: tuple):
    if len(languages) == 0:
        print_info("No language was provided. Will identify differences for \
                   all available language pairs inside provided bot folder.")
        languages_paths = [join(path, "languages", folder) for folder in os.listdir(join(path, "languages"))
                           if os.path.isdir(os.path.join(path, "languages", folder))]
    elif len(languages) == 1:
        print_info("Unable to provide differences: at least two languages must be provided.")
        exit(0)
    else:
        languages_paths = [join(path, "languages", folder) for folder in os.listdir(join(path, "languages"))
                           if os.path.isdir(os.path.join(path, "languages", folder)) and folder in languages]
    return languages_paths


if __name__ == "__main__":
    command()
