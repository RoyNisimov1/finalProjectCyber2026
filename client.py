import socket
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
                data = input("Send messages (/ for commands): ").lstrip()
                if data[0] != "/":
                    Protocol.send_command(self.sock, COMMAND = "SEND_MSG", MSG = data)


    def listen(self):
        while True:
            try:
                data = Protocol.recv_command(self.sock)
                if data["COMMAND"] == "BROADCAST":
                    GREEN = '\033[32m'
                    RESET = '\033[0m'
                    print(GREEN)
                    print("\n" + data["MSG"])
                    print(RESET)
            except ConnectionError:
                return
            except Exception:
                ...

    @staticmethod
    def get_id():
        return input("ID: ")

    def handshake(self, id: str):
        data = {"COMMAND": "HANDSHAKE", "ID": id}
        Protocol.send_command(self.sock, **data)

if __name__ == "__main__":
    client = Client()