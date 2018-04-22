import os
import logging

from flask import Flask

from warpserver.model.base import db

logger = logging.getLogger('albianwarp')
logger.setLevel(logging.DEBUG)

app = Flask(__name__)
config_path = os.path.dirname(os.path.abspath(__file__))
app.config.from_pyfile(os.path.join(config_path, "config.py"))
db.init_app(app)
db.app = app

db.create_all()

from warpserver.route.auth import auth_blueprint

app.register_blueprint(auth_blueprint)

from warpserver.route.user import user_blueprint

app.register_blueprint(user_blueprint)

from warpserver.route.message import message_blueprint

app.register_blueprint(message_blueprint)