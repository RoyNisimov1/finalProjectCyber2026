import os
import socket
import json

from AsymmetricEncryptions import ECPoint
from AsymmetricEncryptions.PublicPrivateKey.ECC import ECKey, ECDH, ECSchnorr, ECIES, EllipticCurveNISTP256
from Encryption.AESWrapper import AESWrapper
from base64 import b64encode, b64decode

class Protocol:
    #Color terminal Codes
    GREEN = '\033[32m'
    RED = '\033[31m'
    RESET = '\033[0m'

    #Encryption
    CURVE = EllipticCurveNISTP256.get_curve()
    DH1 = "DiffieHellman1"
    DHFin = "DiffieHellmanFin"

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
    def create_msg(data: bytes, key: bytes = b"", signKey=None) -> bytes:
        if len(key) != 0:
            data = AESWrapper.encrypt(key, data)
        if signKey is not None:
            signer = ECSchnorr(signKey)
            signature = signer.sign(data)
            d = {"SIG": (signature[0], signature[1].export()), "DATA": b64encode(data).decode()}
            data = json.dumps(d).encode()
        else:
            d = {"SIG": None, "DATA": b64encode(data).decode()}
            data = json.dumps(d).encode()
        len_data = len(data)
        l = Protocol.convert_base(len_data, 256)
        if len(l) > 4: raise Exception(f"Data {data} is too big to send in one packet!")
        for _ in range(4 - len(l)):
            l.insert(0, 0)
        prepending_bytes = b"".join([l[i].to_bytes(1, "little") for i in range(4)])
        finD = prepending_bytes + data
        return finD



    @staticmethod
    def get_msg(working_socket: socket.socket, key: bytes = b"", verifyKey=None):
        prepending_bytes = working_socket.recv(4)
        l = [b for b in prepending_bytes]
        len_of_msg = Protocol.convert_to_base10(l, 256)
        data = working_socket.recv(len_of_msg)
        data = json.loads(data.decode())
        msg = b64decode(data["DATA"])
        verify = None
        if len(key) != 0:
            msg = AESWrapper.decrypt(key, msg)
        if verifyKey:
            signature = (data["SIG"][0], ECPoint.load(data["SIG"][1]))
            verify = ECSchnorr.verify(signature, verifyKey, msg)
        return msg, verify




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
    def broadcast(msg, clients: set, key=b""):
        for client in clients:
            try:
                Protocol.send_command(client.soc, key=key, MSG=msg, COMMAND=Protocol.BROADCAST)
            except Exception as e:
                print(e)



    @staticmethod
    def send_command(sock: socket.socket, key: bytes = b"", signKey=None, **kwargs):
        data = json.dumps(kwargs).encode()
        sock.send(Protocol.create_msg(data, key=key, signKey=signKey))

    @staticmethod
    def recv_command(sock, key: bytes = b"", verifyKey=None):
        data, verified = Protocol.get_msg(sock, key=key, verifyKey=verifyKey)
        d = json.loads(data.decode())
        d["VERIFIED"] = verified
        return d
