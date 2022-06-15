import enum
import logging
from pathlib import Path
import sys
import tempfile
import time
from datetime import datetime
from zipfile import ZipFile
from typing import (
    Any,
    Dict,
    List,
    Literal,
    Optional,
    Union,
)

from .config import Config
from .auth import logined_session
from .user import User


class LanguageType(enum.IntEnum):
    C = 0
    CPP = 1
    PY3 = 2
    HAND = 3


def filename(lang: LanguageType):
    if lang == LanguageType.C:
        return 'main.c'
    if lang == LanguageType.CPP:
        return 'main.cpp'
    if lang == LanguageType.PY3:
        return 'main.py'
    raise ValueError('Cannot determine filename by language')


class Submission:
    # TODO: use class to wrap task result
    class TaskResult:

        def __init__(self) -> None:
            pass

    # TODO: use Enum to define status
    def __init__(
        self,
        _id: str,
        user: Union[User, Dict[str, Any]],
        last_send: float,
        created: float,
        memory_usage: int,
        problem_id: int,
        run_time: int,
        score: int,
        status: int,
        language_type: Union[LanguageType, int],
        tasks: Optional[List[List[Any]]],
        code: Optional[Union[str, bool]] = None,
    ) -> None:
        self.id = _id
        self.last_send = datetime.fromtimestamp(last_send)
        self.created = datetime.fromtimestamp(created)
        self.memory_usage = memory_usage
        self.problem_id = problem_id
        self.run_time = run_time
        self.score = score
        self.status = status
        self.language_type = LanguageType(language_type)
        self.tasks = tasks
        self.code = code
        if isinstance(user, Dict):
            user = User(**user)
        self.user = user

    def __str__(self) -> str:
        return f'Submission [{self.id}]'

    def to_dict(self):
        return {
            'id': self.id,
            'user': self.user.to_dict(),
            'status': self.status,
            'run_time': self.run_time,
            'memory_usage': self.memory_usage,
            'score': self.score,
            'problem_id': self.problem_id,
            'code': self.code,
            'last_send': self.last_send.isoformat(),
        }

    @classmethod
    def load_payload(cls, p: Dict[str, Any]) -> 'Submission':
        return cls(
            _id=p['submissionId'],
            user=p['user'],
            last_send=p['lastSend'],
            created=p['timestamp'],
            memory_usage=p['memoryUsage'],
            problem_id=p['problemId'],
            run_time=p['runTime'],
            score=p['score'],
            status=p['status'],
            language_type=p['languageType'],
            tasks=p.get('tasks'),
            code=p.get('code'),
        )

    @classmethod
    def get_by_id(cls, _id: str):
        with logined_session() as sess:
            resp = sess.get(f'{Config.API_BASE}/submission/{_id}')
            assert resp.ok, resp.text
        return cls.load_payload(resp.json()['data'])

    @classmethod
    def filter(
        cls,
        course: Optional[str] = None,
        tags: List[str] = [],
        problem_id: Optional[int] = None,
        before: Optional[datetime] = None,
        user: Optional[Union[str, User]] = None,
        after: Optional[datetime] = None,
    ) -> List['Submission']:
        '''
        Get submission by parameter
        '''
        params = {
            'offset': 0,
            'count': -1,
        }
        if course is not None:
            params['course'] = course
        if problem_id is not None:
            params['problemId'] = problem_id
        if user is not None:
            if isinstance(user, str):
                params['username'] = user
            else:
                params['username'] = user.username
        if len(tags):
            params['tags'] = ','.join(tags)
        if before is not None:
            params['before'] = int(before.timestamp())
        if after is not None:
            params['after'] = int(after.timestamp())
        with logined_session() as sess:
            submissions = sess.get(
                f'{Config.API_BASE}/submission',
                params=params,
            ).json()['data']['submissions']
        submissions = map(cls.load_payload, submissions)
        return list(submissions)

    def rejudge(
        self,
        max_retry: int = 20,
        interval: int = 3,
    ):
        if self.language_type == LanguageType.HAND:
            logging.warning('Rejudge a handwriten submission')
            return
        with logined_session() as sess:
            resp = sess.get(f'{Config.API_BASE}/submission/{self.id}/rejudge')
            assert resp.ok, resp.text
            # Check rejudge result
            for _ in range(max_retry):
                resp = sess.get(f'{Config.API_BASE}/submission/{self.id}')
                assert resp.ok, resp.text
                if resp.json()['data']['status'] >= 0:
                    break
                time.sleep(interval)
            else:
                raise RuntimeError('Rejudge fail')

    @classmethod
    def submit(
        cls,
        problem_id: int,
        lang: LanguageType,
        code_path: Union[Path, Literal['-']],
    ):
        if isinstance(code_path, Path):
            code = code_path.read_text()
        elif code_path == '-':
            code = sys.stdin.read()
        else:
            raise ValueError(f'\'code_path\' should be a Path or \'-\'')
        source_name = filename(lang)
        with logined_session() as sess:
            resp = sess.post(
                f'{Config.API_BASE}/submission',
                json={
                    'languageType': int(lang),
                    'problemId': problem_id,
                },
            )
            r_data = resp.json()
            if resp.status_code == 403:
                raise PermissionError(r_data['message'])
            elif resp.status_code in {404, 400}:
                raise ValueError(r_data['message'])
            submission_id = r_data['data']['submissionId']
            logging.debug(f'submission created [id={submission_id}]')
            with tempfile.NamedTemporaryFile() as tf:
                with ZipFile(tf, 'w') as zf:
                    zf.writestr(source_name, code)
                tf.seek(0)
                resp = sess.put(
                    f'{Config.API_BASE}/submission/{submission_id}',
                    files={'code': tf},
                )
                if resp.status_code != 200:
                    print(resp.json())
                    return False
        return True
