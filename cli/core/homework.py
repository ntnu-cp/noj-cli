import sys
from datetime import datetime
from typing import Any, Dict, List
from .auth import logined_session
from .config import Config


class Homework:

    class NotFound(Exception):
        '''
        Can not find a homework
        '''

    def __init__(
        self,
        _id: str,
        name: str,
        problem_ids: List[int],
        start: int,
        end: int,
        student_status: Dict[str, Any],
    ) -> None:
        self.id = _id
        self.name = name
        self.problem_ids = problem_ids
        self.student_status = student_status
        self.start = datetime.fromtimestamp(start)
        self.end = datetime.fromtimestamp(end)

    @classmethod
    def get_by_name(
        cls,
        course: str,
        name: str,
    ):
        with logined_session() as sess:
            url = f'{Config.API_BASE}/course/{course}/homework'
            hws = sess.get(url).json()['data']
            try:
                hw = next(hw for hw in hws if hw['name'] == name)
            except StopIteration:
                raise cls.NotFound(
                    f'Homework not found. [course={course}, name={name}]')
        return cls(
            _id=hw['id'],
            name=hw['name'],
            start=hw['start'],
            end=hw['end'],
            problem_ids=hw['problemIds'],
            student_status=hw['studentStatus'],
        )

    @classmethod
    def get_by_id(
        cls,
        id: str,
    ):
        '''
        Get single homework by id
        '''
        with logined_session() as sess:
            url = f'{Config.API_BASE}/homework/{id}'
            resp = sess.get(url)
            if resp.status_code == 404:
                raise cls.NotFound(f'Homework not found. [id={id}]')
            hw = resp.json()['data']
        return cls(
            _id=id,
            name=hw['name'],
            start=hw['start'],
            end=hw['end'],
            problem_ids=hw['problemIds'],
            student_status=hw['studentStatus'],
        )

    def get_score(
        self,
        weights: Dict[int, int] = None,
    ) -> str:
        '''
        Return homework scores in csv format
        '''
        pass

    def export_score(self, target=sys.stdout):
        pass
