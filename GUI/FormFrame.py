import customtkinter as ctk
from GeneralColorPalate import GeneralColorPalate as GCP


class CustomEntryBox(ctk.CTkFrame):
    def __init__(self, master, txt, width=890, height=120, is_password=False,**kwargs):
        super().__init__(master, width, height, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.entry_box = ctk.CTkEntry(self, width=width, height=height, fg_color=GCP.get_blue(), corner_radius=30,
                                      placeholder_text_color=GCP.get_blue_white(), placeholder_text=txt,
                                      font=GCP.get_font(64)
                                      , text_color=GCP.get_black(), border_width=0)
        if is_password:
            self.entry_box.configure(show="*")
        self.entry_box.grid(row=0, column=0, sticky="new")

    def get_val(self):
        return self.entry_box.get()


class FormFrame(ctk.CTkFrame):

    def __init__(self, master, values, submit_btn_text, submit_btn_callback_func, after_btn = None, form_label="", **kwargs):
        super().__init__(master, **kwargs)
        self.values = values
        self.entries = []
        if form_label != "":
            self.columnconfigure(0, weight=1)
            formNameLabel = ctk.CTkLabel(self, text_color=GCP.get_black(), text=form_label, font=GCP.get_font(129),
                                         fg_color="transparent")
            formNameLabel.grid(row=0, column=0, padx=0, pady=(50, 100), sticky="new")
        for i, v in enumerate(values):
            self.columnconfigure(i, weight=1)
            c = CustomEntryBox(self, v, width=890, height=120, fg_color="transparent")
            if v == "Password":
                c = CustomEntryBox(self, v, width=890, height=120, is_password=True, fg_color="transparent")
            c.grid(padx=0, pady=(0, 50))
            self.entries.append(c)

        self.btn = ctk.CTkButton(self, width=790, height=145, fg_color=GCP.get_white(), text_color=GCP.get_black(), text=submit_btn_text, font=GCP.get_font(64)
                                 , command=submit_btn_callback_func, corner_radius=30,
                                 hover_color=GCP.get_green(), border_width=0
                                 )
        self.btn.grid(pady=10)

        if after_btn is not None:
            self.after_btn = ctk.CTkButton(self, width=790, height=145, fg_color="transparent", text_color=GCP.get_white(),
                                           text=after_btn[0], font=GCP.get_font(48)
                                           , command=after_btn[1], corner_radius=30,
                                           hover_color=GCP.get_shadow_yellow(), border_width=0
                                           )
            self.after_btn.grid()



    def get_entry_values(self):
        r = []
        for e in self.entries:

            r.append(e.get_val())
        return r
