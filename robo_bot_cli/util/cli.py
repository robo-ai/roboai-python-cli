import click
from halo import Halo


def loading_indicator(text: str = None):
    return Halo(text=text, spinner="dots")


def print_error(text: str, nl=True):
    click.secho(text, err=True, nl=nl, fg="red")


def print_message(text: str, nl=True):
    click.echo(text, err=False, nl=nl)


def print_warning(text: str, nl=True):
    click.secho("WARNING: " + text, err=False, nl=nl, fg="yellow")


def print_info(text: str, nl=True):
    click.secho(text, err=False, nl=nl, fg="blue")


def print_success(text: str, nl=True):
    click.secho(text, fg="green", nl=nl)
