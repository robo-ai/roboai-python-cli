from robo_bot_cli.main import cli
from click.testing import CliRunner


def setup_module(module):
    runner = CliRunner()

    result = runner.invoke(cli, ['environment', 'activate', 'integration'])

    assert result.exit_code == 0
    assert 'The connection to the integration environment was successfully established.' in result.output


def test_login_prompt(runner):
    result = runner.invoke(cli, ['login'], input='be6b65d4-0b63-4c10-ba8b-e415d9c02e65')

    assert result.exit_code == 0
    assert 'Successfully authenticated!\n' in result.output


def test_login(runner):
    result = runner.invoke(cli, ['login', '--api-key', 'be6b65d4-0b63-4c10-ba8b-e415d9c02e65'])

    assert result.exit_code == 0
    assert 'Successfully authenticated!' in result.output


def test_wrong_key(runner):
    result = runner.invoke(cli, ['login'], input='be6b65d4-0b63-4c10-ba8b')

    assert result.exit_code == 0
    assert 'The API key is invalid.' in result.output
