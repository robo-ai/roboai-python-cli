import click
from pyfiglet import Figlet

from robo_bot_cli.__init__ import (
    __version__,
)  # this is wrong but won't work otherwise
from robo_bot_cli.commands import (
    clean,
    connect,
    deploy,
    diff,
    environment,
    interactive,
    login,
    logout,
    logs,
    package,
    remove,
    run,
    seed,
    shell,
    start,
    status,
    stop,
    stories,
    test,
    train,
)
from robo_bot_cli.util.cli import print_message
from robo_bot_cli.util.text import remove_last_line


@click.group(help=f"robo-bot {__version__}")
@click.version_option(version=__version__, message=f"robo-bot {__version__}")
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
