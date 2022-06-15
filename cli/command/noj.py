import click
import logging
from .submission import submission
from .ip_filter import ip_filter
from .user import user
from .homework import homework
from .copycat import copycat


@click.group()
@click.option(
    '--debug',
    help='Enable debug',
    is_flag=True,
)
def noj(debug: bool):
    '''
    CLI tool for interacting with Normal OJ API
    '''
    if debug:
        logging.basicConfig(level=logging.DEBUG)


sub_commands = (
    submission,
    ip_filter,
    user,
    homework,
    copycat,
)
for cmd in sub_commands:
    noj.add_command(cmd)