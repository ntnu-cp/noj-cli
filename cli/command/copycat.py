from typing import Tuple
import click
from cli.core import Config, Course
from cli.core.auth import logined_session


@click.group()
def copycat():
    '''
    Copycat API
    '''


@copycat.command()
@click.option(
    '-p',
    '--pid',
    type=int,
    multiple=True,
    help='Problem IDs that need to check',
)
@click.option('-c', '--course')
def generate(pid: Tuple[int], course: str):
    '''
    Generate copycat report
    '''
    course = Course.get_by_name(course)
    students = {s.username: s.username for s in course.students}
    with logined_session() as sess:
        for i in pid:
            resp = sess.post(
                f'{Config.API_BASE}/copycat',
                json={
                    'course': course.name,
                    'problemId': i,
                    'studentNicknames': students,
                },
            )
            assert resp.ok, resp.text


@copycat.command()
@click.option(
    '-p',
    '--pid',
    type=int,
    multiple=True,
    help='Problem IDs that need to check',
)
@click.option('-c', '--course')
def get(pid: Tuple[int], course: str):
    '''
    Fetch copycat report
    '''
    urls = {}
    course = Course.get_by_name(course)
    with logined_session() as sess:
        for i in pid:
            resp = sess.get(
                f'{Config.API_BASE}/copycat',
                params={
                    'course': course.name,
                    'problemId': i,
                },
            )
            assert resp.ok, resp.text
            try:
                urls[i] = resp.json()['data']['cpp_report']
            except KeyError:
                print(resp.json())
                raise
    print(urls)
