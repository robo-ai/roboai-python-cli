from robo_bot_cli.main import cli
from os import chdir, getcwd


cwd = None


def setup_module(module):
    global cwd
    cwd = getcwd()
    print(cwd)


def test_endpoint_default(runner):

    path = 'tests/test_bots/test_package/default_bot/'
    chdir(path)

    result = runner.invoke(cli, ['package'])

    assert result.exit_code == 0
    assert 'Package file: build/package.zip' in result.output

    chdir(cwd)


def test_endpoint_language(runner):

    path = 'tests/test_bots/test_package/multi_bot/'
    chdir(path)

    result = runner.invoke(cli, ['package', 'en'])

    assert result.exit_code == 0
    assert 'Package file: build/package.zip' in result.output

    chdir(cwd)


def test_logs_multiple_language(runner):

    result = runner.invoke(cli, ['package', 'en', 'es'])

    assert result.exit_code == 0
    assert "Please select only one bot to package." in result.output
