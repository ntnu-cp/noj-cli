import click
from cli.core.auth import (
    is_valid_username,
    is_valid_email,
)

__all__ = ('user', )


@click.group()
def user():
    pass


@user.command()
@click.argument('name')
def validate_username(name: str):
    '''
    '''
    valid = is_valid_username(name)
    if not valid:
        click.echo(f'{name} cannot be used')
        exit(1)


@user.command()
@click.argument('email')
def validate_email(email: str):
    valid = is_valid_email(email)
    if not valid:
        click.echo(f'{email} cannot be used')
        exit(1)
