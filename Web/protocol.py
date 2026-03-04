import os
import socket
import json

class Protocol:
    #Color terminal Codes
    GREEN = '\033[32m'
    RED = '\033[31m'
    RESET = '\033[0m'

    #Protocol codes
    HANDSHAKE = "HANDSHAKE"
    SEND_MSG = "SEND_MSG"
    APPOINT_MANAGER = "APPOINT_MANAGER"
    DEMOTE_MANAGER = "DEMOTE_MANAGER"
    MUTE = "MUTE"
    UNMUTE = "UNMUTE"
    BROADCAST = "BROADCAST"
    PRIVATE = "PRIVATE"
    KICK = "KICK"
    GET_USERS = "GETUSRS"
    GIDEON = "GIDEON"


    @staticmethod
    def parse_command(cmd: str):
        l = [""]
        i = 0
        cmd_index = 0
        opened_quotes = False
        while len(cmd) > cmd_index:
            if cmd[cmd_index] == " " and not opened_quotes:
                i += 1
                l.append("")
                cmd_index += 1
                continue
            if cmd[cmd_index] in ["'", '"']:
                opened_quotes = not opened_quotes
                cmd_index += 1
                continue
            l[i] += cmd[cmd_index]
            cmd_index += 1
        return l

    @staticmethod
    def create_msg(data: bytes) -> bytes:
        len_data = len(data)
        l = Protocol.convert_base(len_data, 256)
        if len(l) > 4: raise Exception(f"Data {data} is too big to send in one packet!")
        for _ in range(4 - len(l)):
            l.insert(0, 0)
        prepending_bytes = b"".join([l[i].to_bytes(1, "little") for i in range(4)])
        return prepending_bytes + data

    @staticmethod
    def get_msg(working_socket: socket.socket):
        prepending_bytes = working_socket.recv(4)
        l = [b for b in prepending_bytes]
        len_of_msg = Protocol.convert_to_base10(l, 256)
        return working_socket.recv(len_of_msg)


    @staticmethod
    def convert_base(n, b):
        if n == 0:
            return [0]
        digits = []
        while n:
            digits.append(int(n % b))
            n //= b
        return digits[::-1]

    @staticmethod
    def convert_to_base10(n, b):
        s = 0
        n.reverse()
        for p in range(len(n)):
            s += n[p] * pow(b, p)
        return s


    @staticmethod
    def send_file(working_socket: socket.socket, file_path: str):
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                b = f.read()
            working_socket.send(Protocol.create_msg(str(len(b)).encode()))
            working_socket.sendall(b)
        else:
            working_socket.send(Protocol.create_msg(b"Failed to send!"))

    @staticmethod
    def recv_file(working_socket: socket.socket):
        size = int(Protocol.get_msg(working_socket).decode())
        s = 0
        b = b""
        while s < size:
            data = working_socket.recv(size)
            b += data
            s += len(data)
        return b

    @staticmethod
    def broadcast(msg, clients: set):
        for client in clients:
            try:
                Protocol.send_command(client.soc, MSG=msg, COMMAND=Protocol.BROADCAST)
            except Exception as e:
                print(e)



    @staticmethod
    def send_command(sock: socket.socket, **kwargs):
        data = json.dumps(kwargs).encode()
        sock.send(Protocol.create_msg(data))

    @staticmethod
    def recv_command(sock):
        data = Protocol.get_msg(sock)
        return json.loads(data.decode())
