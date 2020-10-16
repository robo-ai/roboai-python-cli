from robo_bot_cli.main import cli
from os import makedirs
from os.path import abspath, join
from shutil import rmtree


def test_seed_no_language(runner):
    result = runner.invoke(cli, ['seed'])

    assert result.exit_code == 0
    assert 'No language was provided. English will be the default.' in result.output


def test_seed_path(runner):
    path = 'tests/test_bots/basic_bot_seed_path'
    makedirs(path, exist_ok=True)
    result = runner.invoke(cli, ['seed', 'en', 'es', '--path', path], input='y')

    assert result.exit_code == 0
    assert f"Created project directory at '{abspath(path)}'" in result.output

    rmtree(path)


def test_existing_path(runner):
    """
    Given path already exists and is not empty. User is aksed if the bot should still be created.
    """
    path = 'tests/test_bots/basic_bot_existing_path'
    makedirs(path, exist_ok=True)
    with open(join(path, 'test.txt'), 'w') as f:
        f.write("New file created")
    result = runner.invoke(cli, ['seed', 'en', 'es', '--path', path])

    assert result.exit_code == 0
    assert f"Directory '{path}' is not empty. Continue?" in result.output

    rmtree(path)


def test_non_existing_path(runner):
    """
    Given path does not exist. User is asked if the path should be created.
    """
    path = 'tests/test_bots/basic_bot_non_existing_path'
    print(path)
    result = runner.invoke(cli, ['seed', 'en', 'es', '--path', path])

    assert result.exit_code == 0
    assert f"Path '{path}' does not exist 🧐. Create path?" in result.output


def test_existing_path_positive(runner):
    """
    Given path already exists and is not empty. User is aksed if the bot should still be created.
    Answer is yes.
    """
    path = 'tests/test_bots/basic_bot_existing_path_positive'
    makedirs(path, exist_ok=True)
    with open(join(path, 'test.txt'), 'w') as f:
        f.write("New file created")
    result = runner.invoke(cli, ['seed', 'en', 'es', '--path', path], input='y')

    assert result.exit_code == 0
    assert f"Created project directory at '{abspath(path)}'" in result.output

    rmtree(path)


def test_non_existing_path_positive(runner):
    """
    Given path does not exist. User is asked if the path should be created.
    Answer is yes.
    """
    path = 'tests/test_bots/basic_bot_non_existing_path_positive'
    result = runner.invoke(cli, ['seed', 'en', '--path', path], input='y')

    assert result.exit_code == 0
    assert f"Created project directory at '{abspath(path)}'" in result.output

    rmtree(path)


def test_existing_path_negative(runner):
    """
    Given path already exists and is not empty. User is aksed if the bot should still be created.
    Answer is yes.
    """
    path = 'tests/test_bots/basic_bot_existing_path_negative'
    makedirs(path, exist_ok=True)
    with open(join(path, 'test.txt'), 'w') as f:
        f.write("New file created")
    result = runner.invoke(cli, ['seed', 'en', 'es', '--path', path], input='n')

    assert result.exit_code == 0
    assert "To proceed with a fresh bot, please choose a different " \
           "installation directory and then rerun 'robo-bot seed'" in result.output

    rmtree(path)


def test_non_existing_path_negative(runner):
    """
    Given path does not exist. User is asked if the path should be created.
    Answer is yes.
    """
    path = 'tests/test_bots/basic_bot_non_existing_path_negative'
    result = runner.invoke(cli, ['seed', 'en', 'es', '--path', path], input='n')

    assert result.exit_code == 0
    assert "To proceed with a fresh bot, please choose a different " \
           "installation directory and then rerun 'robo-bot seed'" in result.output


def test_language_detection(runner):
    path = 'tests/test_bots/basic_language_detection'
    result = runner.invoke(cli, ['seed', 'en', 'es', '--path', path, '--language-detection'], input='y')

    assert result.exit_code == 0
    assert f"Created project directory at '{abspath(path)}'" in result.output

    rmtree(path)


def test_chit_chat(runner):
    path = 'tests/test_bots/basic_chit_chat'
    result = runner.invoke(cli, ['seed', 'en', 'es', '--path', path, '--chit-chat'], input='y')

    assert result.exit_code == 0
    assert f"Created project directory at '{abspath(path)}'" in result.output

    rmtree(path)


def test_coref_resolution(runner):
    path = 'tests/test_bots/basic_coref_resolution'
    result = runner.invoke(cli, ['seed', 'en', 'es', '--path', path, '--coref-resolution'], input='y')

    assert result.exit_code == 0
    assert f"Created project directory at '{abspath(path)}'" in result.output

    rmtree(path)
