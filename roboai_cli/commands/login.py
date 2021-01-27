import click

from roboai_cli.config.tool_settings import ToolSettings
from robo_ai.exception.invalid_credentials_error import InvalidCredentialsError
from roboai_cli.util.cli import print_error, loading_indicator, print_success
from roboai_cli.util.robo import get_robo_client


@click.command(name='login', help='Initialize a new session using a ROBO.AI API key.')
@click.option('--api-key', prompt='Please enter your ROBO.AI API key', help='The ROBO.AI platform API key.')
def command(api_key: str):
    """
    Initialize a new session using a ROBO.AI API key,

    Args:
        api_key (str): API key
    """
    settings = ToolSettings()
    current_environment = settings.get_current_environment()  # this should be an object now
    robo = get_robo_client(current_environment)
    try:
        with loading_indicator('Authenticating...'):
            tokens = robo.oauth.authenticate(api_key)

        current_environment.api_key = api_key
        current_environment.api_auth_token = tokens.access_token
        settings.update_environment(current_environment)
        print_success('Successfully authenticated!\n')

    except InvalidCredentialsError:
        print_error('The API key is invalid.\n')


if __name__ == "__main__":
    command()
