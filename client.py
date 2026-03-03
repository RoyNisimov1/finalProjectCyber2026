import socket
from tkinter.constants import COMMAND

from server import Server
from protocol import Protocol
from threading import Thread

class Client:

    def __init__(self, ip="127.0.0.1", port=Server.PORT):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.sock:
            self.sock.connect((ip, port))
            id = Client.get_id()
            self.handshake(id)
            listenThread = Thread(target=self.listen)
            listenThread.start()
            while True:
                try:
                    data = input("Send messages (/ for commands): ").lstrip()
                    if data[0] != "/":
                        Protocol.send_command(self.sock, COMMAND=Protocol.SEND_MSG, MSG=data)

                    data = data[1:]
                    parsed_data = Protocol.parse_command(data)
                    if parsed_data[0] in ["AM", "APPOINT_MANAGER"]:
                        userID = parsed_data[1]
                        Protocol.send_command(self.sock, COMMAND=Protocol.APPOINT_MANAGER, USERID=userID)
                    if parsed_data[0] in ["DM", "DEMOTE_MANAGER"]:
                        userID = parsed_data[1]
                        Protocol.send_command(self.sock, COMMAND=Protocol.DEMOTE_MANAGER, USERID=userID)
                    if parsed_data[0] in ["MT", "MUTE"]:
                        userID = parsed_data[1]
                        Protocol.send_command(self.sock, COMMAND=Protocol.MUTE, USERID=userID)
                    if parsed_data[0] in ["UMT", "UNMUTE"]:
                        userID = parsed_data[1]
                        Protocol.send_command(self.sock, COMMAND=Protocol.UNMUTE, USERID=userID)
                    if parsed_data[0] in ["GIDEON"]:
                        prompt = " ".join(parsed_data[1:])
                        Protocol.send_command(self.sock, COMMAND=Protocol.GIDEON, PROMPT = prompt)
                except Exception as e:
                    ...
    def listen(self):
        while True:
            try:
                data = Protocol.recv_command(self.sock)
                if data["COMMAND"] == Protocol.BROADCAST:
                    print(Protocol.GREEN)
                    print("\n" + data["MSG"])
                    print(Protocol.RESET)

                if data["COMMAND"] == Protocol.PRIVATE:
                    print(Protocol.RED)
                    print("\n" + data["MSG"])
                    print(Protocol.RESET)
            except ConnectionError:
                return
            except Exception:
                ...

    @staticmethod
    def get_id():
        return input("ID: ")

    def handshake(self, id: str):
        data = {"COMMAND": Protocol.HANDSHAKE, "ID": id}
        Protocol.send_command(self.sock, **data)

if __name__ == "__main__":
    client = Client()