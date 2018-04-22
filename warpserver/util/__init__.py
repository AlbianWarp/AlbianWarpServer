import jwt

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
