import click
import logging

from .submission import submission
from .ip_filter import ip_filter
from .user import user


@click.group()
@click.option(
    '--debug',
    help='Enable debug',
    is_flag=True,
)
def noj(debug: bool):
    if debug:
        logging.basicConfig(level=logging.DEBUG)


sub_commands = (
    submission,
    ip_filter,
    user,
)
for cmd in sub_commands:
    noj.add_command(cmd)