import customtkinter as ctk

class GeneralColorPalate:

    @staticmethod
    def get_black():
        return "#110B11"

    @staticmethod
    def get_white():
        return "#F2F4CB"

    @staticmethod
    def get_yellow():
        return "#B7990D"

    @staticmethod
    def get_blue():
        return "#8CADA7"

    @staticmethod
    def get_blue_white():
        return "#bfd1b9"

    @staticmethod
    def get_green():
        return "#A5D0A8"

    @staticmethod
    def get_heading_font():
        return ctk.CTkFont(family="Inter", size=96, weight="bold")

    @staticmethod
    def get_label_font():
        return ctk.CTkFont(family="Inter", size=32)

    @staticmethod
    def get_font(size=32):
        return ctk.CTkFont(family="Inter", size=size)

    @staticmethod
    def get_shadow_yellow():
        return "#89730a"

