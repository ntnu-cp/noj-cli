import click
import pathlib
import json
import sys
from functools import partial
from datetime import datetime
from typing import (
    Tuple,
    Optional,
)
from cli.core import Submission
from cli.core.submission import LanguageType

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
)
@click.option(
    '-t',
    '--tag',
    type=str,
    multiple=True,
)
@click.option(
    '-c',
    '--course',
    type=str,
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
    tag: Tuple[str],
    course: Optional[str],
):
    '''
    Get submission list
    '''
    if len(pid) == 0 and len(tag) == 0:
        print('Either pid or tag must be given')
        exit(1)
    if before is not None:
        before = datetime.fromisoformat(before)

    def _filter(s: Submission):
        s = s.to_dict()
        return {f: s[f] for f in field}

    _submission_filter = partial(
        Submission.filter,
        course=course,
        before=before,
    )
    submission_filter = lambda *args, **ks: map(
        _filter,
        _submission_filter(*args, **ks),
    )

    submissions = []
    if tag:
        submissions.extend(submission_filter(tags=tag))
    for i in pid:
        submissions.extend(submission_filter(problem_id=i))
    if output is None:
        output = sys.stdout
    else:
        output = output.open('w')
    json.dump(submissions, output)


@submission.command()
@click.argument('problem', type=int)
@click.option(
    '--code',
    type=str,
    default='-',
    help='Path to the source code.'
    'Read from stdin if not given or its value is -',
)
@click.option(
    '--lang',
    type=int,
    help='Submission language. Inferred from filename extension if not given',
)
def submit(
    problem: int,
    code: str,
    lang: Optional[int],
):
    '''
    Create a submission
    '''
    if lang is None:
        if code == '-':
            print('Must specify language if source file not provided')
            exit(1)
        if code.endswith('.c'):
            lang = LanguageType.C
        elif code.endswith('.cpp'):
            lang = LanguageType.CPP
        elif code.endswith('.py'):
            lang = LanguageType.PY3
        else:
            print('Unknow file extension')
            exit(1)
    if code != '-':
        code = pathlib.Path(code)
    result = Submission.submit(
        problem_id=problem,
        lang=lang,
        code_path=code,
    )
    if result == False:
        exit(1)
