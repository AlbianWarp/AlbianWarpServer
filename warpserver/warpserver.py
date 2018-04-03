import os
from uuid import uuid4
from flask import Flask, request, send_file
from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource, Api, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
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
    return """
<form name="register_form"  method="POST">
email: <input type="text" name="email">
<br /> username: <input type="text" name="username">
<br /> password: <input type="password" name="password">
<br /> <input type="submit" value="Submit">
</form>'
"""



@app.route('/creature_upload', methods=['GET', 'POST'])
@auth.login_required
def upload_creature_form():
    if request.method == 'POST':
        f = request.files['file']
        uuid = str(uuid4())
        f.save(os.path.join(config.UPLOAD_FOLDER, "creatures", "%s_%s" % (uuid, secure_filename(f.filename))))
        recipient = request.form['recipient']
        creature_name = request.form['creature_name']
        print('got creature "%s" for user "%s"' % (creature_name, recipient))
        sender_user = db.session.query(models.User).filter(models.User.username == auth.username()).first()
        print(sender_user.username)
        recipient_user = db.session.query(models.User).filter(models.User.username == recipient).first()
        creature = models.Creature(creature_name, secure_filename(f.filename), sender_user, recipient_user)
        db.session.add(creature)
        db.session.commit()
        return 'file uploaded successfully'
    elif request.method == 'GET':
        return """
<form action = "/creature_upload" method = "POST" enctype = "multipart/form-data">
recipient: <input type="text" name="recipient">
<br />creature name: <input type="text" name="creature_name">
<br />creature file: <input type = "file" name = "file" />
<br /><input type = "submit" />
</form>
"""


@app.route('/creature/<int:creature_id>', methods=['GET','DELETE'])
@auth.login_required
def creature(creature_id):
    auth_user = db.session.query(models.User).filter(models.User.username == auth.username()).first()
    creature = db.session.query(models.Creature).filter(models.Creature.id == creature_id and models.Creature.recipient_user_id == auth_user.id)
    if request.method == 'GET':
        filename = os.path.join(config.UPLOAD_FOLDER, "creatures", "%s_%s" % (creature.uuid, creature.filename))
        return send_file(filename,attachment_filename="%s_%s" % (creature.uuid, creature.filename))
    elif request.method == 'DELETE':
        db.session.delete(creature)
        db.session.commit()
        return "creature deleted", 200


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
        sender_user = db.session.query(models.User).filter(models.User.username == auth.username()).first()
        recipient_user = db.session.query(models.User).filter(models.User.username == data['aw_recipient']).first()
        if recipient_user == None:
            abort(404)
        message = models.Message(recipient=recipient_user, sender=sender_user, data=json.dumps(data))
        db.session.add(message)
        db.session.commit()
        return {"message": "direct message successfully added"}, 200


class Creatures(Resource):

    @auth.login_required
    def get(self):
        auth_user = db.session.query(models.User).filter(models.User.username == auth.username()).first()
        creatures = db.session.query(models.Creature).filter(models.Creature.recipient_user_id == auth_user.id)
        creature_ids = []
        for creature in creatures:
            creature_ids.append({ "id": creature.id,
                                "filename": "%s_%s" % (creature.uuid, creature.filename)})
        return {"creatures": creature_ids}


class Message(Resource):
    @auth.login_required
    def get(self, message_id):
        auth_user = db.session.query(models.User).filter(models.User.username == auth.username()).first()
        message = db.session.query(models.Message).filter(
            models.Message.recipient_user_id == auth_user.id and models.Message.id == message_id).first()
        data = json.loads(message.data)
        data['aw_sender'] = message.sender.username
        data['aw_date'] = message.sender.created.strftime('%Y%m%d%H%M%S')
        del data['aw_recipient']
        return data

    @auth.login_required
    def delete(self, message_id):
        auth_user = db.session.query(models.User).filter(models.User.username == auth.username()).first()
        message = db.session.query(models.Message).filter(
            models.Message.recipient_user_id == auth_user.id and models.Message.id == message_id).first()
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
api.add_resource(Creatures, '/creatures')
