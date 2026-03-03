import socket
from threading import Thread
from connection import Connection
from protocol import Protocol
from datetime import datetime
from Gemini import GideonGeminiBackEnd


class Server:
    PORT = 6767

    def __init__(self):
        # setting up the AI
        self.GIDEON = GideonGeminiBackEnd()

        # setting up managers
        self.managers = []
        with open("MANAGER_LIST.txt", "r") as f:
            self.managers = f.read().split("\n")

        self.managers = set(self.managers)
        self.connections = set()
        self.bad_words = []
        with open("BANNED_WORDS", "r") as f:
            self.bad_words = f.read().split("\n")

        # setting up connections
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.sock:
                self.sock.bind(("0.0.0.0", Server.PORT))
                self.sock.listen()
                print("Server is up and listening on port ", Server.PORT)
                while True:
                    try:
                        conn, address = self.sock.accept()
                        print("Client connected from ", address)
                        client_thread = Thread(target=self.handle_client, args=[conn, address])
                        client_thread.start()
                    except Exception as e:
                        print(e)
                        try:
                            conn.close()
                        except Exception as e:
                            print(e)
        except Exception as e:
            print(e)

    def get_connection_by_id(self, id: str):
        r = None
        for con in self.connections:
            if con.userID == id:
                r = con
                break
        return r

    @staticmethod
    def handshake(conn):
        data = Protocol.recv_command(conn)
        assert data["COMMAND"] == Protocol.HANDSHAKE
        assert "ID" in data
        return data

    def isManager(self, id):
        return id in self.managers

    def handle_client(self, conn: socket.socket, address):

        try:
            # For first connection
            handshake = Server.handshake(conn)
            conn_client = Connection(conn, handshake["ID"], isAdmin=self.isManager(handshake["ID"]))
            self.connections.add(conn_client)

            # Handle client
            while True:
                try:
                    data = Protocol.recv_command(conn)
                    command = data["COMMAND"]
                    data["MSG"]: str
                    if command == Protocol.SEND_MSG:
                        if conn_client.isMuted:
                            continue
                        hasBadWord = False
                        for word in self.bad_words:
                            if word in data["MSG"]:
                                hasBadWord = True
                                break
                        if hasBadWord: continue
                        now = datetime.now()
                        time_now = now.strftime("%H:%M")
                        msg = time_now + " "
                        if conn_client.isAdmin:
                            msg += "@"
                        msg += conn_client.userID + ": " + data["MSG"]
                        Protocol.broadcast(msg, self.connections)
                    if command == Protocol.APPOINT_MANAGER:
                        if not conn_client.isAdmin: continue
                        user = self.get_connection_by_id(data["USERID"])
                        if user is None: continue
                        user.set_admin(True)
                    if command == Protocol.DEMOTE_MANAGER:
                        if not conn_client.isAdmin: continue
                        user = self.get_connection_by_id(data["USERID"])
                        if user is None: continue
                        user.set_admin(False)
                    if command == Protocol.MUTE:
                        if not conn_client.isAdmin: continue
                        user = self.get_connection_by_id(data["USERID"])
                        if user is None: continue
                        user.mute(True)
                    if command == Protocol.UNMUTE:
                        if not conn_client.isAdmin: continue
                        user = self.get_connection_by_id(data["USERID"])
                        if user is None: continue
                        user.mute(False)
                    if command == Protocol.GIDEON:
                        prompt = data["PROMPT"]
                        response_ai = self.GIDEON.prompt(prompt)
                        Protocol.send_command(conn_client.soc, COMMAND=Protocol.PRIVATE, MSG = response_ai)





                except ConnectionError as e:
                    self.close_connection(conn_client)
                except Exception as e:
                    print(e)
                    continue

        except:
            conn.close()


    def close_connection(self, conn: Connection):
        self.connections.remove(conn)


if __name__ == "__main__":
    server: Server = Server()
