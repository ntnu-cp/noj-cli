from typing import List
from .auth import logined_session
from .config import Config


class Problem:

    def __init__(self, **ks) -> None:
        self.problem_id = ks['problemId']
        self.problem_name = ks['problemName']
        self.status = ks['status']

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
