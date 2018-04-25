from flask import Blueprint
from flask_restful import Api

from warpserver.resource.message import MessageResource, MessageListResource

message_blueprint = Blueprint('message', __name__)
message_blueprint_api = Api(message_blueprint)

message_blueprint_api.add_resource(MessageListResource, '/message')
message_blueprint_api.add_resource(MessageResource, '/message/<int:message_id>')
