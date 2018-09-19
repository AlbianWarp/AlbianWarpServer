import jwt

import time
from functools import wraps
from flask import request, session, render_template, jsonify

from warpserver.model.base import db
from warpserver.server import logger
from warpserver.config import SECRET_KEY
from warpserver.model.user import User


def request_token_check():
    token = request.headers.get('token')
    if not token:
        token = session.get('token')
    if not token:
        return False, "token not found"
    try:
        session['user'] = jwt.decode(token, SECRET_KEY)
    except Exception as e:
        return False, "token is broken - %s" % str(e)
    return True, "token is ok! session['user']"


def user_power_lvl_check(min_power_lvl):
    if not session.get('user')['id']:
        raise Exception('Not logged in')
    user = db.session.query(User).filter(User.id == session.get('user')['id']).first()
    if int(user.power) < min_power_lvl:
        return False
    return True


def api_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token_check_result, token_check_message = request_token_check()
        if not token_check_result:
            logger.warning(
                '%s/%s Problem with token! tried to access "%s" - %s' % (
                    request.remote_addr,
                    request.headers['X-Forwarded-For'] if 'X-Forwarded-For' in request.headers else "-",
                    str(f.__name__),
                    token_check_message
                )
            )
            return {'message': token_check_message}, 403
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not user_power_lvl_check(10):
            logger.warning(
                '%s/%s Non admin tried to access "%s" - Username: %s' % (
                    request.remote_addr,
                    request.headers['X-Forwarded-For'] if 'X-Forwarded-For' in request.headers else "-",
                    str(f.__name__),
                    session.get('user')['username']
                )
            )
            return {'message': 'You have no power here! (not admin)'}, 403
        return f(*args, **kwargs)
    return decorated


def decode_token(token):
    try:
        return jwt.decode(token, SECRET_KEY)
    except Exception as e:
        return None


class MemoizedTTL(object):
    """Decorator that caches a function's return value each time it is called within a TTL
    If called within the TTL and the same arguments, the cached value is returned,
    If called outside the TTL or a different value, a fresh value is returned.
    """
    def __init__(self, ttl):
        self.cache = {}
        self.ttl = ttl

    def __call__(self, f):
        def wrapped_f(*args):
            now = time.time()
            try:
                value, last_update = self.cache[args]
                if 0 < self.ttl < now - last_update:
                    raise AttributeError
                return value
            except (KeyError, AttributeError):
                value = f(*args)
                self.cache[args] = (value, now)
                return value
            except TypeError:
                return f(*args)

        return wrapped_f
