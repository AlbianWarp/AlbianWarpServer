import os

from uuid import uuid4
from flask import session, request, send_file
from flask_restful import Resource

from warpserver.server import logger
from warpserver.config import UPLOAD_FOLDER
from warpserver.model import Creature, User
from warpserver.model.base import db
from warpserver.util import api_token_required
from werkzeug.utils import secure_filename


class CreatureListResource(Resource):

    @api_token_required
    def get(self):
        creatures = db.session.query(Creature).filter(Creature.recipient_user_id == session['user']['id'])
        creature_ids = []
        for creature in creatures:
            creature_ids.append({"id": creature.id,
                                 "filename": "%s_%s" % (creature.uuid, creature.filename)})
        return {"creatures": [creature.to_dict() for creature in creatures]}

    @api_token_required
    def post(self):
        if any(key not in request.files for key in ['file']):
            return {"message": "bad request"}, 400
        if any(key not in request.form for key in ['creature_name', 'recipient']):
            return {"message": "bad request"}, 400
        f = request.files['file']
        creature_name = request.form['creature_name']
        recipient = request.form['recipient']
        recipient_user = db.session.query(User).filter(User.username == recipient).first()
        if not recipient_user:
            return {"message": "recipient user not found"}, 404
        sender_user = db.session.query(User).filter(User.id == session['user']['id']).first()
        uuid = str(uuid4())
        file_path = os.path.join(UPLOAD_FOLDER, "creatures", "%s_%s" % (uuid, secure_filename(f.filename)))
        try:
            f.save(file_path)
            logger.debug('saved creature "%s" for user "%s in %s"' % (creature_name, recipient, file_path))
        except Exception as e:
            logger.error("Failed to safe File %s - %s" % (file_path, e))
            return {"message": e}, 500
        try:
            creature = Creature(creature_name, secure_filename(f.filename), sender_user, recipient_user, uuid)
            db.session.add(creature)
            db.session.commit()
            logger.info(
                'Creature "%s" successfully sent from %s to %s' % (
                    creature_name,
                    sender_user.username,
                    recipient
                )
            )
        except Exception as e:
            logger.error('Failed to save creature "%s" to Database. %s' % (f.filename, e))
            return {"message": e}, 500


class CreatureResource(Resource):
    """Docstring"""

    @api_token_required
    def get(self, creature_id):
        creature = db.session.query(Creature).filter(
            Creature.id == creature_id
            and Creature.recipient_user_id == session['user']['id']).first()
        if not creature:
            return {"message": "creature not found"}, 404
        file_path = os.path.join(UPLOAD_FOLDER, "creatures", "%s_%s" % (creature.uuid, creature.filename))
        return send_file(file_path, attachment_filename="%s_%s" % (creature.uuid, creature.filename))

    @api_token_required
    def delete(self, creature_id):
        creature = db.session.query(Creature).filter(
            Creature.id == creature_id
            and Creature.recipient_user_id == session['user']['id']).first()
        if not creature:
            return {"message": "creature not found"}, 404
        db.session.delete(creature)
        db.session.commit()
        return "creature deleted", 200
