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
    print('sending message to user: %s %s' % (user, message))
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
            print('Handling auth request')
            user = decode_token(data['auth'])
            if user:
                ws_list[user['username']] = ws
                ws.send(json.dumps({"auth": True}))
                print('that worked out, token is okey dokey')
            else:
                ws.send(json.dumps({"auth": False}))
                print('Nope no auth to you, token is broken!')
        elif check_auth(ws) and "aw_recipient" in data:
            print('Handling RTDMA')
            data['aw_sender'] = check_auth(ws)
            print('1')
            del data['aw_recipient']
            print('2')
            data['aw_date'] = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            print('3')
            send_to_user(data['aw_recipient'], json.dumps(data))

    except json.JSONDecodeError as e:
        print("NOT JSON! %s" % e)
    except Exception as e:
        raise e
