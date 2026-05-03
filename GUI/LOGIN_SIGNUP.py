import customtkinter as ctk
from FormFrame import FormFrame
from GeneralColorPalate import GeneralColorPalate as GCP

class LoginSignupPage (ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master)
        self.configure(fg_color="#110B11")

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.rightSideFrame = ctk.CTkFrame(self)
        self.rightSideFrame.grid_columnconfigure(0, weight=1)
        self.rightSideFrame.grid_rowconfigure(0, weight=1)
        self.rightSideFrame.grid_propagate(False)
        self.rightSideFrame.grid(row=0, column=1, sticky="nsew")

        def change_to_login():
            self.signupframe.grid_forget()
            self.loginframe.grid(row=0, column=0, sticky="nsew")


        def change_to_signup():
            self.loginframe.grid_forget()
            self.signupframe.grid(row=0, column=0, sticky="nsew")

        self.signupframe = FormFrame(self.rightSideFrame, ["Username", "Password"], "Sign me up!",
                                     submit_btn_callback_func=lambda: print(self.signupframe.get_entry_values()),
                                     form_label="Sign up",
                                     fg_color=GCP.get_yellow(),
                                     after_btn=("Already have an account? Log in", change_to_login),
                                     width=50, height=1080)
        self.signupframe.grid_propagate(False)
        self.signupframe.grid(row=0, column=0, sticky="nsew")

        self.loginframe = FormFrame(self.rightSideFrame, ["Username", "Password"], "Log me in!",
                                     submit_btn_callback_func=lambda: print(self.signupframe.get_entry_values()),
                                     form_label="Log in",
                                     fg_color=GCP.get_yellow(),
                                     after_btn=("Don't have an account? Sign up!", change_to_signup),
                                     width=50, height=1080)
        self.loginframe.grid_propagate(False)
        #self.loginframe.grid(row=0, column=0, sticky="nsew")

        self.leftSideFrame = ctk.CTkFrame(self, fg_color="transparent")
        self.leftSideFrame.grid_columnconfigure(0, weight=1)
        self.leftSideFrame.grid_rowconfigure(0, weight=1)
        self.leftSideFrame.grid(row=0, column=0, sticky="nsew")
        self.leftSideFrame.grid_propagate(False)
        self.leftSideFrame.grid_rowconfigure(0, weight=1)
        self.leftSideFrame.grid_columnconfigure(0, weight=1)

        text_with_newlines = "W E L L C O M E\n\n\n\nT O\n\n\n\nC L O A K"

        self.label = ctk.CTkLabel(
            self.leftSideFrame,
            text_color=GCP.get_white(),
            text=text_with_newlines,
            font=GCP.get_font(64),
            justify="center"
        )

        self.label.grid(row=0, column=0, sticky="nwe", pady=40, padx=20)




