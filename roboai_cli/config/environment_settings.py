from .environment_constants import API_KEY_SETTING, API_ENDPOINT_SETTING, API_AUTH_TOKEN_SETTING


class EnvironmentAuth:
    # __username: str = None
    # __password: str = None

    def __init__(self, username: str, password: str):
        self.__username = username
        self.__password = password

    @property
    def username(self) -> str:
        return self.__username

    @property
    def password(self) -> str:
        return self.__password


class Environment:
    # __environment_name: str = None
    # __api_key: str = None
    # __api_auth_token: str = None
    # __base_url: str = None
    # __api_auth_setting: EnvironmentAuth = None

    def __init__(self, environment_name: str, base_url: str,
                 api_key: str = None, api_auth_token: str = None,
                 api_auth_setting: EnvironmentAuth = None):
        self.__environment_name = environment_name
        self.__api_key = api_key
        self.__api_auth_token = api_auth_token
        self.__base_url = base_url
        self.__api_auth_setting = api_auth_setting

    @property
    def environment_name(self) -> str:
        return self.__environment_name

    @property
    def api_key(self) -> str:
        return self.__api_key

    @api_key.setter
    def api_key(self, new_api_key) -> None:
        self.__api_key = new_api_key

    @property
    def api_auth_token(self) -> str:
        return self.__api_auth_token

    @api_auth_token.setter
    def api_auth_token(self, new_api_auth_token) -> None:
        self.__api_auth_token = new_api_auth_token

    @property
    def base_url(self) -> str:
        return self.__base_url

    @property
    def api_auth_setting(self) -> EnvironmentAuth:
        return self.__api_auth_setting

    def environment_as_dict(self) -> dict:
        return {API_KEY_SETTING: self.__api_key,
                API_AUTH_TOKEN_SETTING: self.__api_auth_token,
                API_ENDPOINT_SETTING: {
                    "url": self.__base_url,
                    "username": self.__api_auth_setting.username,
                    "password": self.__api_auth_setting.password
                }}
