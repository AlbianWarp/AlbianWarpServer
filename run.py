import os

from warpserver.server import app
from warpserver.config import PORT, HOST, UPLOAD_FOLDER

if not os.path.exists(os.path.join(UPLOAD_FOLDER, "creatures")):
    os.makedirs(os.path.join(UPLOAD_FOLDER, "creatures"))

if __name__ == '__main__':
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer((HOST, PORT), app, handler_class=WebSocketHandler)
    server.serve_forever()
