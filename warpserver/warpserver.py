import os
import jwt
import datetime
from functools import wraps
from uuid import uuid4
from flask import Flask, request, send_file, jsonify, make_response, session
from flask_restful import Resource, Api, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import json
import logging

from . import models
from . import config

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
config_path = os.path.dirname(os.path.abspath(__file__))
app.config.from_pyfile(os.path.join(config_path, "config.py"))
api = Api(app)

db = SQLAlchemy(app)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('token')
        if not token:
            return jsonify({'message': 'token not found'}), 403
        try:
            session['user'] = jwt.decode(token, app.config['SECRET_KEY'])
        except Exception as e:
            print(e)
            return jsonify({'message': 'token is broken'}), 403
        return f(*args, **kwargs)

    return decorated


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


@app.route('/users')
@token_required
def users():
    tmp = []
    for user in db.session.query(models.User):
        tmp.append(user.username)
    return json.dumps(tmp)


@app.route('/creature_upload', methods=['GET', 'POST'])
@token_required
def upload_creature_form():
    if request.method == 'POST':
        f = request.files['file']
        uid = str(uuid4())
        f.save(os.path.join(config.UPLOAD_FOLDER, "creatures", "%s_%s" % (uid, secure_filename(f.filename))))
        recipient = request.form['recipient']
        creature_name = request.form['creature_name']
        print('got creature "%s" for user "%s"' % (creature_name, recipient))
        sender_user = db.session.query(models.User).filter(models.User.username == session['user']['username']).first()
        print(sender_user.username)
        recipient_user = db.session.query(models.User).filter(models.User.username == recipient).first()
        creature = models.Creature(creature_name, secure_filename(f.filename), sender_user, recipient_user, uid)
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


@app.route('/creature/<int:creature_id>', methods=['GET', 'DELETE'])
@token_required
def creature(creature_id):
    auth_user = db.session.query(models.User).filter(models.User.username == session['user']['username']).first()
    crea = db.session.query(models.Creature).filter(
        models.Creature.id == creature_id and models.Creature.recipient_user_id == auth_user.id).first()
    if request.method == 'GET':
        filename = os.path.join(config.UPLOAD_FOLDER, "creatures", "%s_%s" % (crea.uid, crea.filename))
        return send_file(filename, attachment_filename="%s_%s" % (crea.uid, crea.filename))
    elif request.method == 'DELETE':
        db.session.delete(crea)
        db.session.commit()
        return "creature deleted", 200


@app.route("/version")
def get_version():
    return config.AW_SERVER_VERSION, 200


class Messages(Resource):

    @token_required
    def get(self):
        auth_user = db.session.query(models.User).filter(models.User.username == session['user']['username']).first()
        messages = db.session.query(models.Message).filter(models.Message.recipient_user_id == auth_user.id)
        message_ids = []
        for message in messages:
            message_ids.append(message.id)
        return {"messages": message_ids}

    @token_required
    def post(self):
        data = request.json
        sender_user = db.session.query(models.User).filter(models.User.username == session['user']['username']).first()
        recipient_user = db.session.query(models.User).filter(models.User.username == data['aw_recipient']).first()
        if recipient_user is None:
            abort(404)
        message = models.Message(recipient=recipient_user, sender=sender_user, data=json.dumps(data))
        db.session.add(message)
        db.session.commit()
        return {"message": "direct message successfully added"}, 200


class Creatures(Resource):

    @token_required
    def get(self):
        auth_user = db.session.query(models.User).filter(models.User.username == session['user']['username']).first()
        creatures = db.session.query(models.Creature).filter(models.Creature.recipient_user_id == auth_user.id)
        creature_ids = []
        for creature in creatures:
            creature_ids.append({"id": creature.id,
                                 "filename": "%s_%s" % (creature.uid, creature.filename)})
        return {"creatures": creature_ids}


class Message(Resource):
    @token_required
    def get(self, message_id):
        auth_user = db.session.query(models.User).filter(models.User.username == session['user']['username']).first()
        message = db.session.query(models.Message).filter(
            models.Message.recipient_user_id == auth_user.id and models.Message.id == message_id).first()
        data = json.loads(message.data)
        data['aw_sender'] = message.sender.username
        data['aw_date'] = message.sender.created.strftime('%Y%m%d%H%M%S')
        del data['aw_recipient']
        return data

    @token_required
    def delete(self, message_id):
        auth_user = db.session.query(models.User).filter(models.User.username == session['user']['username']).first()
        message = db.session.query(models.Message).filter(
            models.Message.recipient_user_id == auth_user.id and models.Message.id == message_id).first()
        db.session.delete(message)
        db.session.commit()
        return {"message": "successfully deleted message %s" % message.id}


@app.route('/login')
def login():
    authorization = request.authorization
    user = (db.session.query(models.User).filter(models.User.username == authorization.username).first())
    if user is None:
        return make_response('User not found!', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})
    if user.check_password(authorization.password):
        token = jwt.encode(
            {'username': authorization.username,
             'exp': datetime.datetime.now() + datetime.timedelta(days=7)
             }, app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('UTF-8')})
    return make_response('Could not verify!', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})


def init_db():
    """Erase the tables (if exist) and create them anew."""
    models.Base.metadata.drop_all(bind=db.engine)
    models.Base.metadata.create_all(bind=db.engine)
    db.session.commit()


api.add_resource(Messages, '/messages')
api.add_resource(Message, '/message', '/message/<int:message_id>')
api.add_resource(Creatures, '/creatures')
