import customtkinter as ctk
from router import (
    scan_output_devices,
    scan_audio_apps,
    set_default_device,
    set_app_device,
    toggle_mute,
    open_windows_audio_settings
)
from config import APP_NAME


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class PebXGUI(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title(APP_NAME)
        self.geometry("900x600")
        self.resizable(False, False)

        self.devices = {}
        self.apps = {}

        self.build_ui()
        self.refresh_all()

    # ---------------- UI ----------------

    def build_ui(self):

        title = ctk.CTkLabel(
            self,
            text=APP_NAME,
            font=("Segoe UI", 28, "bold")
        )
        title.pack(pady=20)

        # ---------------- GLOBAL SECTION ----------------

        global_frame = ctk.CTkFrame(self)
        global_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(global_frame,
                     text="Global Output Device",
                     font=("Segoe UI", 16, "bold")).pack(pady=10)

        self.global_device_dropdown = ctk.CTkOptionMenu(global_frame, values=["Loading..."])
        self.global_device_dropdown.pack(pady=5)

        ctk.CTkButton(
            global_frame,
            text="Apply Global Device",
            command=self.apply_global_device
        ).pack(pady=10)

        # ---------------- PER APP SECTION ----------------

        app_frame = ctk.CTkFrame(self)
        app_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(app_frame,
                     text="Per-Application Routing",
                     font=("Segoe UI", 16, "bold")).pack(pady=10)

        self.app_dropdown = ctk.CTkOptionMenu(app_frame, values=["No Apps"])
        self.app_dropdown.pack(pady=5)

        self.app_device_dropdown = ctk.CTkOptionMenu(app_frame, values=["Select Device"])
        self.app_device_dropdown.pack(pady=5)

        ctk.CTkButton(
            app_frame,
            text="Apply App Routing",
            command=self.apply_app_routing
        ).pack(pady=10)

        # ---------------- QUICK ACTIONS ----------------

        actions_frame = ctk.CTkFrame(self)
        actions_frame.pack(pady=20, padx=20, fill="x")

        ctk.CTkLabel(actions_frame,
                     text="Quick Actions",
                     font=("Segoe UI", 16, "bold")).pack(pady=10)

        ctk.CTkButton(
            actions_frame,
            text="Toggle Mute",
            command=toggle_mute
        ).pack(pady=5)

        ctk.CTkButton(
            actions_frame,
            text="Open Windows Audio Mixer",
            command=open_windows_audio_settings
        ).pack(pady=5)

        ctk.CTkButton(
            actions_frame,
            text="Refresh Devices & Apps",
            command=self.refresh_all
        ).pack(pady=10)

    # ---------------- REFRESH ----------------

    def refresh_all(self):
        self.refresh_devices()
        self.refresh_apps()

    def refresh_devices(self):
        self.devices = scan_output_devices()

        if self.devices:
            names = list(self.devices.keys())
            self.global_device_dropdown.configure(values=names)
            self.global_device_dropdown.set(names[0])

            self.app_device_dropdown.configure(values=names)
            self.app_device_dropdown.set(names[0])
        else:
            self.global_device_dropdown.configure(values=["No Devices"])
            self.app_device_dropdown.configure(values=["No Devices"])

    def refresh_apps(self):
        self.apps = scan_audio_apps()

        if self.apps:
            names = list(self.apps.keys())
            self.app_dropdown.configure(values=names)
            self.app_dropdown.set(names[0])
        else:
            self.app_dropdown.configure(values=["No Active Audio Apps"])
            self.app_dropdown.set("No Active Audio Apps")

    # ---------------- ACTIONS ----------------

    def apply_global_device(self):
        selected = self.global_device_dropdown.get()
        if selected in self.devices:
            set_default_device(self.devices[selected])

    def apply_app_routing(self):
        app_name = self.app_dropdown.get()
        device_name = self.app_device_dropdown.get()

        if app_name in self.apps and device_name in self.devices:
            exe_name = self.apps[app_name]
            device_id = self.devices[device_name]
            set_app_device(device_id, exe_name)
