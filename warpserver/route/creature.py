from flask import Blueprint
from flask_restful import Api

from warpserver.resource.creature import CreatureResource, CreatureListResource

creature_blueprint = Blueprint('creature', __name__)
creature_blueprint_api = Api(creature_blueprint)


creature_blueprint_api.add_resource(CreatureListResource, '/creature')
creature_blueprint_api.add_resource(CreatureResource, '/creature/<int:creature_id>')
