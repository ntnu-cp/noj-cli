from typing import List
from .auth import logined_session
from .config import Config
from .user import User


class Course:

    def __init__(
        self,
        name: str,
        teacher: User,
        TAs: List[User],
        students: List[User],
    ) -> None:
        self.name = name
        self.teacher = teacher
        self.TAs = TAs
        self.students = students

    @classmethod
    def get_by_name(cls, name: str) -> 'Course':
        with logined_session() as sess:
            resp = sess.get(f'{Config.API_BASE}/course/{name}')
            # TODO: Error handling
            assert resp.ok, resp.text
            payload = resp.json()['data']
        teacher = User(**payload['teacher'])
        TAs = [User(**t) for t in payload['TAs']]
        students = [User(**s) for s in payload['students']]
        return cls(
            name=name,
            teacher=teacher,
            TAs=TAs,
            students=students,
        )
