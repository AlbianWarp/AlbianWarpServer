from flask import request
from flask_restful import Resource

from warpserver.model import User
from warpserver.model.base import db
from warpserver.server import logger
from warpserver.util import api_token_required, admin_required
from warpserver.sockets import ws_list, refresh_ws_list


class UserListResource(Resource):
    """Docstring"""

    @api_token_required
    def get(self):
        refresh_ws_list()
        tmp = list()
        for user in User.query:
            online_status = "offline"
            try:
                _ = ws_list[user.username]
                online_status = "online"
            except KeyError:
                online_status = "offline"
            finally:
                tmp.append((user.username, online_status))
        return tmp

    def post(self):
        data = request.json
        if any(key not in data for key in ['username', 'password', 'email']):
            return {"message": "bad request"}, 400
        user = db.session.query(User).filter(User.username == data['username']).first()
        if user:
            return {"message": "user already exists"}, 409
        user = User(username=data['username'], password=data['password'], email=data['email'])
        db.session.add(user)
        db.session.commit()
        logger.info("user %s created" % data['username'])
        return {"message": "user successfully created"}, 200


class UserResource(Resource):
    """Docstring"""

    def get(self, user_id):
        user = db.session.query(User).filter(User.id == user_id).first()
        if not user:
            return {"message": "user does not exist"}, 404
        return user.to_dict(), 200

    @api_token_required
    @admin_required
    def delete(self, user_id):
        user = db.session.query(User).filter(User.id == user_id).first()
        if not user:
            return {"message": "user does not exist"}, 404
        db.session.delete(user)
        db.session.commit()
        return {"message": "successfully deleted user %s" % user.id}, 200


