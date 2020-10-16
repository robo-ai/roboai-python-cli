from robo_bot_cli.main import cli


def test_logout(runner):
    result = runner.invoke(cli, ['logout'])

    assert result.exit_code == 0
    assert 'Your session was successfully terminated.' in result.output
