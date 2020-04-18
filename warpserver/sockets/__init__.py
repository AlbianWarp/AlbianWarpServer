import json
import datetime

from warpserver.util import decode_token
from geventwebsocket.exceptions import WebSocketError

ws_list = {}


def refresh_ws_list():
    dead_sockets = list()
    for user in ws_list:
        try:
            ws_list[user].send('{"ping":"0123456789"}')
        except WebSocketError:
            dead_sockets.append(user)
    for socket in dead_sockets:
        del ws_list[socket]


def check_auth(ws):
    for socket in ws_list:
        if ws_list[socket] is ws:
            return socket
    return None


def send_to_user(user, message):
    socket_dead_user = None
    for socket in ws_list.keys():
        if socket == user:
            try:
                ws_list[socket].send(message)
                return True
            except WebSocketError:
                socket_dead_user = user
    if socket_dead_user:
        del ws_list[socket_dead_user]
        return False


def consumer(message, ws):
    try:
        data = json.loads(message)
        if "auth" in data:
            user = decode_token(data["auth"])
            if user:
                ws_list[user["username"]] = ws
                print(user)
                ws.send(json.dumps({"auth": True}))
            else:
                ws.send(json.dumps({"auth": False}))
        elif check_auth(ws) and "aw_recipient" in data:
            recipient = data["aw_recipient"]
            data["aw_sender"] = check_auth(ws)
            del data["aw_recipient"]
            data["aw_date"] = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            send_to_user(recipient, json.dumps(data))
    except json.JSONDecodeError as e:
        print("NOT JSON! %s" % e)
    except Exception as e:
        raise e
