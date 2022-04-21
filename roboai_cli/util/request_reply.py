import json
import os
import uuid
import pkg_resources
import requests

from distutils.dir_util import copy_tree
from os.path import join, exists
from datetime import datetime
from roboai_cli.util.input_output import load_yaml
from deepdiff import DeepDiff
from roboai_cli.util.cli import print_success, print_error
from jinja2 import FileSystemLoader, Environment

ENDPOINT = "http://rasa-training.development.robo-ai.com:5006"
REST_PATH = "/webhooks/rest/webhook"
REST_METHOD = "post"
META_DATA_PATH = "/status"
META_DATA_METHOD = "get"
TRACKER_PATH = "/conversations/{}/tracker?include_events=ALL"
TRACKER_METHOD = "get"
TRUE_FILES_FOLDER_NAME = "tests_true_files"
RESULTS_FOLDER_NAME = "tests_results"


class Tests:

    def __init__(
            self,
            endpoint: str,
            headers: dict,
            true_files_path: str,
            passed: bool
    ) -> None:
        self.__true_files_path = true_files_path
        self.__true_files_list = [true_files_path]
        self.__message = Message(endpoint=endpoint, headers=headers)
        self.__report_folder_path = None
        self.__successful = 0
        self.__successful_input = 0
        self.__failed = 0
        self.__failed_input = 0
        self.__time = get_time()
        self.__tests_failed = []
        self.__tests_passed = []
        self.__data = []
        self.__passed = passed

    def run_tests(self):
        meta_data_dict = self.__message.request_message(META_DATA_PATH, META_DATA_METHOD, body={})
        print(json.dumps(meta_data_dict, sort_keys=True, indent=4))
        self.__report_folder_path = create_folder_report(self.__true_files_path, self.__time)
        self.create_json_file(self.__report_folder_path, "fingerprint", meta_data_dict)
        self.get_all_true_files(self.__true_files_list)
        self.create_html_file(self.__report_folder_path)
        print_success("Tests ended successfully\n")
        print("Tests results:\n")
        print(f"Number of tests: {self.__successful + self.__failed}")
        print_success(f"Successful: {self.__successful}")
        print_error(f"Failed: {self.__failed}")
        print(f"\nNumber of test inputs: {self.__successful_input + self.__failed_input}")
        print_success(f"Successful: {self.__successful_input}")
        print_error(f"Failed: {self.__failed_input}\n")

        if self.__tests_failed:

            print("Tests failed:")
            for test in self.__tests_failed:
                print(f"- {test}")

    def get_all_true_files(self, paths):

        while len(paths):
            path = paths.pop()

            if os.path.isdir(path):
                paths = paths + [os.path.join(path, name) for name in os.listdir(path)]

            elif path.endswith(".yml"):
                self.get_all_stories(path)

    def get_all_stories(self, path):
        true_file = load_yaml(path)
        yml_file = trimming_yml_file(path)
        list_stories_steps = true_file.get('tests')
        true_file_title = true_file.get('title')
        copy_assets(self.__report_folder_path)

        for dict_story_steps in list_stories_steps:
            id_story = generate_id_story()
            list_chatbot_reply = []
            story_name = dict_story_steps['story']
            story_running = f"{yml_file}: {story_name}"
            steps_running = dict_story_steps['steps']
            tracker_response = {}

            print(f"\nRunning {story_running}")
            print(f"With Conversation-UUID: {id_story}\n")

            if self.__passed:
                tracker_response = self.__message.request_message(TRACKER_PATH.format(id_story), TRACKER_METHOD,
                                                                  body={})
                json_folder = join(self.__report_folder_path, "trackers")
                self.create_json_file(json_folder, id_story, tracker_response)

            try:
                for dict_steps in steps_running:
                    for dict_steps_key, dict_steps_value in dict_steps.items():

                        if dict_steps_key == "user":
                            if list_chatbot_reply:
                                raise Exception('Unexpected chatbot utter:\n'
                                                f'{json.dumps(list_chatbot_reply, sort_keys=True, indent=4)}')

                            list_chatbot_reply = self.__message.request_message(REST_PATH, REST_METHOD, body={
                                "sender": id_story,
                                "message": dict_steps_value
                            })

                        elif dict_steps_key == "chatbot":
                            if not list_chatbot_reply:
                                raise Exception('No chatbot utter.\n'
                                                'Expected chatbot utter:\n'
                                                f'{dict_steps_value}')

                            list_chatbot_reply = self.evaluate(list_chatbot_reply, dict_steps_value)
                            self.__successful_input += 1

                data = {
                    'story_id': id_story,
                    'story_name': true_file_title + ": " + story_name,
                    'steps': steps_running,
                    'status': 'Passed',
                    'tracker': tracker_response
                }

                self.__successful += 1
                self.__data.append(data)

            except Exception as e:
                self.__failed_input += 1
                self.__failed += 1
                self.__tests_failed.append(story_running)

                tracker_response = self.__message.request_message(TRACKER_PATH.format(id_story), TRACKER_METHOD,
                                                                  body={})

                if not self.__passed:

                    json_folder = join(self.__report_folder_path, "trackers")
                    self.create_json_file(json_folder, id_story, tracker_response)

                data = {
                    'story_id': id_story,
                    'story_name': true_file_title + ": " + story_name,
                    'steps': steps_running,
                    'status': 'Failed',
                    'tracker': tracker_response
                }

                self.__data.append(data)

                print(e)

                pass

    def evaluate(self, list_chatbot_reply, dict_steps_value):
        answers_list = list(dict_steps_value.values())[0]
        chatbot_reply = list_chatbot_reply.pop(0)

        for custom_answers in answers_list:
            if not DeepDiff(custom_answers['custom'], chatbot_reply['custom']):
                return list_chatbot_reply

        raise Exception("Expected utter:\n"
                        f"{json.dumps(answers_list, sort_keys=True, indent=4)}\n\n"
                        "Chatbot utter:\n"
                        f"{json.dumps(chatbot_reply['custom'], sort_keys=True, indent=4)}")

    def create_html_file(self, report_folder_path: str):
        loader = FileSystemLoader('util')
        env = Environment(loader=loader)
        template = env.get_template('report_draft.html')

        file_dir = join(report_folder_path, "report.html")

        with open(file_dir, "w") as htmlfile:
            render = template.render({'results': self.get_results(),
                                      'data': self.__data,
                                      'passed': self.__passed})
            htmlfile.write(render)
            htmlfile.close()

    def get_results(self):
        results = {
            'number_tests': self.__successful + self.__failed,
            'number_tests_successful': self.__successful,
            'number_tests_failed': self.__failed,
            'number_tests_inputs': self.__successful_input + self.__failed_input,
            'number_tests_inputs_successful': self.__successful_input,
            'number_tests_inputs_failed': self.__failed_input
        }

        return results

    def create_json_file(self, path: str, filename: str, content: dict):

        if not exists(path):
            os.makedirs(path)

        file_dir = join(path, filename) + ".json"
        json_object = json.dumps(content, sort_keys=True, indent=4)

        with open(file_dir, "w") as jsonfile:
            jsonfile.write(json_object)


