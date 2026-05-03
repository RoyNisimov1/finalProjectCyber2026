
import customtkinter as ctk
from LOGIN_SIGNUP import LoginSignupPage
from GeneralColorPalate import GeneralColorPalate as GCP


class APP(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Cloak Client")
        self.geometry("1000x1000")
        self.attributes("-fullscreen", True)
        self.bind("<Escape>", lambda event: app.attributes("-fullscreen", False))
        self.configure(fg_color="#110B11")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        l = LoginSignupPage(self)
        l.grid(sticky="nsew")









if __name__ == "__main__":
    app = APP()
    app.mainloop()
