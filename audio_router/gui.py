import customtkinter as ctk
from router import scan_output_devices, set_default_device
from profiles import save_profile, load_profiles, get_profile
from config import APP_NAME


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class AudioRouterGUI(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title(APP_NAME)
        self.geometry("650x450")
        self.resizable(False, False)

        self.devices = {}
        self.profiles = {}

        self.create_widgets()
        self.refresh_devices()
        self.refresh_profiles()

    def create_widgets(self):

        self.title_label = ctk.CTkLabel(
            self,
            text=APP_NAME,
            font=("Segoe UI", 24, "bold")
        )
        self.title_label.pack(pady=20)

        # Device Section
        self.device_label = ctk.CTkLabel(
            self,
            text="Select Default Output Device",
            font=("Segoe UI", 14)
        )
        self.device_label.pack(pady=10)

        self.device_dropdown = ctk.CTkOptionMenu(self, values=["Loading..."])
        self.device_dropdown.pack(pady=5)

        self.apply_button = ctk.CTkButton(
            self,
            text="Apply Device",
            command=self.apply_device
        )
        self.apply_button.pack(pady=15)

        self.refresh_button = ctk.CTkButton(
            self,
            text="Refresh Devices",
            command=self.refresh_devices
        )
        self.refresh_button.pack(pady=5)

        # Profile Section
        self.profile_label = ctk.CTkLabel(
            self,
            text="Profiles",
            font=("Segoe UI", 16, "bold")
        )
        self.profile_label.pack(pady=20)

        self.profile_dropdown = ctk.CTkOptionMenu(self, values=["No Profiles"])
        self.profile_dropdown.pack(pady=5)

        self.load_profile_button = ctk.CTkButton(
            self,
            text="Load Profile",
            command=self.load_selected_profile
        )
        self.load_profile_button.pack(pady=5)

        self.profile_name_entry = ctk.CTkEntry(
            self,
            placeholder_text="Profile Name"
        )
        self.profile_name_entry.pack(pady=5)

        self.save_profile_button = ctk.CTkButton(
            self,
            text="Save Current as Profile",
            command=self.save_current_profile
        )
        self.save_profile_button.pack(pady=10)

    def refresh_devices(self):
        self.devices = scan_output_devices()

        if self.devices:
            names = list(self.devices.keys())
            self.device_dropdown.configure(values=names)
            self.device_dropdown.set(names[0])
        else:
            self.device_dropdown.configure(values=["No Devices Found"])
            self.device_dropdown.set("No Devices Found")

    def apply_device(self):
        selected = self.device_dropdown.get()
        if selected in self.devices:
            set_default_device(self.devices[selected])

    def refresh_profiles(self):
        self.profiles = load_profiles()

        if self.profiles:
            names = list(self.profiles.keys())
            self.profile_dropdown.configure(values=names)
            self.profile_dropdown.set(names[0])
        else:
            self.profile_dropdown.configure(values=["No Profiles"])
            self.profile_dropdown.set("No Profiles")

    def save_current_profile(self):
        name = self.profile_name_entry.get().strip()
        selected = self.device_dropdown.get()

        if name and selected in self.devices:
            save_profile(name, self.devices[selected])
            self.refresh_profiles()

    def load_selected_profile(self):
        profile_name = self.profile_dropdown.get()
        device_id = get_profile(profile_name)

        if device_id:
            set_default_device(device_id)


