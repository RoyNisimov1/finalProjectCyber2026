import secrets
import socket
from threading import Thread, local
from connection import Connection
from protocol import Protocol
from datetime import datetime
import sqlite3
from secrets import token_bytes
from hashlib import scrypt

#AI
from AI.Gemini import GideonGeminiBackEnd

#Encryption
from AsymmetricEncryptions.PublicPrivateKey.ECC import ECKey, ECDH, ECPoint
from AsymmetricEncryptions.Protocols.KDF import KDF
from AsymmetricEncryptions.General.BytesAndInts import BytesAndInts
from Encryption.AESWrapper import AESWrapper


class Server:
    PORT = 6767

    def __init__(self):
        # setting up the AI
        self.GIDEON = GideonGeminiBackEnd()

        # setting up encryption

        self.key_pair = ECKey.new(Protocol.CURVE)

        self.ENCKey = AESWrapper.generate_key()



        self.thread_data = local()

        # setting up db
        # self.set_up_dbserver()
        #
        # db = self.get_db_connection()
        # dbc = db.cursor()
        # dbc.execute("SELECT * FROM users WHERE userName = 1")
        # print(dbc.fetchall())
        # db.close()
        # setting up managers
        self.managers = []
        with open("Web/MANAGER_LIST.txt", "r") as f:
            self.managers = f.read().split("\n")

        self.managers = set(self.managers)
        self.connections = set()
        self.bad_words = []
        with open("Web/BANNED_WORDS", "r") as f:
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

    def set_up_dbserver(self):

        dbConnection = self.get_db_connection()
        dbCursor = dbConnection.cursor()
        #Initial setup
        sqlcmd = """CREATE TABLE users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        userName VARCHAR(20),
        isAdmin INTEGER DEFAULT 0 CHECK (isAdmin IN (0, 1)),
        passwordHash VARCHAR(64),
        salt BLOB,
        public_key TEXT,
        encrypted_private_key TEXT
        )
        """
        dbCursor.execute(sqlcmd)
        dbConnection.close()

    def get_db_connection(self):
        if not hasattr(self.thread_data, "connection"):
            self.thread_data.connection = sqlite3.connect('UserDataBase.db', timeout=20)
            self.thread_data.connection.execute("PRAGMA journal_mode=WAL;")
        return self.thread_data.connection

    def sign_up(self, connection, shared_private_key: bytes):
        db = self.get_db_connection()
        cursor = db.cursor()

        try:
            # 1. Check if user exists
            cursor.execute("SELECT 1 FROM users WHERE userName = ?", (connection.userID,))
            if cursor.fetchone() is not None:
                return False

            # 2. Receive and Verify Data
            data = Protocol.recv_command(connection.soc, key=shared_private_key, verifyKey=connection.publicKey)
            if not data or not data.get("VERIFIED"):
                return False

            passwd = data.get("PASSWORD", "")
            if len(passwd) > 10:
                return False

            # 3. Hash and Store
            salt = token_bytes(16)
            hashed = scrypt(passwd.encode(), salt=salt, n=16384, r=8, p=1, dklen=64).hex()[:64]

            pub_key_str = str(connection.publicKey.export())

            cursor.execute(
                "INSERT INTO users (userName, isAdmin, passwordHash, salt, public_key, encrypted_private_key) VALUES (?, ?, ?, ?, ?, NULL)",
                (connection.userID, connection.userID == "Admin", hashed, salt, pub_key_str)
            )
            db.commit()
            return True

        except Exception as e:
            print(f"Sign-up error: {e}")  # Log the actual error to see why it fails
            return False
        finally:
            db.close()

    def log_in(self, connection, shared_private_key: bytes):
        db = self.get_db_connection()
        cursor = db.cursor()
        try:
            # 1. Check if user exists
            cursor.execute("SELECT * FROM users WHERE userName = ?", (connection.userID,))
            userData = cursor.fetchone()
            if userData is None:
                return False, None
            data = Protocol.recv_command(connection.soc, key=shared_private_key, verifyKey=connection.publicKey)
            if not data or not data.get("VERIFIED"):
                return False, None

            passwd = data.get("PASSWORD", "")
            pwdhash = userData[3]
            salt = userData[4]
            hashed = scrypt(passwd.encode(), salt=salt, n=16384, r=8, p=1, dklen=64).hex()[:64]
            ver = secrets.compare_digest(pwdhash, hashed)
            return ver, userData
        except Exception as e:
            print(f"Log-in error: {e}")  # Log the actual error to see why it fails
            return False, None


    def get_connection_by_id(self, user_id: str):
        r = None
        for con in self.connections:
            if con.userID == user_id:
                r = con
                break
        return r


    def handshake(self, conn):
        data: dict = Protocol.recv_command(conn)
        assert data["COMMAND"] == Protocol.HANDSHAKE
        assert "ID" in data
        assert "PUBKEY" in data
        Protocol.send_command(conn, COMMAND=Protocol.DH1, PUBKEY=self.key_pair.public_key.export())
        print("sent pk")
        k = ECPoint.load(data["PUBKEY"])
        p = ECDH.Stage2(self.key_pair, k)
        shared_key = KDF.derive_key(p.export().encode())[:32]
        Protocol.send_command(conn, key=shared_key, COMMAND=Protocol.DHFin, ENCKEY=BytesAndInts.byte2Int(self.ENCKey))
        if data["ID"].lower() in self.bad_words:
            print("Kicking client")
            self.kick_client(conn, "Name is not allowed")
            conn.close()
            return None, None
        conn_client = Connection(conn, data["ID"], isAdmin=self.isManager(data["ID"]), publicKey=k)
        if "PURPOSE" in data.keys():
            return conn_client, shared_key, data["PURPOSE"]
        return conn_client, shared_key, None

    def isManager(self, user_id):
        return user_id in self.managers

    def handle_client(self, conn: socket.socket, address):
        try:
            conn_client, shared_private_key, purpose = self.handshake(conn)
            if conn_client is None:
                return
            self.connections.add(conn_client)

            if purpose == Protocol.SIGNUP:
                success = self.sign_up(conn_client, shared_private_key)
                Protocol.send_command(conn, shared_private_key, self.key_pair, signup_success=success)
                self.kick_client(conn_client, "Signup done")
                return

            if purpose == Protocol.LOGGING_IN:
                success, userData = self.log_in(conn_client, shared_private_key)
                Protocol.send_command(conn, shared_private_key, self.key_pair, signup_success=success)
                if not success:
                    self.kick_client(conn_client, "Login Failed")
                if userData[2] == 1:
                    conn_client.set_admin(True)

            # Handle client
            while True:
                try:
                    data = Protocol.recv_command(conn, key=self.ENCKey, verifyKey=conn_client.publicKey)
                    if not data["VERIFIED"]:
                        continue
                    command = data["COMMAND"]
                    data["MSG"]: str
                    if command == Protocol.SEND_MSG:
                        if conn_client.isMuted:
                            continue
                        hasBadWord = False
                        dss1 = data["MSG"].lower()
                        for word in self.bad_words:
                            if word in dss1:
                                hasBadWord = True
                                break
                        if hasBadWord: continue
                        now = datetime.now()
                        time_now = now.strftime("%H:%M")
                        msg = time_now + " "
                        if conn_client.isAdmin:
                            msg += "@"
                        msg += conn_client.userID + ": " + data["MSG"]
                        Protocol.broadcast(msg, self.connections, key=self.ENCKey, signKey=self.key_pair, message_data=data["MSG"], date=time_now, author=conn_client.userID, is_admin=conn_client.isAdmin)
                    if command == Protocol.APPOINT_MANAGER:
                        if not conn_client.isAdmin: continue
                        self.promote_to_admin(data["USERID"])
                    if command == Protocol.DEMOTE_MANAGER:
                        if not conn_client.isAdmin: continue
                        self.demote_from_admin(data["USERID"])
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
                    if command == Protocol.KICK:
                        if not conn_client.isAdmin: continue
                        user = self.get_connection_by_id(data["USERID"])
                        if user is None: continue
                        self.kick_client(user, "Kicked by: " + conn_client.userID)
                    if command == Protocol.GET_USERS:
                        mangs = []
                        usrs = []
                        for _conn in self.connections:
                            if _conn.isAdmin: mangs.append(_conn.userID)
                            else: usrs.append(_conn.userID)
                        d = "----------------------\nAdmins:\n----------------------\n" + "\n".join(mangs) + "\n\n----------------------\nUsers:\n----------------------\n\n" + "\n".join(usrs)
                        Protocol.send_command(conn_client.soc, key=self.ENCKey, signKey=self.key_pair, COMMAND=Protocol.PRIVATE, MSG=d)
                    if command == Protocol.GIDEON:
                        prompt = data["PROMPT"]
                        response_ai = self.GIDEON.prompt(prompt)
                        Protocol.send_command(conn_client.soc, key=self.ENCKey, signKey=self.key_pair, COMMAND=Protocol.PRIVATE, MSG=response_ai, author="GIDEON", date=datetime.now().strftime("%H:%M"))
                except ConnectionError as e:
                    self.close_connection(conn_client)
                except WindowsError as e:
                    self.close_connection(conn_client)
                except Exception as e:
                    print(e)
        except Exception as _:
            conn.close()
        finally:
            self.get_db_connection().close()

    def promote_to_admin(self, user_id: str):
        db = self.get_db_connection()
        dbcursor = db.cursor()
        dbcursor.execute("UPDATE users SET isAdmin = 1 WHERE userName = ?", (user_id,))
        db.commit()
        user = self.get_connection_by_id(user_id)
        if user is None: return
        user.set_admin(True)

    def demote_from_admin(self, user_id: str):
        db = self.get_db_connection()
        dbcursor = db.cursor()
        dbcursor.execute("UPDATE users SET isAdmin = 0 WHERE userName = ?", (user_id,))
        db.commit()
        user = self.get_connection_by_id(user_id)
        if user is None: return
        user.set_admin(False)


    def kick_client(self, conn: Connection, kick_rsn: str):
        Protocol.send_command(conn.soc, key=self.ENCKey, COMMAND=Protocol.PRIVATE, MSG=kick_rsn, signKey=self.key_pair, author="SERVER", date="now")
        Protocol.send_command(conn.soc, key=self.ENCKey, COMMAND=Protocol.KICK, signKey=self.key_pair)
        self.close_connection(conn)


    def close_connection(self, conn: Connection):
        self.connections.remove(conn)
        try:
            conn.soc.close()
        except Exception as _: ...

if __name__ == "__main__":
    server: Server = Server()
