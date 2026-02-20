# gui.py
import customtkinter as ctk
import threading
import time
from router import *
from config import APP_NAME

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

ACCENT = "#00E5FF"
BG_MAIN = "#14181C"
BG_PANEL = "#1B2127"
BORDER = "#2A3138"


class PebXGUI(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("PebX — Signal Control")
        self.geometry("1100x650")
        self.configure(fg_color=BG_MAIN)
        self.resizable(False, False)

        self.output_devices = {}
        self.input_devices = {}
        self.apps = {}

        self._pulse_running = False

        self.build_ui()
        self.refresh_all()

        self.after(2000, self._update_status)

    # --------------------------------------------------
    # UI
    # --------------------------------------------------

    def build_ui(self):

        header = ctk.CTkLabel(self, text="PEBX SIGNAL CONTROL",
                              font=("Segoe UI", 24, "bold"),
                              text_color=ACCENT)
        header.pack(pady=20)

        main = ctk.CTkFrame(self, fg_color=BG_MAIN)
        main.pack(fill="both", expand=True, padx=20)

        main.columnconfigure((0, 1), weight=1)

        # GLOBAL OUTPUT
        output_panel = ctk.CTkFrame(main, fg_color=BG_PANEL)
        output_panel.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

        ctk.CTkLabel(output_panel, text="Global Output", text_color=ACCENT).pack(pady=10)

        self.global_output_dropdown = ctk.CTkOptionMenu(output_panel, values=["Loading..."])
        self.global_output_dropdown.pack(pady=10, padx=20, fill="x")

        ctk.CTkButton(output_panel, text="Apply Output",
                      command=self._apply_global_output).pack(pady=10)

        # GLOBAL MIC
        mic_panel = ctk.CTkFrame(main, fg_color=BG_PANEL)
        mic_panel.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")

        ctk.CTkLabel(mic_panel, text="Global Microphone", text_color=ACCENT).pack(pady=10)

        self.global_mic_dropdown = ctk.CTkOptionMenu(mic_panel, values=["Loading..."])
        self.global_mic_dropdown.pack(pady=10, padx=20, fill="x")

        ctk.CTkButton(mic_panel, text="Apply Microphone",
                      command=self._apply_global_mic).pack(pady=10)

        # PER APP
        app_panel = ctk.CTkFrame(self, fg_color=BG_PANEL)
        app_panel.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(app_panel, text="Per-App Routing", text_color=ACCENT).pack(pady=10)

        self.app_dropdown = ctk.CTkOptionMenu(app_panel, values=["Loading..."])
        self.app_dropdown.pack(pady=5, padx=40, fill="x")

        self.app_output_dropdown = ctk.CTkOptionMenu(app_panel, values=["Select Output"])
        self.app_output_dropdown.pack(pady=5, padx=40, fill="x")

        self.app_mic_dropdown = ctk.CTkOptionMenu(app_panel, values=["Select Mic"])
        self.app_mic_dropdown.pack(pady=5, padx=40, fill="x")

        ctk.CTkButton(app_panel, text="Apply To App",
                      command=self._apply_app).pack(pady=10)

    # --------------------------------------------------
    # REFRESH
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
    # APPLY
    # --------------------------------------------------

    def _apply_global_output(self):
        selected = self.global_output_dropdown.get()
        if selected in self.output_devices:
            set_default_device(self.output_devices[selected])

    def _apply_global_mic(self):
        selected = self.global_mic_dropdown.get()
        if selected in self.input_devices:
            set_default_device(self.input_devices[selected])

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

    # --------------------------------------------------

    def _update_status(self):
        self.after(2000, self._update_status)