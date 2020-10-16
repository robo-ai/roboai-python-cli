from robo_bot_cli.main import cli


def test_activate_environment(runner):
    result = runner.invoke(cli, ['environment', 'activate', 'integration'])

    assert result.exit_code == 0
    assert 'The connection to the integration environment was successfully established.' in result.output


def test_create_environment(runner):
    result = runner.invoke(cli, ['environment', 'create', 'development', '--base-url',
                           'http//fake-url.com', '--username', 'fake-user', '--password', 'fake-pass'])

    assert result.exit_code == 0
    assert "The environment was successfully created.\nYou can now activate it by running "\
           "'robo-bot activate development'.\n" in result.output


def test_remove_environment(runner):
    result = runner.invoke(cli, ['environment', 'remove', 'development'])

    assert result.exit_code == 0
    assert "'development' has been successfully removed." in result.output


def test_which_environment(runner):
    result = runner.invoke(cli, ['environment', 'which'])

    assert result.exit_code == 0
    assert "The 'integration' environment is currently activated." in result.output


def test_list_environments(runner):
    result = runner.invoke(cli, ['environment', 'list'])

    assert result.exit_code == 0
    assert "# robo-bot environments:\n" in result.output
