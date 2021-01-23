import click

from roboai_cli.config.tool_settings import ToolSettings
from roboai_cli.util.cli import print_success


@click.command(name='logout', help='Close the current session in the ROBO.AI platform.')
def command():
    """
    Close the current session in the ROBO.AI platform.
    """
    settings = ToolSettings()
    current_environment = settings.get_current_environment()
    current_environment.api_auth_token = None
    current_environment.api_key = None
    settings.update_environment(current_environment)
    settings.set_current_environment(None)
    print_success('Your session was successfully terminated.\n')


if __name__ == "__main__":
    command()
