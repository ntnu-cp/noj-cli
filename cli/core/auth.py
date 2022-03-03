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


def is_valid_username(name: str) -> bool:
    '''
    Check whether a username is valid to use
    '''
    with logined_session() as sess:
        resp = sess.post(
            f'{Config.API_BASE}/auth/check/username',
            json={'username': name},
        )
        if not resp.ok:
            # TODO: error handling & logging
            return False
        valid = resp.json()['data']['valid']
    return bool(valid)


def is_valid_email(email: str) -> bool:
    '''
    Check whether a username is valid to use
    '''
    with logined_session() as sess:
        resp = sess.post(
            f'{Config.API_BASE}/auth/check/email',
            json={'email': email},
        )
        if not resp.ok:
            # TODO: error handling & logging
            return False
        valid = resp.json()['data']['valid']
    return bool(valid)
