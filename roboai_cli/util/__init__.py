import sys
import ruamel.yaml
import json
from input_output import load_yaml, save_yaml


def start_parsing():

    """
    Load yaml files from their current path
    """

    domain_file = load_yaml('domain.yml')
    template_file = load_yaml('template_form_iptv_support copy.yml')
    add_chatbot_reply(domain_file, template_file)


def add_chatbot_reply(domain: dict, template: dict):

    """
    Merge domain and template dictionaries creating a list (list_story_steps) containing story and steps
    Args:
        domain: domain dictionary
        template: template dictionary

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

    flatten_list(template, list_story_steps)


def flatten_list(template: dict, list_story_steps: list):
    """
    Flattens the list putting story and steps in the same dictionary

    Args:
        template: template dictionary
        list_story_steps: list containing story and steps

    """
    list_aux = []

    for i in range(0, len(list_story_steps), 2):

        dict_aux = {}
        dict_aux.update(list_story_steps[i])
        dict_aux.update(list_story_steps[i+1])
        list_aux.append(dict_aux)

    create_dict_tests(template, list_aux)


def create_dict_tests(template: dict, tests: list):

    """
    Creates true file by merging title, description and tests
    Args:
        template: template dictionary
        tests: list containing story and steps

    """
    dict_aux = {}
    dict_aux.update({'title': template.get('title')})
    dict_aux.update({'description': template.get('description')})
    dict_aux.update({'tests': tests})

    class NonAliasingRTRepresenter(ruamel.yaml.representer.RoundTripRepresenter):
        def ignore_aliases(self, data):
            return True


    yaml = ruamel.yaml.YAML()
    yaml.Representer = NonAliasingRTRepresenter
    yaml.indent(mapping=2, sequence=4, offset=2)

    


    with open('true_file.yml', "w", encoding="UTF-8") as ymlfile:
        yaml.dump(dict_aux, sys.stdout)
    with open(f'true_file.json', 'w', encoding='utf8') as outfile:
        json.dump(dict_aux, outfile, indent=2, ensure_ascii=False)
    # dump_yaml('true_file.yml', dict_aux)
    #print(dict_aux)


# def dump_yaml(path: str, yaml_dict: dict) -> None:
#     """
#     Saves a dictionary into a .yml file.
#     :param path: path where the file should be saved.
#     :param yaml_dict: dictionary to be saved.
#     """
#     with open(path, "w", encoding="UTF-8") as ymlfile:

#         print(yaml_dict)
#         yaml.dump(yaml_dict)
#         ymlfile.write("\n")


if __name__ == "__main__":
    start_parsing()


