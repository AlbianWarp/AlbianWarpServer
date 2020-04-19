from flask import Blueprint
from flask_restful import Api

from warpserver.resource.user import UserListResource, UserResource

user_blueprint = Blueprint("user", __name__)
user_blueprint_api = Api(user_blueprint)


user_blueprint_api.add_resource(UserListResource, "/user")
user_blueprint_api.add_resource(UserResource, "/user/<int:user_id>")
