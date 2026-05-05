import customtkinter as ctk
from customtkinter import CTkFrame

from GeneralColorPalate import GeneralColorPalate as GCP
from GUIEvent import GUIEvent

class Message:

    def __init__(self, author, date, text, isPrivate=False):
        self.author = author
        self.date = date
        self.text = text
        self.isPrivate=isPrivate

class MessageContainer(ctk.CTkFrame):

    def __init__(self, master, message: Message):
        super().__init__(master,  fg_color="transparent", corner_radius=50)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.label = ctk.CTkLabel(self, fg_color="transparent", text_color=GCP.get_black(),
                                  font=GCP.get_font(40), text=message.author)
        self.label.grid(sticky="nsew", row=0, column=0)
        color = GCP.get_blue()
        if message.isPrivate:
            color = GCP.get_yellow()
        self.text_box = ctk.CTkTextbox(self, fg_color=color,
                                       corner_radius=50,
                                       text_color=GCP.get_white(), font=GCP.get_font(48))
        self.text_box.insert("0.0", message.text)
        self.text_box.configure(state="disabled")
        self.text_box.grid(row=1, column=0, sticky="nsew")

class MessagesHolderBox(ctk.CTkScrollableFrame):

    def __init__(self, master):
        super().__init__(master, corner_radius=50, fg_color=GCP.get_green(), scrollbar_button_color=GCP.get_yellow(),
                         scrollbar_button_hover_color=GCP.get_white())
        self.messages: list[Message] = []
        self.mgs_ctr = []
        self.update_msg()



    def update_msg(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=4)
        for i, msg in enumerate(self.messages):
            mc = MessageContainer(self, msg)
            mc.grid(row=i, column=0, sticky="nsew", pady=10)
            self.mgs_ctr.append(mc)

    def add_msg(self, message: Message):
        self.messages.append(message)
        mc = MessageContainer(self, message)
        mc.grid(row=len(self.messages), column=0, sticky="nsew", pady=10)
        self.mgs_ctr.append(mc)


class MessageEntryBox(ctk.CTkFrame):
    def __init__(self, master, submit_btn_callback=None):
        super().__init__(master, fg_color="transparent")
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=7)
        self.grid_columnconfigure(1, weight=1)
        self.msg_box = ctk.CTkTextbox(self, fg_color=GCP.get_yellow(),
                                    font=GCP.get_font(48),
                                    text_color=GCP.get_white(),
                                    corner_radius=40, border_width=0,
                                    )
        self.msg_box.grid(row=1, column=0, sticky="nsew", padx=(10, 0), pady=10)

        self.on_submit = GUIEvent()
        size = 210
        self.send_btn = ctk.CTkButton(self, width=size, height=size, corner_radius=size//2, text="", fg_color="transparent",
                                      border_color=GCP.get_blue(),
                                      hover_color=GCP.get_green(),
                                      border_width=4,
                                      command=self.on_submit.invoke)
        self.send_btn.grid(row=1, column=1, padx=0, pady=10)

    def subscribe(self, callback):
        self.on_submit.subscribe(callback)

    def clear_txt_box(self):
        self.msg_box.delete("0.0", "end")

    def get_text(self):
        return self.msg_box.get("0.0", "end")

    def get_submit_event(self):
        return self.on_submit

class MainPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.grid_rowconfigure(0, weight=100)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.m = MessageEntryBox(self)
        self.m.grid(row=1, sticky="nsew")

        self.msg_holder_box = MessagesHolderBox(self)
        self.get_submit_event().subscribe(self.force_scrollbar_to_bottom)
        self.msg_holder_box.grid(row=0, sticky="nsew", padx=10, pady=10)

    def force_scrollbar_to_bottom(self):
        self.update_idletasks()
        self.msg_holder_box._parent_canvas.yview_moveto(1.0)

    def get_submit_event(self):
        return self.m.get_submit_event()

    def get_msg_entry_box(self):
        return self.m

    def get_msg_holder_box(self):
        return self.msg_holder_box
