# gui.py
import customtkinter as ctk
import threading
import time
from router import (
    scan_output_devices,
    scan_audio_apps,
    set_default_device,
    set_app_device,
    toggle_mute,
    open_windows_audio_settings,
    get_current_default_device,
    enable_startup,
    is_startup_enabled
)
from config import APP_NAME

# Theme & colors
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
        self.geometry("1000x600")
        self.configure(fg_color=BG_MAIN)
        self.resizable(False, False)

        self.devices = {}
        self.apps = {}

        self._pulse_running = False

        self.build_ui()
        self.refresh_all()

        # start periodic status update
        self.after(1500, self._periodic_status_update)

    # ---------- Build UI ----------
    def build_ui(self):
        # HEADER
        header = ctk.CTkFrame(self, fg_color=BG_MAIN)
        header.pack(fill="x", pady=(10, 0), padx=20)

        title_row = ctk.CTkFrame(header, fg_color=BG_MAIN)
        title_row.pack(fill="x")
        self.title_label = ctk.CTkLabel(
            title_row, text="PEBX  •  SIGNAL MATRIX",
            text_color=ACCENT, font=("Segoe UI", 22, "bold")
        )
        self.title_label.pack(side="left", anchor="w")

        # small pulse indicator
        self.pulse_indicator = ctk.CTkFrame(title_row, width=14, height=14, fg_color=BG_PANEL,
                                            corner_radius=4, border_width=1, border_color=BORDER)
        self.pulse_indicator.pack(side="left", padx=12, pady=4)

        self.status_label = ctk.CTkLabel(
            header, text="● ONLINE  •   DEFAULT: —", text_color="#4CAF50", font=("Segoe UI", 12)
        )
        self.status_label.pack(anchor="w", pady=(6, 10))

        # MAIN GRID
        main_frame = ctk.CTkFrame(self, fg_color=BG_MAIN)
        main_frame.pack(fill="both", expand=True, padx=20)

        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # GLOBAL PANEL
        global_panel = ctk.CTkFrame(main_frame, fg_color=BG_PANEL, corner_radius=8,
                                    border_width=1, border_color=BORDER)
        global_panel.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(global_panel, text="GLOBAL OUTPUT", text_color=ACCENT,
                     font=("Segoe UI", 14, "bold")).pack(pady=(20, 10))

        self.global_device_dropdown = ctk.CTkOptionMenu(global_panel, values=["Loading..."],
                                                        fg_color=BG_PANEL, button_color=ACCENT,
                                                        button_hover_color="#00B8CC")
        self.global_device_dropdown.pack(pady=10, padx=30, fill="x")

        ctk.CTkButton(global_panel, text="APPLY DEVICE", fg_color=ACCENT, hover_color="#00B8CC",
                      text_color="black", command=self._apply_global_device_with_pulse).pack(pady=20, padx=30, fill="x")

        # APP PANEL
        app_panel = ctk.CTkFrame(main_frame, fg_color=BG_PANEL, corner_radius=8,
                                 border_width=1, border_color=BORDER)
        app_panel.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(app_panel, text="APPLICATION ROUTING", text_color=ACCENT,
                     font=("Segoe UI", 14, "bold")).pack(pady=(20, 10))

        self.app_dropdown = ctk.CTkOptionMenu(app_panel, values=["No Apps"], fg_color=BG_PANEL,
                                              button_color=ACCENT, button_hover_color="#00B8CC")
        self.app_dropdown.pack(pady=10, padx=30, fill="x")

        self.app_device_dropdown = ctk.CTkOptionMenu(app_panel, values=["Select Device"], fg_color=BG_PANEL,
                                                     button_color=ACCENT, button_hover_color="#00B8CC")
        self.app_device_dropdown.pack(pady=10, padx=30, fill="x")

        ctk.CTkButton(app_panel, text="APPLY ROUTE", fg_color=ACCENT, hover_color="#00B8CC",
                      text_color="black", command=self._apply_app_with_pulse).pack(pady=20, padx=30, fill="x")

        # FOOTER
        footer = ctk.CTkFrame(self, fg_color=BG_PANEL, corner_radius=0, border_width=1, border_color=BORDER)
        footer.pack(fill="x", padx=20, pady=(0, 20))
        footer.columnconfigure((0, 1, 2, 3), weight=1)

        ctk.CTkButton(footer, text="MUTE", fg_color=BG_PANEL, hover_color=ACCENT, border_width=1,
                      border_color=BORDER, command=self._mute_and_pulse).grid(row=0, column=0, padx=10, pady=15, sticky="ew")

        ctk.CTkButton(footer, text="WINDOWS MIXER", fg_color=BG_PANEL, hover_color=ACCENT, border_width=1,
                      border_color=BORDER, command=open_windows_audio_settings).grid(row=0, column=1, padx=10, pady=15, sticky="ew")

        ctk.CTkButton(footer, text="REFRESH", fg_color=BG_PANEL, hover_color=ACCENT, border_width=1,
                      border_color=BORDER, command=self.refresh_all).grid(row=0, column=2, padx=10, pady=15, sticky="ew")

        # autostart toggle
        self.autostart_toggle = ctk.CTkButton(footer, text="Auto-Start: Checking...", fg_color=BG_PANEL,
                                              hover_color=ACCENT, border_width=1, border_color=BORDER,
                                              command=self._toggle_autostart)
        self.autostart_toggle.grid(row=0, column=3, padx=10, pady=15, sticky="ew")

    # ---------- periodic status update ----------
    def _periodic_status_update(self):
        try:
            current = get_current_default_device()
            if current:
                self.status_label.configure(text=f"● ONLINE  •   DEFAULT: {current}")
            else:
                self.status_label.configure(text="● ONLINE  •   DEFAULT: —")
            # update autostart label
            self._update_autostart_label()
        except Exception:
            pass
        finally:
            # schedule next
            self.after(2000, self._periodic_status_update)

    def _update_autostart_label(self):
        if is_startup_enabled():
            self.autostart_toggle.configure(text="Auto-Start: ON")
        else:
            self.autostart_toggle.configure(text="Auto-Start: OFF")

    # ---------- PULSE animation ----------
    def _pulse_animation(self, cycles=3, interval=120):
        if self._pulse_running:
            return
        self._pulse_running = True

        def pulse():
            try:
                for _ in range(cycles):
                    # highlight
                    self.pulse_indicator.configure(fg_color=ACCENT, border_color=ACCENT)
                    time.sleep(interval / 1000.0)
                    # back
                    self.pulse_indicator.configure(fg_color=BG_PANEL, border_color=BORDER)
                    time.sleep(interval / 1000.0)
            finally:
                self._pulse_running = False

        t = threading.Thread(target=pulse, daemon=True)
        t.start()

    # ---------- apply wrappers that pulse ----------
    def _apply_global_device_with_pulse(self):
        self.apply_global_device()
        self._pulse_animation()

    def _apply_app_with_pulse(self):
        self.apply_app_routing()
        self._pulse_animation()

    def _mute_and_pulse(self):
        toggle_mute()
        self._pulse_animation()

    # ---------- AUTOSTART toggle ----------
    def _toggle_autostart(self):
        current = is_startup_enabled()
        success = enable_startup(not current)
        if success:
            # small UI update
            self._update_autostart_label()

    # ---------- Refresh ----------
    def refresh_all(self):
        self.refresh_devices()
        self.refresh_apps()
        self._update_autostart_label()

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
            self.app_dropdown.configure(values=["No Active Apps"])
            self.app_dropdown.set("No Active Apps")

    # ---------- Actions ----------
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
