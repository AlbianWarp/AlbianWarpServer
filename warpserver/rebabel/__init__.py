import random
import socketserver
import threading
from threading import Thread
from socket import SHUT_RDWR, timeout

from warpserver.model import User
from warpserver.model.base import db
from warpserver.config import REBABEL_PORT, REBABEL_CONFIG_HOST, REBABEL_HOST ,REBABEL_SERVER_NAME

# Config

echo_load = "40524b28eb000000"

server_ehlo = {"host": REBABEL_CONFIG_HOST, "port": REBABEL_PORT, "name": REBABEL_SERVER_NAME}

requests = {}
threads = {}

BUFSIZ = 1024


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    """
    The RequestHandler class for our server.
    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    def handle(self):
        print(f"{self.request.gettimeout()}")
        data = self.request.recv(BUFSIZ)
        if data[0:4] == bytes.fromhex("25000000"):
            reply, self.user_id = net_line_reply_package(data)
            self.request.sendall(reply)
            if self.user_id is not None:
                self.session_run = True
            else:
                return
        else:
            print(f"Whatever that was, It was not a 'NET: LINE' Request! Bye Bye! ;)")
            return
        requests[self.user_id] = self
        threads[self.user_id] = threading.current_thread()
        excess_data = None
        while self.session_run:
            if excess_data:
                print(f"Oh boy! found some excess Data, handling that instead of a `self.request.recv(1024)`")
                data = excess_data
                excess_data = None
                print(f"{self.user_id}> DATA {len(data)} : {data.hex()}")
            else:
                try:
                    data = self.request.recv(BUFSIZ)
                except ConnectionResetError as exception:
                    print(f"{self.user_id} BREAK, {exception}")
                    break
            if not data:
                print(f"{self.user_id} BREAK, NODATA")
                break
            if data[0:4].hex() in [
                "13000000",
                "18000000",
                "21020000",
                "21030000",
                "0f000000",
                "10000000",
                "09000000",
            ]:
                pass
            else:
                print(f"{self.user_id}> \033[91m{data.hex()}\033[00m")
            if data[0:4] == bytes.fromhex("13000000"):  # NET: ULIN
                reply, ulin_user_id, ulin_online_status = net_ulin_reply_package(data)
                print(
                    f"{self.user_id}> NET: ULIN, User Online status request for UserID {ulin_user_id}, user online status: {ulin_online_status}."
                )
                self.request.sendall(reply)
                if len(data) > 32:
                    excess_data = data[32:]
            elif data[0:4] == bytes.fromhex("18000000"):  # NET: STAT
                reply = net_stat_reply_package(data)
                print(f"{self.user_id}> NET: STAT, Request.")
                self.request.sendall(reply)
            elif data[0:4] == bytes.fromhex("21020000"):  # NET: RUSO
                reply, random_user_id, random_user_hid = net_ruso_reply_package(data)
                print(
                    f"{self.user_id}> NET: RUSO, Requested Random online UserID, got: {random_user_id}+{random_user_hid}"
                )
                self.request.sendall(reply)
            elif data[0:4] == bytes.fromhex("0f000000"):  # NET: UNIK
                (
                    reply,
                    unik_username,
                    unik_user_id,
                    unik_user_hid,
                ) = net_unik_reply_package(data)
                print(
                    f"{self.user_id}> NET: UNIK, Requested screenname of UserID: {unik_user_id}+{unik_user_hid}: {unik_username}"
                )
                self.request.sendall(reply)
            elif data[0:4] == bytes.fromhex("10000000"):
                user_id = int.from_bytes(data[12:16], byteorder="little")
                user_hid = int.from_bytes(data[16:18], byteorder="little")
                reply, user_status_online_status = user_status_package(
                    user_id=user_id, user_hid=user_hid
                )
                print(
                    f"{self.user_id}> USER_STATUS, Requested User online status of UserID: {user_id}+{user_hid}:  user online status: {user_status_online_status}."
                )
                self.request.sendall(reply)
                if len(data) > 32:
                    excess_data = data[32:]
            elif data[0:4] == bytes.fromhex("21030000"):
                self.request.sendall(data[0:24] + bytes.fromhex("0000000000000000"))
                print(
                    f"{self.user_id}> CREA HIST, Acknowledged a Creatures History package."
                )
            elif data[0:4] == bytes.fromhex("09000000"):  # PRAY Data
                pray_data_corrupted = False
                raw_pray = data[76:]
                pld_len = int.from_bytes(data[24:28], byteorder="little")
                print(f"{self.user_id}> PRAY, incoming data, pld_len: {pld_len}")
                assembly_required = True
                if pld_len == len(data[32:]) - 8:
                    print(f"{self.user_id}> PRAY, no assembly required.")
                    assembly_required = False
                else:
                    print(f"{self.user_id}> PRAY, assembling chunks...")
                while assembly_required:
                    payr_data_chunk = self.request.recv(BUFSIZ)
                    if not payr_data_chunk:
                        print(f"{self.user_id}> ERROR: PRAY CONN BROKE!!!!")
                        assembly_required = False
                    raw_pray = raw_pray + payr_data_chunk
                    data = data[:76] + raw_pray
                    if pld_len == len(data[32:]) - 8:
                        assembly_required = False
                        print(f"{self.user_id}> PRAY, chunks assembled!")
                    elif pld_len <= len(data[32:]) - 8:
                        assembly_required = False
                        pray_data_corrupted = False # todo: We might actually want to check this. Which could be done via the "prayer" library.
                        print(f"{self.user_id}> PRAY, \033[91mWHOOPS, Got to much data there!\033[00m")
                        print(f"{self.user_id}> PRAY, expected length: {pld_len} actual length {len(data[32:]) - 8}, Data lenght: {len(data)}")
                        excess_data = data[(pld_len + 40):]
                        print(f"{self.user_id}> EXCESS DATA {len(excess_data)} : {excess_data.hex()}")
                        data = data[:(pld_len + 40)]
                if not pray_data_corrupted:
                    user_id = data[32:36]
                    pld_len = 36 + len(raw_pray)

                    reply = (
                        bytes.fromhex(
                            f"090000000000000000000000000000000000000000000000{pld_len.to_bytes(4,byteorder='little').hex()}00000000{pld_len.to_bytes(4,byteorder='little').hex()}0100cccc{self.user_id.to_bytes(4,byteorder='little').hex()}{(pld_len - 24).to_bytes(4, byteorder='little').hex()}00000000010000000c0000000000000000000000"
                        )
                        + raw_pray
                    )
                    print(f"{self.user_id}> PRAY, done")
                    try:
                        requests[int.from_bytes(user_id, byteorder="little")].request.settimeout(10)
                        requests[int.from_bytes(user_id, byteorder="little")].request.sendall(
                            reply
                        )
                        requests[int.from_bytes(user_id, byteorder="little")].request.settimeout(None)
                    except KeyError as e:
                        print(f"{self.user_id}> PRAY, ERROR! The Recipient user with ID {int.from_bytes(user_id, byteorder='little')} is not online!")
                        # todo: So what now... the recipient user is not online, shall we just throw away the PRAY ?
                    except timeout as e:
                        print(f"{self.user_id}> PRAY, ERROR! The Recipient user with ID {int.from_bytes(user_id, byteorder='little')} did not respond in Time!")
                        raise e
                    except Exception as e:
                        print(f"{self.user_id}> PRAY, ERROR! Could not send data to recipient. {int.from_bytes(user_id, byteorder='little')}, {str(e)} {type(e)}")
                        raise e
        requests.pop(self.user_id, None)
        print(f" removed {self.user_id} from requests")

    def finish(self):
        requests.pop(self.user_id, None)
        print(f"FINISH! removed {self.user_id} from requests")


def net_line_reply_package(line_request_package):
    package_count = int.from_bytes(line_request_package[20:24], byteorder="little")
    username_len = int.from_bytes(line_request_package[44:48], byteorder="little")
    username = line_request_package[52 : 52 + username_len - 1].decode("latin-1")
    password_len = int.from_bytes(line_request_package[48:52], byteorder="little")
    password = line_request_package[
        52 + username_len : 52 + username_len + password_len - 1
    ].decode("latin-1")
    user = db.session.query(User).filter(User.username == username).first()
    db.session.close()
    if not user or not user.check_password(password):
        print("message: username or password incorrect")
        return (
            bytes.fromhex(
                f"0a00000000000000000000000000000000000000{package_count.to_bytes(4, byteorder='little').hex()}000000000000000000000000000000000000000000000000000000000000000000000000"
            ),
            None,
        )
    user_hid = 1
    print(f"{username} has joined!")
    return (
        bytes.fromhex(
            f"0a000000{echo_load}{user.id.to_bytes(4, byteorder='little').hex()}{user_hid.to_bytes(2,byteorder='little').hex()}0a00{package_count.to_bytes(4, byteorder='little').hex()}0000000000000000"
            + f"00000000"
            + f"01000000"
            + f"00000000"
            + (len(server_ehlo["host"]) + len(server_ehlo["name"]) + 22)
            .to_bytes(4, byteorder="little")
            .hex()
            + f"01000000"
            + f"01000000"
            + f"01000000"
            + server_ehlo["port"].to_bytes(4, byteorder="little").hex()
            + f"01000000"
            + server_ehlo["host"].encode("latin-1").hex()
            + f"00"
            + server_ehlo["name"].encode("latin-1").hex()
            + f"00"
        ),
        user.id,
    )


def net_ulin_reply_package(ulin_request_package):
    requested_user_id = int.from_bytes(ulin_request_package[12:16], byteorder="little")
    package_count = int.from_bytes(ulin_request_package[20:24], byteorder="little")
    package_count_hex = package_count.to_bytes(4, byteorder="little").hex()
    if requested_user_id in requests or requested_user_id == 0:
        return (
            bytes.fromhex(
                f"13000000{echo_load}0000000000000000{package_count_hex}000000000a000000"
            ),
            requested_user_id,
            True,
        )
    else:
        return (
            bytes.fromhex(
                f"1300000000000000000000000000000000000000{package_count_hex}0000000000000000"
            ),
            requested_user_id,
            False,
        )


def net_stat_reply_package(stat_request_package):
    """This whole thing is a mock, all the date, asside from the Online player count, returned by this is nonsense ;)"""
    package_count = int.from_bytes(stat_request_package[20:24], byteorder="little")
    bytes_received = (12345).to_bytes(4, byteorder="little").hex()
    bytes_sent = (54321).to_bytes(4, byteorder="little").hex()
    player_online = (len(requests)).to_bytes(4, byteorder="little").hex()
    mil_seconds_online = (10602856).to_bytes(4, byteorder="little").hex()
    return bytes.fromhex(
        "1800000000000000000000000000000000000000"
        + package_count.to_bytes(4, byteorder="little").hex()
        + "0000000000000000"
        + mil_seconds_online
        + player_online
        + bytes_sent
        + bytes_received
    )


def net_ruso_reply_package(ruso_request_package):
    package_count = int.from_bytes(ruso_request_package[20:24], byteorder="little")
    package_count_hex = package_count.to_bytes(4, byteorder="little").hex()
    random_user_id = random.choice(list(requests))
    random_user_hid = 1
    return (
        bytes.fromhex(
            f"21020000{echo_load}{random_user_id.to_bytes(4, byteorder='little').hex()}{random_user_hid.to_bytes(2,byteorder='little').hex()}0a00{package_count_hex}0000000001000000"
        ),
        random_user_id,
        random_user_hid,
    )


def net_unik_reply_package(unik_request_package):
    package_count_hex = unik_request_package[20:24].hex()
    user_id = int.from_bytes(unik_request_package[12:16], byteorder="little")
    user_id_hex = unik_request_package[12:16].hex()
    user_hid = int.from_bytes(unik_request_package[16:18], byteorder="little")
    username = None
    user = db.session.query(User).filter(User.id == user_id).first()
    db.session.close()
    if user:
        username = user.username
        username_hex = username.encode("latin-1").hex()
        username_len_hex = len(username).to_bytes(4, byteorder="little").hex()
    payld_len = 34 + len(username)
    if username is None:
        print(
            f"ERROR: UNIK Requested User does Not exist!!!!"
        )  # todo: so what happens if a requested user does not exist?
    if username is not None:
        reply = (
            bytes.fromhex(
                f"0f000000{echo_load}{user_id_hex}{unik_request_package[16:18].hex()}0000{package_count_hex}{payld_len.to_bytes(4, byteorder='little').hex()}00000000{payld_len.to_bytes(4, byteorder='little').hex()}{user_id_hex}0b00cccc0500000005000000{username_len_hex}48617070794d65696c69{username_hex}"
            ),
            username,
            user_id,
            user_hid,
        )
    return reply


def user_status_package(user_id, user_hid=1):
    username = "NONE"
    user = db.session.query(User).filter(User.id == user_id).first()
    db.session.close()
    if user_id == 0 or not user:
        payld_len = 34 + len(username)
        if not user:
            print(
                f"ERROR - user_status_package: A User that is not in the database was requested!"
            )
        return (
            bytes.fromhex(
                f"0e0000000000000000000000{user_id.to_bytes(4, byteorder='little').hex()}{user_hid.to_bytes(2, byteorder='little').hex()}0a0000000000{payld_len.to_bytes(4, byteorder='little').hex()}00000000{payld_len.to_bytes(4, byteorder='little').hex()}{user_id.to_bytes(4, byteorder='little').hex()}{user_hid.to_bytes(2, byteorder='little').hex()}cccc0500000005000000{len(username).to_bytes(4, byteorder='little').hex()}48617070794d65696c69{username.encode('latin-1').hex()}"
            ),
            False,
        )
    username = user.username
    payld_len = 34 + len(username)
    if user_id in requests or user_id == 0:
        reply, online_status = (
            bytes.fromhex(
                f"0d0000000000000000000000{user_id.to_bytes(4, byteorder='little').hex()}{user_hid.to_bytes(2,byteorder='little').hex()}000000000000{payld_len.to_bytes(4, byteorder='little').hex()}00000000{payld_len.to_bytes(4, byteorder='little').hex()}{user_id.to_bytes(4, byteorder='little').hex()}{user_hid.to_bytes(2,byteorder='little').hex()}cccc0500000005000000{len(username).to_bytes(4, byteorder='little').hex()}48617070794d65696c69{username.encode('latin-1').hex()}"
            ),
            True,
        )
        print(f"{user_id}+{user_hid} is online")
    else:
        reply, online_status = (
            bytes.fromhex(
                f"0e0000000000000000000000{user_id.to_bytes(4, byteorder='little').hex()}{user_hid.to_bytes(2,byteorder='little').hex()}0a0000000000{payld_len.to_bytes(4, byteorder='little').hex()}00000000{payld_len.to_bytes(4, byteorder='little').hex()}{user_id.to_bytes(4, byteorder='little').hex()}{user_hid.to_bytes(2,byteorder='little').hex()}cccc0500000005000000{len(username).to_bytes(4, byteorder='little').hex()}48617070794d65696c69{username.encode('latin-1').hex()}"
            ),
            False,
        )
        print(f"{user_id}+{user_hid} is offline")
    return reply, online_status


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


ThreadedTCPServer.allow_reuse_address = True
server = ThreadedTCPServer((REBABEL_HOST, REBABEL_PORT), ThreadedTCPRequestHandler)
ip, port = server.server_address

# Start a thread with the server -- that thread will then start one
# more thread for each request
server_thread = Thread(target=server.serve_forever)
