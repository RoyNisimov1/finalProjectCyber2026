
import customtkinter as ctk
from LOGIN_SIGNUP import LoginSignupPage
from MAIN_PAGE import MainPage, Message
from GeneralColorPalate import GeneralColorPalate as GCP
import socket
from threading import Thread

from Web.protocol import Protocol
from GUIEvent import GUIEvent
from AsymmetricEncryptions.PublicPrivateKey.ECC import ECKey, ECDH, ECPoint
from AsymmetricEncryptions.Protocols.KDF import KDF
from AsymmetricEncryptions.General.BytesAndInts import BytesAndInts

class APP(ctk.CTk):

    def __init__(self, ip="127.0.0.1", port=6767):
        super().__init__()
        try:
            self.key_pair = ECKey.new(Protocol.CURVE)
            self.ENCKey = None
            self.sock = None
            self.server_public_key = None

            self.disconnectB = False

            self.logged_event = GUIEvent()

            def signup(signupframe: LoginSignupPage):
                username, password = signupframe.get_signup_values()
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.sock:
                    self.sock.connect((ip, port))
                    data = {"COMMAND": Protocol.HANDSHAKE, "ID": username, "PUBKEY": self.key_pair.public_key.export(),
                            "PURPOSE": Protocol.SIGNUP}
                    Protocol.send_command(self.sock, **data)
                    d = Protocol.recv_command(self.sock)
                    assert "PUBKEY" in d and "COMMAND" in d
                    self.server_public_key = ECPoint.load(d["PUBKEY"])
                    ecdh = ECDH(self.key_pair)
                    p = ecdh.Stage1(self.server_public_key)
                    shared_key = KDF.derive_key(p.export().encode())[:32]
                    d = Protocol.recv_command(self.sock, key=shared_key)
                    self.ENCKey = BytesAndInts.int2Byte(d["ENCKEY"])
                    data = {"PASSWORD": password,
                            "PURPOSE": Protocol.SIGNUP}
                    Protocol.send_command(self.sock, **data, key=shared_key, signKey=self.key_pair)
                    data = Protocol.recv_command(self.sock, key=shared_key, verifyKey=self.server_public_key)
                    if data['signup_success']:
                        signupframe.change_to_login()

            def login(loginframe: LoginSignupPage):
                username, password = loginframe.get_login_values()
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((ip, port))
                data = {"COMMAND": Protocol.HANDSHAKE, "ID": username, "PUBKEY": self.key_pair.public_key.export(),
                        "PURPOSE": Protocol.LOGGING_IN}
                Protocol.send_command(self.sock, **data)
                d = Protocol.recv_command(self.sock)
                assert "PUBKEY" in d and "COMMAND" in d
                self.server_public_key = ECPoint.load(d["PUBKEY"])
                ecdh = ECDH(self.key_pair)
                p = ecdh.Stage1(self.server_public_key)
                shared_key = KDF.derive_key(p.export().encode())[:32]
                d = Protocol.recv_command(self.sock, key=shared_key)
                self.ENCKey = BytesAndInts.int2Byte(d["ENCKEY"])
                data = {"USERNAME": username, "PASSWORD": password,
                        "PURPOSE": Protocol.LOGGING_IN}
                Protocol.send_command(self.sock, **data, key=shared_key, signKey=self.key_pair)
                data = Protocol.recv_command(self.sock, key=shared_key, verifyKey=self.server_public_key)
                self.logged_event.invoke()
                return data

            # GUI
            self.title("Cloak Client")
            self.geometry("1920x1080")
            self.attributes("-fullscreen", True)
            self.bind("<Escape>", lambda event: app.attributes("-fullscreen", False))
            self.configure(fg_color="#110B11")
            self.grid_columnconfigure(0, weight=1)
            self.grid_rowconfigure(0, weight=1)
            self.login_signup_page = LoginSignupPage(self, sign_up_callback_func=signup, log_in_callback_func=login)
            self.login_signup_page.grid(sticky="nsew")
            self.main_page = MainPage(self)

            def change_login_to_main_page():
                self.login_signup_page.grid_forget()
                self.main_page.grid(sticky="nsew")

            def start_listening_loop():
                self.listenThread = Thread(target=self.listen)
                self.listenThread.start()

            def send_msg():
                entry_box = self.main_page.get_msg_entry_box()
                txt: str = entry_box.get_text()
                txt = txt.lstrip()
                txt = txt.rstrip()
                Protocol.send_command(self.sock, key=self.ENCKey, COMMAND=Protocol.SEND_MSG, MSG=txt,
                                      signKey=self.key_pair)
                entry_box.clear_txt_box()

            self.main_page.get_submit_event().subscribe(send_msg)
            self.logged_event.subscribe(change_login_to_main_page)
            self.logged_event.subscribe(start_listening_loop)

            #change_login_to_main_page()

        except Exception as e:
            print(e)
        finally:
            if self.sock is not None:
                self.sock.close()

    def listen(self):
        print("Started listening")
        while not self.disconnectB:
            try:
                data = Protocol.recv_command(self.sock, key=self.ENCKey, verifyKey=self.server_public_key)
                if not data["VERIFIED"]: continue
                if data["COMMAND"] == Protocol.BROADCAST:
                    self.main_page.get_msg_holder_box().add_msg(Message(author=data["author"], date=data["date"], text=data["message_data"]))

                if data["COMMAND"] == Protocol.PRIVATE:
                    self.main_page.get_msg_holder_box().add_msg(
                        Message(author=data["author"], date=data["date"], text=data["message_data"],
                                isPrivate=True))

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



if __name__ == "__main__":
    app = APP()
    app.mainloop()
