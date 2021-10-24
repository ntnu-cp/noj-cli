import requests as rq
from .config import Config


def logined_session():
    sess = rq.Session()
    # Config might not load before
    if Config.curr_user is None:
        Config.load()
    resp = sess.post(
        f'{Config.API_BASE}/auth/session',
        json=Config.curr_user,
    )
    if resp.status_code == 403:
        raise PermissionError('Invalid credential.')
    assert resp.ok, resp.text
    return sess
