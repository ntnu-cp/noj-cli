import json
import click
from cli.core import (
    Homework,
    Config,
)
from cli.core.auth import logined_session
from typing import Optional


@click.group()
def ip_filter():
    pass


@ip_filter.command()
@click.option('-i', '--id', help='Homework ID')
@click.option('-n', '--name', help='Homework\'s name')
@click.option(
    '-c',
    '--course',
    help='Course name, should be provided with -n/--name option',
    required=True,
)
def get(
    course: str,
    id: Optional[str],
    name: Optional[str],
):
    '''
    Get homework's ip filters
    '''
    if id is not None:
        hw = Homework.get_by_id(id)
    elif name is not None:
        hw = Homework.get_by_name(course, name)
    else:
        raise ValueError('Option error, either id or name should be provided.')
    with logined_session() as sess:
        url = f'{Config.API_BASE}/homework/{course}/{hw.name}/ip-filters'
        ip_filters = sess.get(url).json()['data']['ipFilters']
    print(json.dumps(ip_filters))
