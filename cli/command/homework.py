import json
import click
from cli.core.homework import Homework

__all__ = ('homework', )


@click.group()
def homework():
    pass


@homework.command()
@click.argument('course')
@click.argument('name')
def get(course: str, name: str):
    '''
    Get single homework by course & homework name
    '''
    hw = Homework.get_by_name(course, name)
    print(json.dumps(hw.to_dict()))
