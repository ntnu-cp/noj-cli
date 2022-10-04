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
from tqdm import tqdm
from cli.core import Submission
from cli.core.submission import LanguageType
from cli.core import submission as submission_lib

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
    '--status',
    type=int,
    help='Submission status. e.g. 0 is AC.',
)
@click.option(
    '-b',
    '--before',
)
def get_list(
    pid: Tuple[int],
    output: Optional[pathlib.Path],
    field: Tuple[str],
    before: Optional[str],
    tag: Tuple[str],
    course: Optional[str],
    status: Optional[int],
):
    '''
    Get submission list
    '''
    if len(pid) == 0 and len(tag) == 0:
        print('Either pid or tag must be given')
        exit(1)

    def extract_fields(s: Submission):
        s = s.to_dict()
        return {f: s[f] for f in field}

    if before is not None:
        before = datetime.fromisoformat(before)
    shared_filter = partial(
        Submission.filter,
        course=course,
        before=before,
        status=status,
    )
    submission_filter = lambda *args, **ks: map(
        extract_fields,
        shared_filter(*args, **ks),
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


@submission.command()
@click.option('--pid', type=int, required=True)
@click.option(
    '-o',
    '--output',
    type=click.Path(
        writable=True,
        path_type=pathlib.Path,
        dir_okay=True,
        file_okay=False,
    ),
    default=None,
    help='Output directory. Default to problem id.',
)
@click.option(
    '--before',
    help='Download code only submitted before specific time. (ISO format)',
)
@click.option(
    '--after',
    help='Download code only submitted after specific time. (ISO format)',
)
def get_problem_code(
    pid: int,
    output: Optional[pathlib.Path],
    before: Optional[str],
    after: Optional[str],
):
    '''
    Download all source code of a problem
    '''
    if output is None:
        output = pathlib.Path(str(pid))
        if output.exists():
            print(f'The output directory {output} has been created.')
            exit(1)
        output.mkdir()
    else:
        output.mkdir(exist_ok=True)
    if before is not None:
        before = datetime.fromisoformat(before)
    if after is not None:
        after = datetime.fromisoformat(after)
    query_params = {
        k: v
        for k, v in dict(
            problem_id=pid,
            before=before,
            after=after,
        ).items() if v is not None
    }
    submissions = Submission.filter(**query_params)
    print(f'Found {len(submissions)} submissions.')
    print('Start downloading code.')
    for submission in tqdm(submissions):
        # Reload for code
        submission = Submission.get_by_id(submission.id)
        user_dir = output / submission.user.username
        user_dir.mkdir(exist_ok=True)
        main_filename = submission_lib.filename(submission.language_type)
        main_filename = f'{submission.id}{pathlib.Path(main_filename).suffix}'
        (user_dir / main_filename).write_text(submission.code)
