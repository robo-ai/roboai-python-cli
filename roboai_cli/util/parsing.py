import yaml
import os.path

from os.path import exists, join
from typing import List
from roboai_cli.util.cli import print_error
from roboai_cli.util.input_output import load_yaml

TEMPLATES_FOLDER_NAME = "tests_templates"
TRUE_FILES_FOLDER_NAME = "tests_true_files"

DOMAIN_FILE_NAME = "domain.yml"


def create_true_files(domain_path: str, paths: List[str]):
    """

    Args:
        domain_path: domain path
        paths: list of templates

    Returns:

    """
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


def start_parsing(domain_path: str, template_path: str):
    """
    Load yaml files from their current path and create final path
    """

    add_to_true_file_filename = '_true_file'
    true_file_path = ''

    if add_to_true_file_filename not in template_path:
        index_yaml = template_path.find('.yml')
        true_file_path = template_path[:index_yaml] + '_true_file' + template_path[index_yaml:]

    true_file_path = true_file_path.replace(TEMPLATES_FOLDER_NAME, TRUE_FILES_FOLDER_NAME)
    create_true_file_folder(true_file_path)

    domain_file = load_yaml(domain_path)
    template_file = load_yaml(template_path)
    add_chatbot_reply(domain_file, template_file, template_path, true_file_path)


def create_true_file_folder(true_file_path: str):
    """
    Verifies if the path exists and if not creates a new path
    Args:
        true_file_path: true file path
    """

    dir_path_index = true_file_path.rfind('/')
    dir_true_file_path = true_file_path[:dir_path_index]

    if not exists(dir_true_file_path):
        os.makedirs(dir_true_file_path)


def add_chatbot_reply(domain: dict, template: dict, template_path: str, true_file_path: str):
    """
    Merge domain and template dictionaries creating a list (list_story_steps) containing story and steps
    Args:
        template_path: template path
        domain: domain dictionary
        template: template dictionary
        true_file_path: true file path

    """

    if check_file(template, template_path, 'title') and check_file(template, template_path, 'description')\
            and check_file(template, template_path, 'tests'):

        list_tests = template.get('tests')
        list_story_steps = []
        list_steps = []
        error_detected = False
        flag_first = True
        story_name = None
        last = None

        for dic in list_tests:
            if check_file(dic, template_path, 'story') and check_file(dic, template_path, 'steps')\
                    and not error_detected:

                for item_key, item_value in dic.items():

                    if item_key == 'story' and not error_detected:
                        list_story_steps.append({item_key: item_value})
                        story_name = item_value

                    elif item_key == 'steps' and not error_detected:
                        for dict_values in item_value:

                            if 'user' in dict_values:
                                flag_first = False

                                if check_steps(dict_values, template_path, story_name, 'user'):

                                    if last is 'utter' or last is None:

                                        list_steps.append(dict_values)

                                    elif last is 'user':

                                        index = template_path.find(TEMPLATES_FOLDER_NAME)
                                        print_error(f"\nFile:{template_path[index:]}\n"
                                                    f"There are two users in a row in story {story_name}\n")
                                        error_detected = True

                                last = 'user'

                            elif 'utter' in dict_values:

                                if check_steps(dict_values, template_path, story_name, 'utter'):
                                    if not flag_first:
                                        if utter_id_exists(domain['responses'], dict_values.get('utter')):

                                            list_steps.append(
                                                {'chatbot': {dict_values.get('utter'): domain['responses'].get(dict_values.get('utter'))}})
                                        else:

                                            index = template_path.find(TEMPLATES_FOLDER_NAME)
                                            print_error(f"\nFile:{template_path[index:]}\n"
                                                        f"utter_id ({dict_values.get('utter')}) does not exists. "
                                                        f"Story {story_name}\n")
                                            error_detected = True

                                    if flag_first:

                                        index = template_path.find(TEMPLATES_FOLDER_NAME)
                                        print_error(f"\nFile:{template_path[index:]}\n"
                                                    f"The first step of the story {story_name} is not user\n")
                                        error_detected = True
                                last = "utter"

                        list_story_steps.append({'steps': list_steps})
                        list_steps = []
                        flag_first = True

        if not error_detected:
            flatten_list(template, list_story_steps, true_file_path)


