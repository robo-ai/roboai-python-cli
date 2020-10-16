from robo_bot_cli.main import cli
from os import makedirs, chdir, getcwd
from os.path import join
from shutil import rmtree


path = None
cwd = None


def setup_module(module):
    global path
    path = 'tests/test_bots/'
    global cwd
    cwd = getcwd()
    makedirs(join(path, 'test_clean', 'build'))
    chdir(join(path, 'test_clean'))


def test_clean(runner):

    result = runner.invoke(cli, ['clean'])

    assert result.exit_code == 0
    assert 'Successfully cleaned' in result.output


def teardown_module(module):
    chdir(cwd)
    rmtree(join(path, 'test_clean'))
