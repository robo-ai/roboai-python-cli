from robo_bot_cli.main import cli
from click.testing import CliRunner
from os import chdir, getcwd


cwd = None


def setup_module(module):
    global cwd
    cwd = getcwd()
    runner = CliRunner()

    result = runner.invoke(cli, ['environment', 'activate', 'integration'])

    assert result.exit_code == 0
    assert 'The connection to the integration environment was successfully established.' in result.output

    result = runner.invoke(cli, ['login', '--api-key', 'be6b65d4-0b63-4c10-ba8b-e415d9c02e65'])

    assert result.exit_code == 0
    assert 'Successfully authenticated!' in result.output


def test_logs(runner):

    result = runner.invoke(cli, ['logs', '--bot-uuid', 'test-rasa-bot'])

    assert result.exit_code == 0
    assert "Displaying logs for bot 'test-rasa-bot'\n" in result.output


def test_logs_language(runner):

    path = 'tests/test_bots/test_logs/multi_bot'
    chdir(path)
    result = runner.invoke(cli, ['logs', 'en'])

    assert result.exit_code == 0
    assert "Displaying logs for bot 'test-rasa-bot'\n" in result.output

    chdir(cwd)


def test_logs_multiple_language(runner):

    result = runner.invoke(cli, ['logs', 'en', 'es'])

    assert result.exit_code == 0
    assert "Please select only one bot to check the logs." in result.output


def test_logs_default_structure(runner):

    path = 'tests/test_bots/test_logs/default_bot'
    chdir(path)
    result = runner.invoke(cli, ['logs'])

    assert result.exit_code == 0
    assert "Displaying logs for bot 'test-rasa-bot'\n" in result.output

    chdir(cwd)
