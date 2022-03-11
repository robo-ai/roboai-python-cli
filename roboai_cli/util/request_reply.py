import json
import os
import uuid
import requests

from roboai_cli.util.input_output import load_yaml
from deepdiff import DeepDiff

ENDPOINT = "http://rasa-training.development.robo-ai.com:5006"
REST_PATH = "/webhooks/rest/webhook"
REST_METHOD = "post"
META_DATA_PATH = "/status"
META_DATA_METHOD = "get"
TRACKER_PATH = "/conversations/{}/tracker?include_events=ALL"
TRACKER_METHOD = "get"
TRUE_FILES_FOLDER_NAME = "tests_true_files"


class Tests:

    def __init__(
            self,
            endpoint: str,
            headers: dict,
            true_files_path: str
    ) -> None:
        self.__true_files_list = [true_files_path]
        self.__message = Message(endpoint=endpoint, headers=headers)

    def run_tests(self):
        print(self.__message.request_message(META_DATA_PATH, META_DATA_METHOD, body={}))
        self.get_all_true_files(self.__true_files_list)

    def get_all_true_files(self, paths):
        while len(paths):

            path = paths.pop()
            print(path)
            if os.path.isdir(path):
                paths = paths + [os.path.join(path, name) for name in os.listdir(path)]

            elif path.endswith(".yml"):
                self.get_all_stories(load_yaml(path))

    def get_all_stories(self, true_file):
        list_stories_steps = true_file.get('tests')

        for dict_story_steps in list_stories_steps:
            id_story = generate_id_story()
            list_chatbot_reply = []
            print(dict_story_steps['story'])
            print(id_story)

            try:
                for dict_steps in dict_story_steps['steps']:
                    for dict_steps_key, dict_steps_value in dict_steps.items():

                        if dict_steps_key == "user":
                            if list_chatbot_reply:
                                raise Exception(f'The reply was not evaluated: {list_chatbot_reply}')

                            list_chatbot_reply = self.__message.request_message(REST_PATH, REST_METHOD, body={
                                "sender": id_story,
                                "message": dict_steps_value
                            })

                        elif dict_steps_key == "chatbot":
                            if not list_chatbot_reply:
                                raise Exception('Chatbot did not reply (the list is empty)')

                            list_chatbot_reply = self.evaluate(list_chatbot_reply, dict_steps_value)

            except Exception as e:
                print(e)
                print(self.__message.request_message(TRACKER_PATH.format(id_story), TRACKER_METHOD, body={}))
                pass

    def evaluate(self, list_chatbot_reply, dict_steps_value):
        answers_list = list(dict_steps_value.values())[0]
        chatbot_reply = list_chatbot_reply.pop(0)

        for custom_answers in answers_list:
            if not DeepDiff(custom_answers['custom'], chatbot_reply['custom']):
                return list_chatbot_reply

        raise Exception(f"Could not find {chatbot_reply['custom']} on the list {answers_list}")


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


if __name__ == "__main__":
    tests = Tests(
        true_files_path="../roboai_tests/tests_true_files/",
        endpoint=ENDPOINT,
        headers={}
    )

    tests.run_tests()
