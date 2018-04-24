from flask import Blueprint
from flask_restful import Api

from warpserver.resource.auth import AuthResource

auth_blueprint = Blueprint('auth', __name__)
auth_blueprint_api = Api(auth_blueprint)


auth_blueprint_api.add_resource(AuthResource, '/auth')

