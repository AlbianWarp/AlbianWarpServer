import jwt

from flask import session, request
from flask_restful import Resource

from warpserver.model import User
from warpserver.model.base import db
from warpserver.server import logger
from warpserver.util import api_token_required, tokenize_user
from warpserver.config import SECRET_KEY


class AuthResource(Resource):
    """Docstring"""

    @api_token_required
    def get(self):
        return (
            db.session.query(User)
            .filter(User.id == session["user"]["id"])
            .first()
            .to_dict()
        )

    def post(self):
        data = request.json
        if any(key not in data for key in ["username", "password"]):
            return {"message": "bad request"}, 400
        user = db.session.query(User).filter(User.username == data["username"]).first()
        if not user.username == data["username"]:
            return {"message": "username is case sensitive!"}, 401
        if not user or not user.check_password(data["password"]):
            return {"message": "username or password false"}, 401
        logger.info("user %s token generated" % data["username"])
        return {"token": tokenize_user(user)}, 200
