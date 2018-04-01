import os
from flask import Flask, request
from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource, Api, abort
from flask_sqlalchemy import SQLAlchemy
import json

from . import models
from . import config

app = Flask(__name__)
config_path = os.path.dirname(os.path.abspath(__file__))
app.config.from_pyfile(os.path.join(config_path, "config.py"))
api = Api(app)

db = SQLAlchemy(app)
auth = HTTPBasicAuth()


@app.route('/register', methods=['GET', 'POST'])
def register_form():
    if request.method == 'POST':
        user = db.session.query(models.User).filter(models.User.username == request.form['username']).first()
        if user:
            return '<h1>THAT USER ALREADY EXISTS!!!!</h1>', 409
        new_user = models.User(username=request.form['username'], password=request.form['password'],
                               email=request.form['email'])
        db.session.add(new_user)
        db.session.commit()
        return '<h1>USER CREATED!</h1>'
    return '<form name="register_form"  method="POST">email:<br><input type="text" name="email"><br>username:<br><input type="text" name="username"><br>password :<br><input type="password" name="password"><br><input type="submit" value="Submit"></form>'


@app.route("/version")
def get_version():
    return config.AW_SERVER_VERSION, 200


class Messages(Resource):

    @auth.login_required
    def get(self):
        auth_user = db.session.query(models.User).filter(models.User.username == auth.username()).first()
        messages = db.session.query(models.Message).filter(models.Message.recipient_user_id == auth_user.id)
        message_ids = []
        for message in messages:
            message_ids.append(message.id)
        return {"messages": message_ids}

    @auth.login_required
    def post(self):
        data = request.json
        recipient_user = db.session.query(models.User).filter(models.User.username == data['aw_recipient']).first()
        if recipient_user == None:
            abort(404)
        sender_user = db.session.query(models.User).filter(models.User.username == auth.username()).first()
        message = models.Message(recipient=recipient_user, sender=sender_user, data=json.dumps(data))
        db.session.add(message)
        db.session.commit()
        return {"message": "direct message successfully added"}, 200


class Message(Resource):
    @auth.login_required
    def get(self, message_id):
        auth_user = db.session.query(models.User).filter(models.User.username == auth.username()).first()
        message = db.session.query(models.Message).filter(models.Message.recipient_user_id == auth_user.id and models.Message.id == message_id).first()
        data = json.loads(message.data)
        data['aw_sender'] = message.sender.username
        data['aw_date'] = message.sender.created.strftime('%Y%m%d%H%M%S')
        del data['aw_recipient']
        return data

    def delete(self, message_id):
        auth_user = db.session.query(models.User).filter(models.User.username == auth.username()).first()
        message = db.session.query(models.Message).filter(models.Message.recipient_user_id == auth_user.id and models.Message.id == message_id).first()
        db.session.delete(message)
        db.session.commit()
        return {"message": "successfully deleted message %s" % message.id}


@auth.error_handler
def auth_error():
    abort(401, message="Unathorized")


@auth.verify_password
def get_password(username, password):
    result = (db.session.query(models.User).filter(models.User.username == username).first())
    if result is None:
        return False
    return result.check_password(password)


def init_db():
    """Erase the tables (if exist) and create them anew."""
    models.Base.metadata.drop_all(bind=db.engine)
    models.Base.metadata.create_all(bind=db.engine)
    db.session.commit()


api.add_resource(Messages, '/messages')
api.add_resource(Message, '/message', '/message/<int:message_id>')
