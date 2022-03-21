import json
import os
import uuid
import requests

from os.path import join, exists
from datetime import datetime
from roboai_cli.util.input_output import load_yaml
from deepdiff import DeepDiff
from roboai_cli.util.cli import print_success, print_error

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
            true_files_path: str
    ) -> None:
        self.__true_files_list = [true_files_path]
        self.__message = Message(endpoint=endpoint, headers=headers)
        self.__successful = 0
        self.__successful_input = 0
        self.__failed = 0
        self.__failed_input = 0
        self.__time = get_time()
        self.__tests_failed = []

    def run_tests(self):
        meta_data_dict = self.__message.request_message(META_DATA_PATH, META_DATA_METHOD, body={})
        print(json.dumps(meta_data_dict, sort_keys=True, indent=4))
        self.get_all_true_files(self.__true_files_list)
        print_success("Tests ended successfully\n")
        print("Tests results:\n")
        print(f"Number of tests: {self.__successful + self.__failed}")
        print_success(f"Successful: {self.__successful}")
        print_error(f"Failed: {self.__failed}")
        print(f"\nNumber of test inputs: {self.__successful_input + self.__failed}")
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

        for dict_story_steps in list_stories_steps:
            id_story = generate_id_story()
            list_chatbot_reply = []
            story_name = dict_story_steps['story']
            story_running = f"{yml_file}: {story_name}"
            print(f"\nRunning {story_running}")
            print(f"With Conversation-UUID: {id_story}\n")

            try:
                for dict_steps in dict_story_steps['steps']:
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

                self.__successful += 1

            except Exception as e:
                self.__failed_input += 1
                self.__failed += 1
                self.__tests_failed.append(story_running)
                print(e)
                create_json_file(path, id_story,
                                 self.__message.request_message(TRACKER_PATH.format(id_story), TRACKER_METHOD, body={}),
                                 self.__time)
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


def create_json_file(path: str, id_story: str, content: dict, folder: str):

    true_files_path_index = path.find(TRUE_FILES_FOLDER_NAME)
    folder_dir = join(path[:true_files_path_index], RESULTS_FOLDER_NAME, folder)

    if not exists(folder_dir):
        os.makedirs(folder_dir)

    file_dir = join(folder_dir, id_story) + ".json"
    json_object = json.dumps(content, sort_keys=True, indent=4)

    with open(file_dir, "w") as jsonfile:
        jsonfile.write(json_object)


def trimming_yml_file(path: str):

    yml_file_index = path.rfind('/')
    yml_file = path[yml_file_index:]
    yml_file = yml_file.replace("/", "")
    return yml_file


if __name__ == "__main__":
    tests = Tests(
        true_files_path="../roboai_tests/tests_true_files/",
        endpoint=ENDPOINT,
        headers={}
    )

    tests.run_tests()
