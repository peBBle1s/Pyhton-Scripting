import customtkinter as ctk
import threading
import time
import os
import base64
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox
from router import (
    scan_output_devices, scan_audio_apps, set_default_device,
    set_app_device, toggle_mute, open_windows_audio_settings,
    get_current_default_device, enable_startup, is_startup_enabled
)
from config import APP_NAME, LOG_FILE, logger

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
        self.current_default_cache = None
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
            header, text="● ENGINE ACTIVE  •   DEFAULT: —", text_color="#4CAF50", font=("Segoe UI", 12)
        )
        self.status_label.pack(anchor="w", pady=(6, 10))

        # ---------------- TABS ----------------
        self.tabview = ctk.CTkTabview(self, fg_color=BG_MAIN, segmented_button_selected_color=ACCENT, 
                                      segmented_button_selected_hover_color="#00B8CC",
                                      text_color="white")
        self.tabview.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        tab_routing = self.tabview.add("Routing Matrix")
        tab_reports = self.tabview.add("Live Reports")

        # --- TAB 1: ROUTING MATRIX ---
        tab_routing.columnconfigure(0, weight=1)
        tab_routing.columnconfigure(1, weight=1)

        # GLOBAL PANEL
        global_panel = ctk.CTkFrame(tab_routing, fg_color=BG_PANEL, corner_radius=8,
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
        app_panel = ctk.CTkFrame(tab_routing, fg_color=BG_PANEL, corner_radius=8,
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

        # --- TAB 2: LIVE REPORTS ---
        ctk.CTkLabel(tab_reports, text="SYSTEM AUDIT LOG (Last 15 Events)", text_color=ACCENT, 
                     font=("Segoe UI", 14, "bold")).pack(pady=(10, 5), anchor="w", padx=10)
        
        self.log_textbox = ctk.CTkTextbox(tab_reports, fg_color=BG_PANEL, text_color="#00FF41", 
                                          font=("Consolas", 12), border_width=1, border_color=BORDER)
        self.log_textbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.log_textbox.insert("1.0", "Waiting for telemetry...")
        self.log_textbox.configure(state="disabled")

        # FOOTER
        footer = ctk.CTkFrame(self, fg_color=BG_PANEL, corner_radius=0, border_width=1, border_color=BORDER)
        footer.pack(fill="x", padx=20, pady=(0, 20))
        footer.columnconfigure((0, 1, 2, 3, 4), weight=1)

        ctk.CTkButton(footer, text="MUTE", fg_color=BG_PANEL, hover_color=ACCENT, border_width=1,
                      border_color=BORDER, command=self._mute_and_pulse).grid(row=0, column=0, padx=5, pady=15, sticky="ew")

        ctk.CTkButton(footer, text="WINDOWS MIXER", fg_color=BG_PANEL, hover_color=ACCENT, border_width=1,
                      border_color=BORDER, command=open_windows_audio_settings).grid(row=0, column=1, padx=5, pady=15, sticky="ew")

        ctk.CTkButton(footer, text="REFRESH", fg_color=BG_PANEL, hover_color=ACCENT, border_width=1,
                      border_color=BORDER, command=self.refresh_all).grid(row=0, column=2, padx=5, pady=15, sticky="ew")

        self.autostart_toggle = ctk.CTkButton(footer, text="Auto-Start: Checking...", fg_color=BG_PANEL,
                                              hover_color=ACCENT, border_width=1, border_color=BORDER,
                                              command=self._toggle_autostart)
        self.autostart_toggle.grid(row=0, column=3, padx=5, pady=15, sticky="ew")

        ctk.CTkButton(footer, text="COLLECT LOGS", fg_color="#FF3B30", hover_color="#CC2E26", border_width=1,
                      border_color=BORDER, text_color="white", command=self._extract_diagnostic_report).grid(row=0, column=4, padx=5, pady=15, sticky="ew")

    # ---------- Diagnostic Extraction & Live Reports ----------
    def _update_live_reports(self):
        """Reads the obfuscated log file, decrypts it, and displays recent events in the UI."""
        if not os.path.exists(LOG_FILE):
            return

        try:
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Grab the last 15 lines to keep the UI clean
            recent_lines = lines[-15:]
            display_text = ""
            for line in recent_lines:
                clean_line = line.strip()
                if clean_line:
                    try:
                        decoded = base64.b64decode(clean_line).decode('utf-8')
                        display_text += decoded + "\n"
                    except Exception:
                        pass # Ignore corrupted lines in live view

            # Safely update the textbox
            self.log_textbox.configure(state="normal")
            self.log_textbox.delete("1.0", "end")
            self.log_textbox.insert("1.0", display_text)
            self.log_textbox.yview("end") # Auto-scroll to bottom
            self.log_textbox.configure(state="disabled")
        except Exception as e:
            logger.debug(f"Live report update error: {e}")

    def _extract_diagnostic_report(self):
        if not os.path.exists(LOG_FILE):
            messagebox.showinfo("No Data", "No diagnostic logs found to collect.")
            return

        dest = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile="PebX_Diagnostic_Report.txt",
            title="Save Diagnostic Report",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        
        if not dest:
            return

        try:
            with open(LOG_FILE, 'r') as f_in, open(dest, 'w', encoding='utf-8') as f_out:
                f_out.write("--- PEBX DIAGNOSTIC REPORT ---\n\n")
                for line in f_in:
                    clean_line = line.strip()
                    if clean_line:
                        try:
                            decoded_bytes = base64.b64decode(clean_line)
                            f_out.write(decoded_bytes.decode('utf-8') + "\n")
                        except Exception:
                            f_out.write(f"[CORRUPTED LINE] {clean_line}\n")
            
            messagebox.showinfo("Success", "Diagnostic report generated. You can now analyze this file.")
            logger.info("User extracted diagnostic reports.")
            self._update_live_reports() # Force refresh the UI
        except Exception as e:
            messagebox.showerror("Error", f"Failed to extract logs: {e}")

    # ---------- periodic status update ----------
    def _periodic_status_update(self):
        try:
            current = get_current_default_device()
            if current:
                self.status_label.configure(text=f"● ENGINE ACTIVE  •   DEFAULT: {current}")
                if self.current_default_cache != current:
                    logger.info(f"System default device detected as: {current}")
                    self.current_default_cache = current
            else:
                self.status_label.configure(text="● ENGINE ACTIVE  •   DEFAULT: —")
            self._update_autostart_label()
            
            # Update the Live Reports tab
            self._update_live_reports()
        except Exception as e:
            logger.debug(f"Status update cycle error: {e}")
        finally:
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
                    self.pulse_indicator.configure(fg_color=ACCENT, border_color=ACCENT)
                    time.sleep(interval / 1000.0)
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
            self._update_autostart_label()

    # ---------- Refresh ----------
    def refresh_all(self):
        logger.info("Manual refresh triggered by user.")
        self.refresh_devices()
        self.refresh_apps()
        self._update_autostart_label()
        self._update_live_reports()

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