from warpserver.server import app
from warpserver.config import PORT, HOST, DEBUG

if __name__ == '__main__':
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer((HOST, PORT), app, handler_class=WebSocketHandler)
    server.serve_forever()