class Message:

    def __init__(
            self,
            endpoint: str,
            headers: dict,
    ) -> None:
        self.__endpoint = endpoint
        self.__headers = headers

    def request_message(self, path: str, method: str, body: dict) -> dict:

        reply_info = None
        reply_info_dict = {}

        if method == "get":
            reply_info = requests.get(url=f"{self.__endpoint}{path}", headers=self.__headers,
                                      data=json.dumps(body))
        elif method == "post":
            reply_info = requests.post(url=f"{self.__endpoint}{path}", headers=self.__headers,
                                       data=json.dumps(body))

        if reply_info.status_code == 200:
            reply_info_dict = reply_info.json()

        return reply_info_dict


def generate_id_story():
    return uuid.uuid4().hex


def get_time():
    now = datetime.now()
    time_string = now.strftime("%d%m%Y-%H%M%S")
    return time_string


def create_folder_report(path: str, folder: str):
    true_files_path_index = path.find(TRUE_FILES_FOLDER_NAME)
    folder_dir = join(path[:true_files_path_index], RESULTS_FOLDER_NAME, folder)

    if not exists(folder_dir):
        os.makedirs(folder_dir)

    return folder_dir


def copy_assets(path: str):

    from_directory = assets_path()
    to_directory = join(path, "assets")

    copy_tree(from_directory, to_directory)


def trimming_yml_file(path: str):
    yml_file_index = path.rfind('/')
    yml_file = path[yml_file_index:]
    yml_file = yml_file.replace("/", "")
    return yml_file


def assets_path() -> str:
    return pkg_resources.resource_filename(__name__, "assets")


if __name__ == "__main__":
    tests = Tests(
        true_files_path="../roboai_tests/tests_true_files/",
        endpoint=ENDPOINT,
        headers={},
        passed=False
    )

    tests.run_tests()
