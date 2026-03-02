import socket
from threading import Thread
from connection import Connection
from protocol import Protocol
from datetime import datetime


class Server:
    PORT = 6767

    def __init__(self):
        # setting up managers
        self.managers = []
        with open("MANAGER_LIST.txt", "r") as f:
            self.managers = f.read().split("\n")

        self.managers = set(self.managers)
        self.connections = set()

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

    @staticmethod
    def handshake(conn):
        data = Protocol.recv_command(conn)
        assert data["COMMAND"] == "HANDSHAKE"
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
                    if command == "SEND_MSG":
                        now = datetime.now()
                        time_now = now.strftime("%H:%M")
                        msg = time_now + " "
                        if conn_client.isAdmin:
                            msg += "@"
                        msg += conn_client.userID + ": " + data["MSG"]
                        Protocol.broadcast(msg, self.connections)


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
