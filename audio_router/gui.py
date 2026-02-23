# gui.py
import customtkinter as ctk
from router import *
from config import APP_NAME

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

ACCENT = "#00E5FF"
BG_MAIN = "#14181C"
BG_CARD = "#1B2127"
BORDER = "#2A3138"


class PebXGUI(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("PebX — Signal Control")
        self.geometry("1100x650")
        self.resizable(False, False)
        self.configure(fg_color=BG_MAIN)

        self.output_devices = {}
        self.input_devices = {}
        self.apps = {}

        self.build_ui()
        self.refresh_all()

    # --------------------------------------------------
    # UI
    # --------------------------------------------------

    def build_ui(self):

        # Header
        header = ctk.CTkLabel(
            self,
            text="PEBX SIGNAL CONTROL",
            font=("Segoe UI", 24, "bold"),
            text_color=ACCENT
        )
        header.pack(pady=(25, 10))

        # ---------------------------
        # TOP ROW
        # ---------------------------

        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(pady=20)

        # Global Output Card
        output_card = ctk.CTkFrame(
            top_frame,
            width=450,
            height=170,
            fg_color=BG_CARD,
            corner_radius=12
        )
        output_card.grid(row=0, column=0, padx=25)
        output_card.grid_propagate(False)

        ctk.CTkLabel(
            output_card,
            text="Global Output",
            text_color=ACCENT,
            font=("Segoe UI", 14)
        ).pack(pady=(15, 5))

        self.global_output_dropdown = ctk.CTkOptionMenu(
            output_card,
            width=350
        )
        self.global_output_dropdown.pack(pady=10)

        ctk.CTkButton(
            output_card,
            text="Apply Output",
            width=160,
            command=self._apply_global_output
        ).pack(pady=(10, 15))

        # Global Microphone Card
        mic_card = ctk.CTkFrame(
            top_frame,
            width=450,
            height=170,
            fg_color=BG_CARD,
            corner_radius=12
        )
        mic_card.grid(row=0, column=1, padx=25)
        mic_card.grid_propagate(False)

        ctk.CTkLabel(
            mic_card,
            text="Global Microphone",
            text_color=ACCENT,
            font=("Segoe UI", 14)
        ).pack(pady=(15, 5))

        self.global_mic_dropdown = ctk.CTkOptionMenu(
            mic_card,
            width=350
        )
        self.global_mic_dropdown.pack(pady=10)

        ctk.CTkButton(
            mic_card,
            text="Apply Microphone",
            width=160,
            command=self._apply_global_mic
        ).pack(pady=(10, 15))

        # ---------------------------
        # BOTTOM PANEL (PER APP)
        # ---------------------------

        bottom_card = ctk.CTkFrame(
            self,
            width=1000,
            height=230,
            fg_color=BG_CARD,
            corner_radius=12
        )
        bottom_card.pack(pady=30)
        bottom_card.pack_propagate(False)

        ctk.CTkLabel(
            bottom_card,
            text="Per-App Routing",
            text_color=ACCENT,
            font=("Segoe UI", 15)
        ).pack(pady=(15, 10))

        self.app_dropdown = ctk.CTkOptionMenu(
            bottom_card,
            width=800
        )
        self.app_dropdown.pack(pady=5)

        self.app_output_dropdown = ctk.CTkOptionMenu(
            bottom_card,
            width=800
        )
        self.app_output_dropdown.pack(pady=5)

        self.app_mic_dropdown = ctk.CTkOptionMenu(
            bottom_card,
            width=800
        )
        self.app_mic_dropdown.pack(pady=5)

        ctk.CTkButton(
            bottom_card,
            text="Apply To App",
            width=180,
            command=self._apply_app
        ).pack(pady=(15, 20))

    # --------------------------------------------------
    # DATA LOAD
    # --------------------------------------------------

    def refresh_all(self):
        self.output_devices = scan_output_devices()
        self.input_devices = scan_input_devices()
        self.apps = scan_audio_apps()

        if self.output_devices:
            names = list(self.output_devices.keys())
            self.global_output_dropdown.configure(values=names)
            self.global_output_dropdown.set(names[0])
            self.app_output_dropdown.configure(values=names)

        if self.input_devices:
            names = list(self.input_devices.keys())
            self.global_mic_dropdown.configure(values=names)
            self.global_mic_dropdown.set(names[0])
            self.app_mic_dropdown.configure(values=names)

        if self.apps:
            names = list(self.apps.keys())
            self.app_dropdown.configure(values=names)
            self.app_dropdown.set(names[0])

    # --------------------------------------------------
    # APPLY FUNCTIONS
    # --------------------------------------------------

    def _apply_global_output(self):
        selected = self.global_output_dropdown.get()
        if selected in self.output_devices:
            set_default_output(self.output_devices[selected])

    def _apply_global_mic(self):
        selected = self.global_mic_dropdown.get()
        if selected in self.input_devices:
            set_default_input(self.input_devices[selected])

    def _apply_app(self):
        app = self.app_dropdown.get()
        if app in self.apps:
            exe = self.apps[app]

            out_dev = self.app_output_dropdown.get()
            if out_dev in self.output_devices:
                set_app_device(self.output_devices[out_dev], exe)

            mic_dev = self.app_mic_dropdown.get()
            if mic_dev in self.input_devices:
                set_app_device(self.input_devices[mic_dev], exe)