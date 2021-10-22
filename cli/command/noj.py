import click
import logging

from .submission import submission


@click.group()
@click.option(
    '--debug',
    help='Enable debug',
    is_flag=True,
)
def noj(debug: bool):
    if debug:
        logging.basicConfig(level=logging.DEBUG)


noj.add_command(submission)
