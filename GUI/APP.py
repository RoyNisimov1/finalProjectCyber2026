import customtkinter as ctk
import hashlib

class APP(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Cloak Client")
        self.geometry("300x200")
        self.attributes("-fullscreen", True)
        self.bind("<Escape>", lambda event: app.attributes("-fullscreen", False))
        self.configure(fg_color="#110B11")



if __name__ == "__main__":
    print(len(hashlib.sha3_256(b"test").hexdigest()))
    app = APP()
    app.mainloop()























