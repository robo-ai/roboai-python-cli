from roboai_cli.config.store import ConfigStore
from .environment_constants import DEFAULT_SETTINGS, PACKAGE_NAME, API_KEY_SETTING, \
    API_AUTH_TOKEN_SETTING, API_ENDPOINT_SETTING, CURRENT_ENVIRONMENT
from .environment_settings import Environment, EnvironmentAuth


class ToolSettings:
    _store = ConfigStore(PACKAGE_NAME, DEFAULT_SETTINGS, globalConfigPath=True)

    def get_api_key(self) -> str:
        return self._store.get(API_KEY_SETTING)

    def set_api_key(self, api_key: str) -> None:
        self._store.set(API_KEY_SETTING, api_key)

    def get_auth_token(self) -> str:
        return self._store.get(API_AUTH_TOKEN_SETTING)

    def set_auth_token(self, auth_token: str) -> None:
        self._store.set(API_AUTH_TOKEN_SETTING, auth_token)

    def get_api_endpoint(self) -> dict:
        return self._store.get(API_ENDPOINT_SETTING)

    def set_api_endpoint(self, endpoint: dict) -> None:
        self._store.set(API_ENDPOINT_SETTING, endpoint)

    def get_environment(self, environment_name: str) -> Environment:
        environment_config = self._store.get(environment_name)
        if environment_config is not None:
            return Environment(environment_name, api_key=environment_config["API_KEY"],
                               api_auth_token=environment_config["API_AUTH_TOKEN"],
                               base_url=environment_config["API_ENDPOINT"]["url"],
                               api_auth_setting=EnvironmentAuth(environment_config["API_ENDPOINT"]["username"],
                               environment_config["API_ENDPOINT"]["password"]))
        else:
            return None

    def update_environment(self, environment) -> None:
        env_dict = environment.environment_as_dict()
        self._store.set(environment.environment_name, env_dict)

    def remove_environment(self, environment_name: str) -> None:
        self._store.delete(environment_name)

    def environment_exists(self, environment_name: str) -> bool:
        self._store.has(environment_name)

    def get_current_environment(self) -> str:
        environment_name = self._store.get(CURRENT_ENVIRONMENT)
        environment_config = self._store.get(environment_name)
        if environment_config is not None:
            return Environment(environment_name, api_key=environment_config["API_KEY"],
                               api_auth_token=environment_config["API_AUTH_TOKEN"],
                               base_url=environment_config["API_ENDPOINT"]["url"],
                               api_auth_setting=EnvironmentAuth(environment_config["API_ENDPOINT"]["username"],
                               environment_config["API_ENDPOINT"]["password"]))
        else:
            return None

    def set_current_environment(self, environment: Environment) -> None:
        if environment is not None:
            self._store.set(CURRENT_ENVIRONMENT, environment.environment_name)
        else:
            self._store.set(CURRENT_ENVIRONMENT, None)

    def get_environments(self) -> list:
        config_dict = self._store.all()
        env_list = list(config_dict.keys())
        env_list.remove(CURRENT_ENVIRONMENT)
        return env_list
