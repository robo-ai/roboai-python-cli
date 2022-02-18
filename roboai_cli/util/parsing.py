import yaml
import os.path

from input_output import load_yaml


def start_parsing(template_path: str):

    """
    Load yaml files from their current path and create final path
    """

    index_yaml = template_path.find('.yml')
    true_file_path = template_path[:index_yaml] + '_true_file' + template_path[index_yaml:]
    true_file_path = true_file_path.replace("tests_templates", "tests_true_files")
    path_exists(true_file_path)

    domain_file = load_yaml('domain.yml')
    template_file = load_yaml(template_path)
    add_chatbot_reply(domain_file, template_file, true_file_path)


def path_exists(true_file_path: str):
    """
    Verifies if the path exists and if not creates a new path
    Args:
        true_file_path: true file path
    """

    dir_path_index = true_file_path.rfind('/')
    dir_true_file_path = true_file_path[:dir_path_index]
    exists = os.path.exists(dir_true_file_path)

    if not exists:

        os.makedirs(dir_true_file_path)


def add_chatbot_reply(domain: dict, template: dict, true_file_path: str):

    """
    Merge domain and template dictionaries creating a list (list_story_steps) containing story and steps
    Args:
        domain: domain dictionary
        template: template dictionary
        true_file_path: true file path

    """

    list_tests = template.get('tests')
    list_story_steps = []
    list_steps = []

    for dic in list_tests:
        for item_key, item_value in dic.items():

            if item_key == 'story':
                list_story_steps.append({item_key: item_value})

            elif item_key == 'steps':
                for dict_values in item_value:

                    if 'user' in dict_values:
                        list_steps.append(dict_values)

                    elif 'utter' in dict_values:
                        list_steps.append({'chatbot': {dict_values.get('utter'): domain['responses'].get(dict_values.get('utter'))}})

                list_story_steps.append({'steps': list_steps})

    flatten_list(template, list_story_steps, true_file_path)


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
        dict_aux.update(list_story_steps[i+1])
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
    start_parsing('../roboai_tests/tests_templates/template_form_iptv_support.yml')

    #To test : '../roboai_tests/tests_templates/template_form_iptv_support.yml'


