import os
import logging

from flask import Flask, jsonify
from flask_sockets import Sockets

from warpserver.model.base import db

logger = logging.getLogger('albianwarp')
logger.setLevel(logging.DEBUG)

from warpserver.sockets import ws_list, refresh_ws_list, consumer
from warpserver.pages import register_page_blueprint, home_page_blueprint, tos_page_blueprint, pp_page_blueprint, client_downloads_page_blueprint


app = Flask(__name__)
config_path = os.path.dirname(os.path.abspath(__file__))
app.config.from_pyfile(os.path.join(config_path, "config.py"))
db.init_app(app)
db.app = app
db.create_all()
sockets = Sockets(app)

app.register_blueprint(register_page_blueprint)
app.register_blueprint(home_page_blueprint)
app.register_blueprint(tos_page_blueprint)
app.register_blueprint(pp_page_blueprint)
app.register_blueprint(client_downloads_page_blueprint)

@app.route("/who_is_online")
def who_is_online():
    refresh_ws_list()
    return jsonify(list(ws_list))


@sockets.route('/ws')
def echo_socket(ws):
    while not ws.closed:
        message = ws.receive()
        if message:
            consumer(message, ws)


@app.route("/version")
def version():
    return "beta baboon"


from warpserver.route.auth import auth_blueprint

app.register_blueprint(auth_blueprint)

from warpserver.route.user import user_blueprint

app.register_blueprint(user_blueprint)

from warpserver.route.message import message_blueprint

app.register_blueprint(message_blueprint)

from warpserver.route.creature import creature_blueprint

app.register_blueprint(creature_blueprint)

