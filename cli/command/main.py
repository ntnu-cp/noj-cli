import re
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
import click


@click.group()
@click.option(
    '--debug',
    help='Enable debug',
    is_flag=True,
)
def noj(debug: bool):
    if debug:
        logging.basicConfig(level=logging.DEBUG)


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
    '-d',
    '--deadline',
    help='''
    Homework's deadline and score ratio. In format '<data>,<ratio>'.
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
    '-w',
    '--weight',
    help='',
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
        if deadline is None:
            deadline = f'{homework.end.isoformat()},100'
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
    if deadline is not None:
        deadline = [d.split(',') for d in deadline]
        if any(len(d) != 2 for d in deadline):
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
    submissions = [*chain(*(Submission.filter(i) for i in pid))]
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
        submissions = Submission.filter(i)
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


@noj.command()
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
    required=True,
)
def submission(
    pid: Tuple[int],
    output: pathlib.Path,
):
    submissions = []
    for i in pid:
        submissions.extend([s.id for s in Submission.filter(i)])
    json.dump(submissions, output.open('w'))


# TODO: seperate this from main.py


@noj.command()
@click.option(
    '-p',
    '--pid',
    type=int,
    multiple=True,
)
def copycat(pid: Tuple[int]):
    from cli.core.auth import logined_session
    urls = {}
    with logined_session() as sess:
        for i in pid:
            resp = sess.post(
                f'{Config.API_BASE}/copycat',
                json={
                    'course': 'Computer-Programming-II',
                    'problemId': i,
                },
            )
            assert resp.ok, resp.text
        for i in pid:
            resp = sess.get(
                f'{Config.API_BASE}/copycat',
                params={
                    'course': 'Computer-Programming-II',
                    'problemId': i,
                },
            )
            assert resp.ok, resp.text
            urls[i] = resp.json()['data']['cppReport']
    print(urls)


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