def check_file(dictionary: dict, template_path: str, component: str):
    if component not in dictionary:
        index = template_path.find(TEMPLATES_FOLDER_NAME)
        print_error(f'\nFile:{template_path[index:]}\n'
                    f'ERROR: {component} not detected\n')
        return False
    if dictionary.get(component) is None:
        index = template_path.find(TEMPLATES_FOLDER_NAME)
        print_error(f'\nFile:{template_path[index:]}\n'
                    f'ERROR: {component} dictionary is empty\n')
        return False

    return True


def check_steps(dictionary: dict, template_path: str, story_name: str, component):

    index = template_path.find(TEMPLATES_FOLDER_NAME)

    if dictionary.get(component) is None:
        print_error(f'\nFile:{template_path[index:]}\n'
                    f'{component} is empty in story {story_name}\n')
        return False

    if type(dictionary.get(component)) == str:

        if component == "user":
            file_index = template_path.rfind("/")

            if dictionary.get(component).startswith("/") and template_path[file_index:] != "/defaults.yml":
                print_error(f'\nFile:{template_path[index:]}\n'
                            f'{component} starts with / in story {story_name}\n')
                return False

            elif dictionary.get(component).startswith("utter_"):
                print_error(f'\nFile:{template_path[index:]}\n'
                            f'{component} starts with utter_ in {story_name}\n')
                return False

        elif component == "utter":
            if not dictionary.get(component).startswith("utter_"):
                print_error(f'\nFile:{template_path[index:]}\n'
                            f'{component} does not starts with utter_ in {story_name}\n')
                return False
    else:
        print_error(f'\nFile:{template_path[index:]}\n'
                    f'{component} type in {story_name} is not a string\n')
        return False

    return True


def utter_id_exists(domain_dic: dict, utter_id: str):
    """
    Checks if utter id exist in domain file
    Args:
        domain_dic: domain dictionary
        utter_id: utter id that will be tested

    """
    if utter_id in domain_dic.keys():
        return True
    return False


def flatten_list(template: dict, list_story_steps: list, true_file_path: str):
    """
    Flattens the list putting story and steps in the same dictionary

    Args:
        template: template dictionary
        list_story_steps: list containing story and steps
        true_file_path: true file path

    """
    list_aux = []

    for i in range(0, len(list_story_steps), 2):
        dict_aux = {}
        dict_aux.update(list_story_steps[i])
        dict_aux.update(list_story_steps[i + 1])
        list_aux.append(dict_aux)

    add_header(template, list_aux, true_file_path)


def add_header(template: dict, tests: list, true_file_path: str):
    """
    Merge title, description and tests
    Args:
        template: template dictionary
        tests: list containing story and steps
        true_file_path: true file path

    """
    dict_aux = {}
    dict_aux.update({'title': template.get('title')})
    dict_aux.update({'description': template.get('description')})
    dict_aux.update({'tests': tests})
    yaml_dump(true_file_path, dict_aux)


def yaml_dump(path: str, dict_data: dict):
    """
    Dumps yaml file
    Args:
        path: Path where the file will be dumped
        dict_data: dictionary that contains all the data

    """

    class NoAliasDumper(yaml.SafeDumper):
        def ignore_aliases(self, data):
            return True

    with open(path, "w", encoding="UTF-8") as ymlfile:
        yaml.dump(dict_data, ymlfile, Dumper=NoAliasDumper, allow_unicode=True, sort_keys=False)


if __name__ == "__main__":
    start_parsing('../roboai-python-cli/roboai_cli/util',
                  '../roboai_tests/tests_templates/template_form_iptv_support.yml')

    # To test : '../roboai_tests/tests_templates/template_form_iptv_support.yml'
