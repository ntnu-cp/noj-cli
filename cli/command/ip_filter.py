import json
import logging
from typing import Optional
from cli.core import (
    Homework,
    Config,
)
from cli.core.auth import logined_session
import click


@click.group()
def ip_filter():
    pass


def patch(
    op: str,
    ip: str,
    course: str,
    id: Optional[str],
    name: Optional[str],
):
    if id is not None:
        hw = Homework.get_by_id(id)
    elif name is not None:
        hw = Homework.get_by_name(course, name)
    else:
        raise ValueError('Option error, either id or name should be provided.')
    with logined_session() as sess:
        url = f'{Config.API_BASE}/homework/{course}/{hw.name}/ip-filters'
        resp = sess.patch(
            url,
            json={'patches': [{
                'op': op,
                'value': ip,
            }]},
        )
        logging.debug(resp.text)
        if resp.status_code != 200:
            exit(1)


@ip_filter.command()
@click.option('-i', '--id', help='Homework ID')
@click.option('-n', '--name', help='Homework name')
@click.option(
    '-c',
    '--course',
    help='Course name, should be provided with -n/--name option',
    required=True,
)
@click.argument('ip')
def add(*args, **ks):
    '''
    Add IP filter to homework
    '''
    patch(*args, **ks, op='add')


@ip_filter.command()
@click.option('-i', '--id', help='Homework ID')
@click.option('-n', '--name', help='Homework name')
@click.option(
    '-c',
    '--course',
    help='Course name, should be provided with -n/--name option',
    required=True,
)
@click.argument('ip')
def delete(*args, **ks):
    '''
    Remove IP filter from homework
    '''
    patch(*args, **ks, op='del')


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
