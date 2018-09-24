import json

from flask import session, request
from flask_restful import Resource

from warpserver.model import User, Message
from warpserver.model.base import db
from warpserver.util import api_token_required


class MessageListResource(Resource):
    """Docstring"""

    @api_token_required
    def get(self):
        messages = db.session.query(Message).filter(Message.recipient_user_id == session['user']['id'])
        return {"messages": [message.id for message in messages]}

    @api_token_required
    def post(self):
        data = request.json
        if any(key not in data for key in ['aw_recipient']):
            return {"message": "bad request"}, 400
        sender_user = db.session.query(User).filter(User.id == session['user']['id']).first()
        recipient_user = db.session.query(User).filter(User.username == data['aw_recipient']).first()
        if recipient_user is None:
            return {"message": "recipient user not found"}, 404
        message = Message(recipient=recipient_user, sender=sender_user, data=json.dumps(data))
        db.session.add(message)
        db.session.commit()
        return {"message": "direct message successfully added"}, 200


class MessageResource(Resource):
    """Docstring"""

    @api_token_required
    def get(self, message_id):
        message = db.session.query(Message).filter(
            Message.recipient_user_id == session['user']['id']
            and Message.id == message_id).first()
        if not message:
            return {"message": "message not found"}, 404
        data = json.loads(message.data)
        data['aw_sender'] = message.sender.username
        data['aw_date'] = message.sender.date_created.strftime('%Y%m%d%H%M%S')
        del data['aw_recipient']
        return data

    @api_token_required
    def delete(self, message_id):
        message = db.session.query(Message).filter(
            Message.recipient_user_id == session['user']['id']
            and Message.id == message_id).first()
        if not message:
            return {"message": "message not found"}, 404
        db.session.delete(message)
        db.session.commit()
        return {"message": "successfully deleted message %s" % message.id}, 200
