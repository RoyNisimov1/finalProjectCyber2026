import customtkinter as ctk
from FormFrame import FormFrame
from GeneralColorPalate import GeneralColorPalate as GCP


class LoginSignupPage(ctk.CTkFrame):

    def __init__(self, master, sign_up_callback_func=None, log_in_callback_func=None):
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

        self.signupframe = FormFrame(self.rightSideFrame, ["Username", "Password"], "Sign me up!",
                                     submit_btn_callback_func=lambda: sign_up_callback_func(self),
                                     form_label="Sign up",
                                     fg_color=GCP.get_yellow(),
                                     after_btn=("Already have an account? Log in", self.change_to_login),
                                     width=50, height=1080)
        self.signupframe.grid_propagate(False)
        self.signupframe.grid(row=0, column=0, sticky="nsew")

        self.loginframe = FormFrame(self.rightSideFrame, ["Username", "Password"], "Log me in!",
                                    submit_btn_callback_func=lambda: log_in_callback_func(self),
                                    form_label="Log in",
                                    fg_color=GCP.get_yellow(),
                                    after_btn=("Don't have an account? Sign up!", self.change_to_signup),
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

        text_with_newlines = "W E L L C O M E   T O  \nC L O A K"

        self.txtbx = ctk.CTkTextbox(
            self.leftSideFrame,
            text_color=GCP.get_white(),
            font=GCP.get_font(64),
            fg_color="transparent"
        )

        self.txtbx.insert("0.0", text_with_newlines)
        self.txtbx.unbind("<MouseWheel>")
        self.txtbx.configure(state="disabled")
        self.txtbx.bind("<Button-1>", lambda e: "break")
        self.txtbx.bind("<B1-Motion>", lambda e: "break")
        self.txtbx.bind("<Double-Button-1>", lambda e: "break")

        self.txtbx.grid(row=0, column=0, sticky="nsew", pady=40, padx=20)

    def change_to_login(self):
        self.signupframe.grid_forget()
        self.loginframe.grid(row=0, column=0, sticky="nsew")

    def change_to_signup(self):
        self.loginframe.grid_forget()
        self.signupframe.grid(row=0, column=0, sticky="nsew")

    def get_signup_values(self):
        return self.signupframe.get_entry_values()

    def get_login_values(self):
        return self.loginframe.get_entry_values()
