
from requests import get, post
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher


class ParlaiAPI:
    def create_world(self):
        url = "http://158.177.139.34:8081/create_world"
        world_id = get(url=url).json()["world_id"]
        return world_id

    def world_exists(self, world_id):
        url = f"http://158.177.139.34:8081/world_exists/{world_id}"
        return get(url=url).json()["world_exists"]

    def generate_chitchat(self, world_id, user_message):
        url = "http://158.177.139.34:8081/generate_chitchat"
        user_message_json = {"world_id": world_id, "user_message": user_message}
        return_message = post(url=url, json=user_message_json).json()["chitchat_message"]
        print(return_message)
        return return_message


class ActionParlaiFallback(Action):
    def name(self):
        return "action_parlai_fallback"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        parlai_api = ParlaiAPI()
        if tracker.get_slot("parlai_world_created"):
            world_id = tracker.get_slot("parlai_world")
            if not parlai_api.world_exists(world_id):
                print("PARLAI world doesn't exist yet. Creating world...")
                world_id = parlai_api.create_world()
                print("World created. The ID is {}".format(world_id))
            else:
                print("PARLAI world is already created. The ID is {}".format(world_id))
        else:
            print("PARLAI world doesn't exist yet. Creating world...")
            world_id = parlai_api.create_world()
            print("World created. The ID is {}".format(world_id))
        print("user message: {}, type: {}".format(tracker.latest_message["text"], type(tracker.latest_message["text"])))
        return_message = parlai_api.generate_chitchat(world_id, tracker.latest_message["text"])
        json_response = {"answers": [{"ssml": "<speak> " + return_message + " </speak>", "type": "ssml"},
                                     {"text": return_message, "type": "text"}]}
        dispatcher.utter_message(json_message=json_response)
        return [
            SlotSet("parlai_world_created", True),
            SlotSet("parlai_world", world_id)
        ]
