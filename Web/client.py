import socket

from server import Server
from protocol import Protocol
from threading import Thread
from AsymmetricEncryptions.PublicPrivateKey.ECC import ECKey, ECDH, ECPoint
from AsymmetricEncryptions.Protocols.KDF import KDF
from AsymmetricEncryptions.General.BytesAndInts import BytesAndInts


class Client:

    def __init__(self, ip="127.0.0.1", port=Server.PORT):
        #Encryption
        self.key_pair = ECKey.new(Protocol.CURVE)
        self.ENCKey = None

        self.server_public_key = None

        self.disconnectB = False
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.sock:
            self.sock.connect((ip, port))
            id = Client.get_id()
            method = input("Sign up [0]\nLog in [1]\n")
            if method in ["0", ""]:
                method = Protocol.SIGNUP
            if method in ["1"]:
                method = Protocol.LOGGING_IN
            handshake_data = self.handshake(id, method)
            if method == Protocol.SIGNUP:
                print(handshake_data)
                self.disconnect()
                return
            listenThread = Thread(target=self.listen)
            listenThread.start()
            while not self.disconnectB:
                try:
                    data = input("Send messages (/ for commands): ").lstrip()
                    if data[0] != "/":
                        Protocol.send_command(self.sock, key=self.ENCKey, COMMAND=Protocol.SEND_MSG, MSG=data, signKey=self.key_pair)

                    data = data[1:]
                    parsed_data = Protocol.parse_command(data)
                    if parsed_data[0].lower() in ["am", "appoint_manager", "appointmanager"]:
                        userID = parsed_data[1]
                        Protocol.send_command(self.sock, key=self.ENCKey, COMMAND=Protocol.APPOINT_MANAGER, USERID=userID, signKey=self.key_pair)
                    if parsed_data[0].lower() in ["dm", "demote_manager", "demotemanager"]:
                        userID = parsed_data[1]
                        Protocol.send_command(self.sock, key=self.ENCKey, COMMAND=Protocol.DEMOTE_MANAGER, USERID=userID, signKey=self.key_pair)
                    if parsed_data[0].lower() in ["mt", "mute"]:
                        userID = parsed_data[1]
                        Protocol.send_command(self.sock, key=self.ENCKey, COMMAND=Protocol.MUTE, USERID=userID, signKey=self.key_pair)
                    if parsed_data[0].lower() in ["umt", "unmute"]:
                        userID = parsed_data[1]
                        Protocol.send_command(self.sock, key=self.ENCKey, COMMAND=Protocol.UNMUTE, USERID=userID, signKey=self.key_pair)
                    if parsed_data[0].lower() in ["kick"]:
                        userID = parsed_data[1]
                        Protocol.send_command(self.sock, key=self.ENCKey, COMMAND=Protocol.KICK, USERID=userID, signKey=self.key_pair)
                    if parsed_data[0].lower() in ["users", "gusrs", "get_users"]:
                        Protocol.send_command(self.sock, key=self.ENCKey, COMMAND=Protocol.GET_USERS, signKey=self.key_pair)
                    if parsed_data[0] in ["GIDEON"]:
                        prompt = " ".join(parsed_data[1:])
                        Protocol.send_command(self.sock, key=self.ENCKey, COMMAND=Protocol.GIDEON, PROMPT=prompt, signKey=self.key_pair)
                except Exception as e:
                    ...
    def listen(self):
        while not self.disconnectB:
            try:
                data = Protocol.recv_command(self.sock, key=self.ENCKey)
                if data["COMMAND"] == Protocol.BROADCAST:
                    print(Protocol.GREEN)
                    print("\n" + data["MSG"])
                    print(Protocol.RESET)

                if data["COMMAND"] == Protocol.PRIVATE:
                    print(Protocol.RED)
                    print("\n" + data["MSG"])
                    print(Protocol.RESET)
                if data["COMMAND"] == Protocol.KICK:
                    print(Protocol.RED)
                    print("KICKED")
                    if "KICKRSN" in data.keys():
                        print("KICK REASON: " + data["KICKRSN"])
                    print(Protocol.RESET)
                    self.disconnect()
            except ConnectionError:
                return
            except Exception:
                ...

    def disconnect(self):
        self.disconnectB = True

    @staticmethod
    def get_id():
        return input("ID: ")

    def handshake(self, id: str, purpose=Protocol.SIGNUP):
        data = {"COMMAND": Protocol.HANDSHAKE, "ID": id, "PUBKEY": self.key_pair.public_key.export(), "PURPOSE": purpose}
        Protocol.send_command(self.sock, **data)
        d = Protocol.recv_command(self.sock)
        assert "PUBKEY" in d and "COMMAND" in d
        self.server_public_key = ECPoint.load(d["PUBKEY"])
        ecdh = ECDH(self.key_pair)
        p = ecdh.Stage1(self.server_public_key)
        shared_key = KDF.derive_key(p.export().encode())[:32]
        d = Protocol.recv_command(self.sock, key=shared_key)
        self.ENCKey = BytesAndInts.int2Byte(d["ENCKEY"])
        data = None
        if purpose == Protocol.SIGNUP:
            password = input("Password: ")
            data = {"PASSWORD": password,
                    "PURPOSE": purpose}
            Protocol.send_command(self.sock, **data, key=shared_key, signKey=self.key_pair)
            data = Protocol.recv_command(self.sock,  key=shared_key, verifyKey=self.server_public_key)
        if purpose == Protocol.LOGGING_IN:
            password = input("Password: ")
            data = {"PASSWORD": password,
                    "PURPOSE": purpose}
            Protocol.send_command(self.sock, **data, key=shared_key, signKey=self.key_pair)
            data = Protocol.recv_command(self.sock,  key=shared_key, verifyKey=self.server_public_key)
        return data


if __name__ == "__main__":
    client = Client()
