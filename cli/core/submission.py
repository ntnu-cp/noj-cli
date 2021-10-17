import enum
import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from .config import Config
from .auth import logined_session
from .user import User


class LanguageType(enum.Enum):
    C = 0
    CPP = 1
    PY3 = 2
    HAND = 3


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
            tasks: List[List[Any]],
            code: Optional[str] = None,
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
            tasks=p['tasks'],
        )

    @classmethod
    def get_by_id(cls, _id: str):
        with logined_session() as sess:
            resp = sess.get(f'{Config.API_BASE}/submission/{_id}')
            assert resp.ok, resp.text
        return cls.load_payload(resp.json()['data'])

    @classmethod
    def filter(cls, problem_id: int) -> List['Submission']:
        '''
        Get submission by parameter
        '''
        with logined_session() as sess:
            submissions = sess.get(
                f'{Config.API_BASE}/submission',
                params={
                    'offset': 0,
                    'count': -1,
                    'problemId': problem_id,
                },
            ).json()['data']['submissions']
        return [cls.load_payload(s) for s in submissions]

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
            success = False
            for _ in range(max_retry):
                resp = sess.get(f'{Config.API_BASE}/submission/{self.id}')
                assert resp.ok, resp.text
                if resp.json()['data']['status'] >= 0:
                    success = True
                    break
                time.sleep(interval)
            if not success:
                raise RuntimeError('Rejudge fail')
