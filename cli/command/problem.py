from typing import Optional

import click
from cli.core import Problem

__all__ = ('problem', )


@click.group()
def problem():
    pass


@problem.command
@click.option(
    '--problem',
    help='ID of the problem you want to copy',
    required=True,
    type=int,
)
@click.option(
    '--target',
    help=('Name of target course. '
          'Default to the same course of problem\'s'),
)
def copy(
    problem: int,
    target: Optional[str],
):
    '''
    Copy a problem to target course
    '''
    Problem.get_by_id(problem).copy(target)
