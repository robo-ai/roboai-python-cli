import os
import json
from typing import List

MANIFEST_FILE = "robo-manifest.json"
BOT_ID_SETTING = "bot_id"
BOT_RUNTIME_BASE_VERSION_SETTING = "base_version"
EXCLUSIONS_SETTING = "exclusions"
DEFAULT_RUNTIME_BASE_VERSION = "rasa-1.10.0"

DEFAULT_MANIFEST = {
    BOT_ID_SETTING: None,
    BOT_RUNTIME_BASE_VERSION_SETTING: DEFAULT_RUNTIME_BASE_VERSION,
    # EXCLUSIONS_SETTING: [
    #     "__pycache__",
    #     "*.py[cod]",
    #     "*$py.class",
    #     "*.so",
    #     ".*",
    #     "eggs",
    #     "*.egg-info",
    #     "venv",
    #     "virtualenv",
    #     "build",
    # ]
}


class BotManifest:
    __path: str

    def __init__(self, path: str = None):
        self.__path = os.getcwd() if not path else path

    def get_bot_id(self):
        return self.__get_setting_value(BOT_ID_SETTING)

    def set_bot_id(self, bot_id):
        self.__update_setting_value(BOT_ID_SETTING, bot_id)

    def get_exclusions(self) -> List[str]:
        return self.__get_setting_value(EXCLUSIONS_SETTING)

    def set_exclusions(self, exclusions: List[str]):
        self.__update_setting_value(EXCLUSIONS_SETTING, exclusions)

    def get_base_version(self) -> List[str]:
        return self.__get_setting_value(BOT_RUNTIME_BASE_VERSION_SETTING)

    def set_base_version(self, version: str):
        self.__update_setting_value(BOT_RUNTIME_BASE_VERSION_SETTING, version)

    def __get_setting_value(self, key):
        settings = self.__load_settings()
        if key in settings:
            return settings[key]
        return None

    def __update_setting_value(self, key, value):
        settings = self.__load_settings()
        settings[key] = value
        self.__save_settings(settings)

    def __load_settings(self):
        manifest_path = self.__get_manifest_path()
        if not os.path.exists(manifest_path):
            return DEFAULT_MANIFEST

        with open(manifest_path) as file:
            return json.load(file)

    def __save_settings(self, settings):
        manifest_path = self.__get_manifest_path()
        with open(manifest_path, "w") as file:
            json.dump(settings, file, indent=4, sort_keys=True)

    def __get_manifest_path(self):
        return self.__path + os.path.sep + MANIFEST_FILE
