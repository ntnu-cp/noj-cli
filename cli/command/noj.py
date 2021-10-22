import click
import logging


@click.group()
@click.option(
    '--debug',
    help='Enable debug',
    is_flag=True,
)
def noj(debug: bool):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
