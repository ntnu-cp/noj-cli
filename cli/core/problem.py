import logging
from typing import List, Optional, Union
from .auth import logined_session
from .config import Config
from .course import Course


class Problem:

    def __init__(self, **ks) -> None:
        self.id = ks['problemId']
        self.name = ks['problemName']
        self.status = ks['status']

    @classmethod
    def get_by_id(cls, pid: int):
        with logined_session() as sess:
            resp = sess.get(f'{Config.API_BASE}/problem/{pid}')
            assert resp.ok, resp.text
            payload = resp.json()['data']
        return cls(**payload, problemId=pid)

    @classmethod
    def filter(
        cls,
        *,
        tags: List[str] = [],
    ):
        params = {
            'tags': ','.join(tags) or None,
        }
        params = {k: v for k, v in params.items() if v is not None}
        with logined_session() as sess:
            resp = sess.get(
                f'{Config.API_BASE}/problem',
                params=params,
            )
            problems = resp.json()['data']
        return [*map(lambda p: cls(**p), problems)]

    def copy(
        self,
        target: Optional[Union[str, Course]] = None,
    ) -> int:
        payload = {
            'problemId': self.id,
            'target': target,
        }
        logging.debug(f'payload {payload}')
        with logined_session() as sess:
            resp = sess.post(
                f'{Config.API_BASE}/problem/copy',
                json=payload,
            )
            assert resp.ok, resp.text
        return resp.json()['data']['problemId']
