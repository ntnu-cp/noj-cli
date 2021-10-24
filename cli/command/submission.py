import click
import pathlib
import json
import sys
from datetime import datetime
from typing import (
    Tuple,
    Optional,
)
from cli.core import Submission

__all__ = ('submission', )


@click.group()
def submission():
    pass


@submission.command()
@click.option('-i', '--id')
def get(id):
    '''
    Get single submission by id
    '''
    output = Submission.get_by_id(id).to_dict()
    print(json.dumps(output))


@submission.command()
@click.option(
    '-p',
    '--pid',
    type=int,
    multiple=True,
    required=True,
)
@click.option(
    '-o',
    '--output',
    # FIXME: the writable check seems to not working
    type=click.Path(writable=True, path_type=pathlib.Path),
    default=None,
)
@click.option(
    '-f',
    '--field',
    default=['id'],
    multiple=True,
)
@click.option(
    '-b',
    '--before',
)
def get_list(
    pid: Tuple[int],
    output: Optional[pathlib.Path],
    field: Tuple[int],
    before: Optional[str],
):
    '''
    Get submission list
    '''
    def filter(s: Submission):
        s = s.to_dict()
        return {f: s[f] for f in field}

    if before is not None:
        before = datetime.fromisoformat(before)
    submissions = []
    for i in pid:
        submissions.extend(map(filter, Submission.filter(i, before)))
    if output is None:
        output = sys.stdout
    else:
        output = output.open('w')
    json.dump(submissions, output)
