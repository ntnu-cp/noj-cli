import click
import logging

from .submission import submission
from .ip_filter import ip_filter


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
noj.add_command(ip_filter)
