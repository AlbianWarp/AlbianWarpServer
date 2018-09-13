import jwt

import time
from functools import wraps
from flask import request, session

from warpserver.server import logger
from warpserver.config import SECRET_KEY


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('token')
        if not token:
            logger.warning(
                '%s/%s tried to access "%s" without a token!' % (
                    request.remote_addr,
                    request.headers['X-Forwarded-For'] if 'X-Forwarded-For' in request.headers else "-",
                    str(f.__name__)
                )
            )
            return {'message': 'token not found'}, 403
        try:
            session['user'] = jwt.decode(token, SECRET_KEY)
        except Exception as e:
            logger.error(
                '%s/%s tried to access "%s" with a broken token! %s' % (
                    request.remote_addr,
                    request.headers['X-Forwarded-For'] if 'X-Forwarded-For' in request.headers else "-",
                    str(f.__name__),
                    str(e)
                )
            )
            return {'message': 'token is broken'}, 403
        return f(*args, **kwargs)

    return decorated


def decode_token(token):
    try:
        return jwt.decode(token, SECRET_KEY)
    except Exception as e:
        return None


class memoized_ttl(object):
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