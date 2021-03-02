import click
from roboai_cli.commands import (
    login,
    logout,
    connect,
    deploy,
    remove,
    stop,
    start,
    seed,
    status,
    environment,
    package,
    clean,
    logs,
    diff,
    train,
    run,
    shell,
    test,
    interactive,
    stories,
    data
)
from pyfiglet import Figlet

from roboai_cli.__init__ import __version__  # this is wrong but won't work otherwise
from roboai_cli.util.cli import print_message
from roboai_cli.util.text import remove_last_line


@click.group(help=f"roboai {__version__}")
@click.version_option(version=__version__, message=f"roboai {__version__}")
def cli():
    pass


cli.add_command(login.command)
cli.add_command(logout.command)
cli.add_command(connect.command)
cli.add_command(deploy.command)
cli.add_command(remove.command)
cli.add_command(stop.command)
cli.add_command(start.command)
cli.add_command(seed.command)
cli.add_command(status.command)
cli.add_command(environment.command)
cli.add_command(package.command)
cli.add_command(clean.command)
cli.add_command(logs.command)
cli.add_command(diff.command)
cli.add_command(train.command)
cli.add_command(run.command)
cli.add_command(shell.command)
cli.add_command(stories.command)
cli.add_command(test.command)
cli.add_command(interactive.command)
cli.add_command(data.command)

try:
    import colorama

    colorama.init()
except any:
    pass


def get_motd():
    figlet = Figlet(font="standard")
    logo = figlet.renderText("ROBO . AI")
    logo = remove_last_line(remove_last_line(logo))
    logo += "\nBot Management Tool             robo-ai.com\n"
    return logo


def run():
    print_message(get_motd())
    cli()


if __name__ == "__main__":
    run()
