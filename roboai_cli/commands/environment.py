import click

from roboai_cli.config.tool_settings import ToolSettings
from robo_ai.exception.invalid_credentials_error import InvalidCredentialsError
from robo_ai.model.config import Config
from roboai_cli.util.cli import loading_indicator, print_error, print_success, print_info
from roboai_cli.util.robo import get_robo_client
from roboai_cli.config.environment_settings import EnvironmentAuth, Environment


@click.command(name='environment', help='Define the ROBO.AI platform API endpoint to use.')
@click.argument('action', nargs=1)
@click.argument('env_name', nargs=-1)
@click.option('--base-url', type=str)
@click.option('--username', default=None, help='The HTTP basic authentication username to use')
@click.option('--password', default=None, help='The HTTP basic authentication password to use')
def command(action: tuple, env_name: str, base_url: str, username: str, password: str):

    """
    Define the ROBO.AI platform API endpoint to use.

    Args:
        action: which action to be applied. Possible actions:
            - create: create an environment
            - remove: remove an environment
            - activate: activate an environment
            - which: indicate which environment is activated
        env_name: name of the environment to create, remove, activate
        base-url (str): Endpoint url of the environment to be created
        username: basic authentication username to use
        password: basic authentication password to use
    """

    settings = ToolSettings()

    if action == 'create':
        create_environment(settings, env_name, base_url, username, password)
    elif action == 'activate':
        activate_environment(settings, env_name)
    elif action == 'remove':
        remove_environment(settings, env_name)
    elif action == 'which':
        which_environment(settings)
    elif action == 'list':
        list_environments(settings)


def create_environment(settings, new_env_name, base_url, username, password):
    new_env_name = new_env_name[0]
    verify_endpoint_validity(base_url, username, password)

    settings = ToolSettings()
    if username and password:
        env_auth = EnvironmentAuth(username, password)
    else:
        env_auth = None
    environment = Environment(environment_name=new_env_name, base_url=base_url,
                              api_auth_setting=env_auth)
    settings.update_environment(environment)

    print_success(f"The environment was successfully created.\nYou can now activate it by running "
                  f"'roboai environment activate {new_env_name}'.\n")


def activate_environment(settings, env_name):
    env_name = env_name[0]
    environment = settings.get_environment(env_name)
    if not environment:
        print_error("The environment you're trying to activate is not configured yet.\n")
        exit(0)
    verify_endpoint_validity(environment.base_url, environment.api_auth_setting.username,
                             environment.api_auth_setting.password, environment)
    settings.set_current_environment(environment)
    print_success(f"The connection to the {env_name} environment was successfully established.")


def remove_environment(settings, env_name):
    env_name = env_name[0]
    settings.remove_environment(env_name)
    print_success(f"'{env_name}' has been removed successfully.")


def which_environment(settings):
    current_environment = settings.get_current_environment()
    if not current_environment:
        print_info("No environment is currently activated.\nRun 'roboai environment activate <env-name>' to activate"
                   "an environment.")
    else:
        print_info(f"The '{current_environment.environment_name}' environment is currently activated.")


def list_environments(settings):
    environments_list = settings.get_environments()
    print("# roboai environments:\n")
    for environment in environments_list:
        print(environment)


# FIXME: this is a dummy way of checking endpoint validity, it doesn't verify if credentials are valid
def is_endpoint_config_valid(url, username: str, password: str, environment: Environment = None) -> bool:
    config = Config(url, http_auth={
        'username': username,
        'password': password
    })
    if not environment:
        robo_ai = get_robo_client(config=config)
    else:
        robo_ai = get_robo_client(environment, config)
    try:
        robo_ai.oauth.authenticate('')
    except InvalidCredentialsError:
        return True
    except Exception:
        return False

    return False


def verify_endpoint_validity(base_url: str, username: str, password: str, env_name: str = None):
    with loading_indicator('Verifying the endpoint validity...') as spinner:
        if not is_endpoint_config_valid(base_url, username, password, env_name):
            spinner.stop()
            print_error('The endpoint configuration is invalid.\n')
            return


if __name__ == "__main__":
    command()
