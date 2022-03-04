import json
import uuid
import requests


class Message:

    def __init__(
            self,
            endpoint: str,
            path: str,
            method: str,
            headers: dict,
            body: dict,
    ) -> None:
        self.__endpoint = endpoint
        self.__path = path
        self.__method = method
        self.__headers = headers
        self.__body = body

    def request_message(self) -> dict:

        reply_info = None
        reply_info_dict = {}

        if self.__method == "get":
            reply_info = requests.get(url=f"{self.__endpoint}{self.__path}", headers=self.__headers,
                                      data=json.dumps(self.__body))
        elif self.__method == "post":
            reply_info = requests.post(url=f"{self.__endpoint}{self.__path}", headers=self.__headers,
                                       data=json.dumps(self.__body))

        if reply_info.status_code == 200:
            reply_info_dict = reply_info.json()

        return reply_info_dict

    def set_endpoint(self, endpoint):
        self.__endpoint = endpoint

    def get_endpoint(self):
        return self.__endpoint

    def set_path(self, path):
        self.__path = path

    def get_path(self):
        return self.__path

    def set_method(self, method):
        self.__method = method

    def get_method(self):
        return self.__method

    def set_headers(self, headers_dict):
        self.__headers = headers_dict

    def set_headers_key(self, key, value):
        self.__headers[key] = value

    def get_headers(self):
        return self.__headers

    def get_headers_key(self, key):
        if key in self.__headers:
            return self.__headers[key]

    def set_body(self, body_dict):
        self.__body = body_dict

    def set_body_key(self, key, value):
        self.__body[key] = value

    def get_body(self):
        return self.__body

    def get_body_key(self, key):
        if key in self.__body:
            return self.__body[key]


def generate_id_conversation():
    return uuid.uuid4().hex


if __name__ == "__main__":

    sender = generate_id_conversation()
    conversation = Message(
        endpoint="http://rasa-training.development.robo-ai.com:5006",
        path="/webhooks/rest/webhook",
        method="post",
        headers={},
        body={
            "sender": sender,
            "message": "/start-dialogue"
        }
    )

    print(conversation.request_message())





