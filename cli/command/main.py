import re
import sys
import json
import pathlib
import logging
from datetime import datetime
from itertools import chain
from typing import (
    Optional,
    Tuple,
    List,
)

from cli.core import (
    Submission,
    Config,
    MultiDeadLinePolicy,
    Homework,
)
from cli.core import util
from cli.command.noj import noj
import click


@noj.command()
@click.option(
    '-p',
    '--pid',
    help='Problem IDs',
    multiple=True,
    type=int,
)
@click.option(
    '--homework',
    help='''
    Homework in format '<course_name>/<homework_name>'.
    If given, then problem ids will be ignored.
    ''',
)
@click.option(
    '--deadline',
    help='''
    Homework's deadline and score ratio. In format '<date>,<ratio>'.
    The date part will be parsed by python's `datetime.fromisoformat`.
    ratio is an integer in [0, 100]. If not pass, then first try to
    use homework's deadline with ratio 100, otherwise use `datetime.max`.
    ''',
    multiple=True,
)
@click.option(
    '-o',
    '--output',
    help='The output path. Default value are \'output.csv\'.',
    default=pathlib.Path('output.csv'),
    # FIXME: the writable check seems to not working
    type=click.Path(writable=True, path_type=pathlib.Path),
)
@click.option(
    '-e',
    '--exclude',
    help='',
)
@click.option(
    '--weight',
    help=('Weights used to calculate scores.\n'
          'Given in the format: <pid>=<ratio>.\n'
          'e.g. 487=63 means that problem 487 has weight 63%.\n'
          'You must set ratio for each problem of this query.\n'
          'If this option is not set, the weights are equally distributed.\n'),
    multiple=True,
)
def grade(
    pid: Optional[Tuple[int]],
    homework: Optional[str],
    deadline: Tuple[str],
    output: pathlib.Path,
    exclude: Optional[str],
    weight: Tuple[str],
):
    '''
    Generate score file
    '''
    if homework is not None:
        # Try to get homework
        course, homework = homework.split('/')
        homework = Homework.get_by_name(course, homework)
        # Use course's student list
        students = [*homework.student_status.keys()]
        # Use homework's problems
        pid = homework.problem_ids
        # Use homework deadline if not given
        if len(deadline) == 0:
            deadline = [f'{homework.end.isoformat()},100']
    else:
        # Use policy default
        students = None
    # If weight is passed
    if weight:
        w_pat = r'^\d+=\d+$'
        if any(not re.match(w_pat, w) for w in weight):
            raise ValueError('Get invalid weight value')
        weight = {
            int(i): int(w)
            for i, w in map(lambda x: x.split('='), weight)
        }
    else:
        weight = None
    # Convert deadlines
    if len(deadline) != 0:
        deadline = [d.split(',') for d in deadline]
        if any(len(d) != 2 for d in deadline):
            logging.debug(f'Got deadline: {deadline}')
            raise ValueError('Invalid deadline format.')
        deadline = [(
            datetime.fromisoformat(d[0]),
            int(d[1]),
        ) for d in deadline]
    # Exclude students
    if exclude is not None:
        # Try read from file
        if exclude.startswith('@'):
            with open(exclude[1:]) as f:
                exclude = f.read()
            exclude = exclude.split('\n')
        # Comma-seperated names
        else:
            exclude = exclude.split(',')
        # Trim each name and filter empty string
        exclude = [*filter(bool, (name.strip() for name in exclude))]
    logging.debug(f'Grade parameter:')
    if homework is not None:
        logging.debug(f'Homework: {homework.name}')
    if weight is not None:
        logging.debug(f'Weights: {weight}')
    logging.debug(f'Deadline: {deadline}')
    logging.debug(f'Exclude list: {exclude}')
    submissions = [*chain(*(Submission.filter(problem_id=i) for i in pid))]
    policy = MultiDeadLinePolicy(
        submissions,
        students=students,
        deadlines=deadline,
        excludes=exclude,
        weights=weight,
    )
    policy.gen_score(output)


@noj.command()
@click.option(
    '-p',
    '--pid',
    help='The problem ID(s) want to be rejudged.',
    type=int,
    multiple=True,
)
@click.option(
    'file',
    '-f',
    '--file',
    type=click.Path(
        writable=True,
        readable=True,
        path_type=pathlib.Path,
    ),
)
def rejudge(
    pid: Tuple[int],
    file: Optional[pathlib.Path],
):
    '''
    Rejudge submissions by problem id
    '''
    logging.debug(f'Rejudge for problems: {pid}')
    if file is not None:
        submission_ids = json.load(file.open('r'))
        fails = []
        submissions = map(Submission.get_by_id, submission_ids[:])
        for chunk in util.chunker_list(submissions, 10):
            for i, s in enumerate(chunk):
                json.dump(
                    fails + submission_ids,
                    file.open('w'),
                )
                if s.status == -2:
                    continue
                try:
                    s.rejudge(interval=5)
                except RuntimeError as e:
                    logging.debug(f'Fail at {s.id}: {e}')
                    fails.append(s.id)
                submission_ids.remove(s.id)
        return
    for i in pid:
        logging.debug(f'Start rejudge problem {i}')
        # Get submissions by problem id
        submissions = Submission.filter(problem_id=i)
        logging.debug(f'Found {len(submissions)} submissions')
        fails = []
        for chunk in util.chunker_list(submissions, 10):
            for i, s in enumerate(chunk):
                if s.status == -2:
                    continue
                s.rejudge(interval=5)
        if fails:
            logging.debug(f'Failed submissions for {i}')
            logging.debug(f'{[s.id for s in fails]}')


# TODO: seperate this from main.py


@noj.command()
@click.option('-c', '--course', required=True)
@click.option('-s', '--student', multiple=True)
@click.option('-t', '--ta', multiple=True)
def add_student(
    course: str,
    student: List[str],
    ta: List[str],
):
    from cli.core.auth import logined_session
    students = {s: s for s in student}
    with logined_session() as sess:
        resp = sess.put(
            f'{Config.API_BASE}/course/{course}',
            json={
                'studentNicknames': students,
                'TAs': ta,
            },
        )
        assert resp.ok, resp.text
