# gui.py
import customtkinter as ctk
import threading
import time
import os
import base64
import json
import ctypes
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox
from router import (
    scan_output_devices, scan_audio_apps, set_default_device,
    set_app_device, toggle_mute, open_windows_audio_settings,
    get_current_default_device, enable_startup, is_startup_enabled
)
from foreground import get_foreground_process
from profiles import (
    get_profile, save_profile, add_app_to_profile, apply_profile, 
    BASE_PROFILES, get_custom_profiles, create_custom_profile, delete_custom_profile
)
from config import APP_NAME, LOG_FILE, STATE_FILE, LOGO_APP, logger

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
        
        # --- WINDOWS TASKBAR OVERRIDE ---
        # Forces Windows to treat this as a unique app, revealing the logo on the taskbar
        try:
            myappid = 'pebx.signalmatrix.app.1.0'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception as e:
            logger.debug(f"Taskbar override bypassed: {e}")
        # --------------------------------

        self.title(f"{APP_NAME} — Signal Control")
        self.geometry("1000x720")
        self.configure(fg_color=BG_MAIN)
        self.resizable(False, False)

        # --- THE NATIVE ICO LOADER ---
        if os.path.exists(LOGO_APP):
            try:
                # The native, bulletproof method for true .ico files
                self.iconbitmap(LOGO_APP)
                logger.info("Application ICO logo successfully mounted.")
            except Exception as e:
                logger.error(f"Failed to mount ICO logo: {e}")
        else:
            logger.warning(f"App logo ({LOGO_APP}) missing. Taskbar will use default.")
        # -----------------------------

        self.devices = {}
        self.apps = {}
        self.current_default_cache = None
        self._pulse_running = False
        self.saved_app_routes = {}
        
        # Memory for The Brain
        self.last_foreground_app = None
        self.auto_switch_enabled = ctk.BooleanVar(value=False)

        self.build_ui()
        self.refresh_all()
        self.load_state()

        # Start background threads
        self.after(1500, self._periodic_status_update)
        self.after(2000, self._foreground_watcher_loop)

    # ---------- Build UI ----------
    def build_ui(self):
        header = ctk.CTkFrame(self, fg_color=BG_MAIN)
        header.pack(fill="x", pady=(10, 0), padx=20)

        title_row = ctk.CTkFrame(header, fg_color=BG_MAIN)
        title_row.pack(fill="x")
        self.title_label = ctk.CTkLabel(
            title_row, text="PEBX  •  SIGNAL MATRIX",
            text_color=ACCENT, font=("Segoe UI", 22, "bold")
        )
        self.title_label.pack(side="left", anchor="w")

        self.pulse_indicator = ctk.CTkFrame(title_row, width=14, height=14, fg_color=BG_PANEL,
                                            corner_radius=4, border_width=1, border_color=BORDER)
        self.pulse_indicator.pack(side="left", padx=12, pady=4)

        self.status_label = ctk.CTkLabel(
            header, text="● ENGINE ACTIVE  •   DEFAULT: —", text_color="#4CAF50", font=("Segoe UI", 12)
        )
        self.status_label.pack(anchor="w", pady=(6, 10))

        self.tabview = ctk.CTkTabview(self, fg_color=BG_MAIN, segmented_button_selected_color=ACCENT, 
                                      segmented_button_selected_hover_color="#00B8CC", text_color="white")
        self.tabview.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        tab_routing = self.tabview.add("Routing Matrix")
        tab_reports = self.tabview.add("Live Reports")

        tab_routing.columnconfigure(0, weight=1)
        tab_routing.columnconfigure(1, weight=1)

        # 1. GLOBAL PANEL
        global_panel = ctk.CTkFrame(tab_routing, fg_color=BG_PANEL, corner_radius=8, border_width=1, border_color=BORDER)
        global_panel.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(global_panel, text="GLOBAL OUTPUT", text_color=ACCENT, font=("Segoe UI", 14, "bold")).pack(pady=(20, 10))

        self.global_device_dropdown = ctk.CTkOptionMenu(global_panel, values=["Loading..."], fg_color=BG_PANEL, button_color=ACCENT, button_hover_color="#00B8CC")
        self.global_device_dropdown.pack(pady=10, padx=30, fill="x")

        ctk.CTkButton(global_panel, text="APPLY DEVICE", fg_color=ACCENT, hover_color="#00B8CC", text_color="black", command=self._apply_global_device_with_pulse).pack(pady=20, padx=30, fill="x")

        # 2. APP PANEL
        app_panel = ctk.CTkFrame(tab_routing, fg_color=BG_PANEL, corner_radius=8, border_width=1, border_color=BORDER)
        app_panel.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(app_panel, text="APPLICATION ROUTING", text_color=ACCENT, font=("Segoe UI", 14, "bold")).pack(pady=(15, 5))

        self.app_dropdown = ctk.CTkOptionMenu(app_panel, values=["No Apps"], fg_color=BG_PANEL, button_color=ACCENT, button_hover_color="#00B8CC")
        self.app_dropdown.pack(pady=5, padx=30, fill="x")

        self.app_device_dropdown = ctk.CTkOptionMenu(app_panel, values=["Select Device"], fg_color=BG_PANEL, button_color=ACCENT, button_hover_color="#00B8CC")
        self.app_device_dropdown.pack(pady=5, padx=30, fill="x")

        ctk.CTkButton(app_panel, text="APPLY ROUTE", fg_color=ACCENT, hover_color="#00B8CC", text_color="black", command=self._apply_app_with_pulse).pack(pady=10, padx=30, fill="x")

        self.brain_toggle = ctk.CTkSwitch(app_panel, text="Enable Smart Brain (Auto-Switch)  [WORK IN PROGRESS]", text_color="#FFA500", variable=self.auto_switch_enabled, progress_color="#4CAF50")
        self.brain_toggle.pack(pady=5, padx=30, fill="x")

        ctk.CTkButton(app_panel, text="SAVE AS AUTO-PROFILE", fg_color="#4CAF50", hover_color="#45a049", text_color="black", command=self._save_auto_profile_with_pulse).pack(pady=(5, 15), padx=30, fill="x")

        # 3. PROFILE MATRIX BUILDER
        self.profile_frame = ctk.CTkFrame(tab_routing, fg_color=BG_PANEL, border_color=BORDER, border_width=1)
        self.profile_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(self.profile_frame, text="PROFILE MATRIX BUILDER", font=("Segoe UI", 14, "bold"), text_color=ACCENT).pack(pady=(10, 5))
        
        prof_row = ctk.CTkFrame(self.profile_frame, fg_color="transparent")
        prof_row.pack(pady=5, fill="x", padx=10)
        
        ctk.CTkLabel(prof_row, text="Select Profile:").pack(side="left", padx=(10, 5))
        
        self.profile_name_entry = ctk.CTkComboBox(prof_row, values=BASE_PROFILES, width=130)
        self.profile_name_entry.pack(side="left", padx=5)
        
        self.btn_add_prof = ctk.CTkButton(prof_row, text="+", width=30, fg_color=ACCENT, text_color="black", hover_color="#00B8CC", command=self.gui_create_profile)
        self.btn_add_prof.pack(side="left", padx=2)
        self.btn_del_prof = ctk.CTkButton(prof_row, text="-", width=30, fg_color="#FF3B30", hover_color="#CC2E26", command=self.gui_delete_profile)
        self.btn_del_prof.pack(side="left", padx=2)
        
        ctk.CTkLabel(prof_row, text="Target App:").pack(side="left", padx=(15, 5))
        self.profile_app_dropdown = ctk.CTkComboBox(prof_row, values=["No Apps"], width=160)
        self.profile_app_dropdown.pack(side="left", padx=5)
        
        ctk.CTkLabel(prof_row, text="Assign Device:").pack(side="left", padx=(15, 5))
        self.profile_device_dropdown = ctk.CTkComboBox(prof_row, values=["No Devices"], width=180)
        self.profile_device_dropdown.pack(side="left", padx=5)
        
        btn_prof_row = ctk.CTkFrame(self.profile_frame, fg_color="transparent")
        btn_prof_row.pack(pady=(10, 15))
        
        ctk.CTkButton(btn_prof_row, text="SAVE TO MATRIX", fg_color=ACCENT, text_color="black", hover_color="#00B8CC", command=self.save_to_profile_matrix).pack(side="left", padx=10)
        ctk.CTkButton(btn_prof_row, text="TEST PROFILE NOW", border_color=ACCENT, border_width=1, fg_color="transparent", hover_color=BORDER, command=self.test_profile).pack(side="left", padx=10)

        # 4. LIVE REPORTS TAB
        ctk.CTkLabel(tab_reports, text="SYSTEM AUDIT LOG (Last 15 Events)", text_color=ACCENT, font=("Segoe UI", 14, "bold")).pack(pady=(10, 5), anchor="w", padx=10)
        self.log_textbox = ctk.CTkTextbox(tab_reports, fg_color=BG_PANEL, text_color="#00FF41", font=("Consolas", 12), border_width=1, border_color=BORDER)
        self.log_textbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.log_textbox.insert("1.0", "Waiting for telemetry...")
        self.log_textbox.configure(state="disabled")

        # 5. FOOTER
        footer = ctk.CTkFrame(self, fg_color=BG_PANEL, corner_radius=0, border_width=1, border_color=BORDER)
        footer.pack(fill="x", padx=20, pady=(0, 20))
        footer.columnconfigure((0, 1, 2, 3, 4), weight=1)

        ctk.CTkButton(footer, text="MUTE", fg_color=BG_PANEL, hover_color=ACCENT, border_width=1, border_color=BORDER, command=self._mute_and_pulse).grid(row=0, column=0, padx=5, pady=15, sticky="ew")
        ctk.CTkButton(footer, text="WINDOWS MIXER", fg_color=BG_PANEL, hover_color=ACCENT, border_width=1, border_color=BORDER, command=open_windows_audio_settings).grid(row=0, column=1, padx=5, pady=15, sticky="ew")
        ctk.CTkButton(footer, text="REFRESH", fg_color=BG_PANEL, hover_color=ACCENT, border_width=1, border_color=BORDER, command=self.refresh_all).grid(row=0, column=2, padx=5, pady=15, sticky="ew")
        self.autostart_toggle = ctk.CTkButton(footer, text="Auto-Start: Checking...", fg_color=BG_PANEL, hover_color=ACCENT, border_width=1, border_color=BORDER, command=self._toggle_autostart)
        self.autostart_toggle.grid(row=0, column=3, padx=5, pady=15, sticky="ew")
        ctk.CTkButton(footer, text="COLLECT LOGS", fg_color="#FF3B30", hover_color="#CC2E26", border_width=1, border_color=BORDER, text_color="white", command=self._extract_diagnostic_report).grid(row=0, column=4, padx=5, pady=15, sticky="ew")

    # ---------- Custom Profile Management ----------
    def gui_create_profile(self):
        dialog = ctk.CTkInputDialog(text="Enter new Profile Name:", title="Create Custom Profile")
        name = dialog.get_input()
        
        if name:
            success, msg = create_custom_profile(name)
            if success:
                self.refresh_profiles()
                self.profile_name_entry.set(name)
                self._update_live_reports()
            else:
                messagebox.showwarning("Creation Blocked", msg)

    def gui_delete_profile(self):
        target = self.profile_name_entry.get()
        if target in BASE_PROFILES:
            messagebox.showwarning("Deletion Blocked", "Core base profiles cannot be deleted.")
            return
            
        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to permanently delete the '{target}' profile?")
        if confirm:
            success, msg = delete_custom_profile(target)
            if success:
                self.refresh_profiles()
                self._update_live_reports()
            else:
                messagebox.showerror("Error", msg)

    def refresh_profiles(self):
        all_profiles = BASE_PROFILES + get_custom_profiles()
        self.profile_name_entry.configure(values=all_profiles)
        
        if self.profile_name_entry.get() not in all_profiles:
            self.profile_name_entry.set(all_profiles[0])

    # ---------- Profile Matrix Execution ----------
    def save_to_profile_matrix(self):
        profile_name = self.profile_name_entry.get()
        app_name = self.profile_app_dropdown.get()
        device_name = self.profile_device_dropdown.get()
        
        if app_name in self.apps and device_name in self.devices:
            exe_name = self.apps[app_name]
            device_id = self.devices[device_name]
            add_app_to_profile(profile_name, exe_name, device_id)
            messagebox.showinfo("Matrix Updated", f"Assigned '{exe_name}' to '{device_name}' under the '{profile_name}' profile.")
            self._update_live_reports()
        else:
            messagebox.showwarning("Invalid Matrix", "Please ensure an active app and valid device are selected.")

    def test_profile(self):
        profile_name = self.profile_name_entry.get()
        apply_profile(profile_name, set_app_device)
        self._pulse_animation()

    # ---------- THE BRAIN (Foreground Watcher) ----------
    def _foreground_watcher_loop(self):
        try:
            if self.auto_switch_enabled.get():
                active_exe = get_foreground_process()
                if active_exe and active_exe != self.last_foreground_app:
                    self.last_foreground_app = active_exe
                    target_device_id = get_profile(active_exe)
                    
                    if target_device_id:
                        logger.info(f"[BRAIN] Target locked: '{active_exe}'. Applying auto-route.")
                        set_app_device(target_device_id, active_exe)
                        self._update_live_reports()
        except Exception as e:
            logger.debug(f"Brain loop error: {e}")
        finally:
            self.after(2000, self._foreground_watcher_loop) 

    def _save_auto_profile_with_pulse(self):
        app_name = self.app_dropdown.get()
        device_name = self.app_device_dropdown.get()
        if app_name in self.apps and device_name in self.devices:
            exe_name = self.apps[app_name]
            device_id = self.devices[device_name]
            save_profile(exe_name, device_id)
            logger.info(f"[BRAIN] Saved Auto-Profile: '{exe_name}' -> '{device_name}'")
            self._update_live_reports()
            self.save_state()
        self._pulse_animation()

    # ---------- STATE MANAGEMENT (Memory) ----------
    def load_state(self):
        if not os.path.exists(STATE_FILE):
            return
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                state = json.load(f)
                
            global_dev = state.get("global_device")
            if global_dev and global_dev in self.devices:
                self.global_device_dropdown.set(global_dev)
                set_default_device(self.devices[global_dev])
                logger.info(f"[MEMORY] Restored Global Device: {global_dev}")

            routes = state.get("app_routes", {})
            for app_name, dev_name in routes.items():
                if app_name in self.apps and dev_name in self.devices:
                    self.saved_app_routes[app_name] = dev_name
                    set_app_device(self.devices[dev_name], self.apps[app_name])
                    logger.info(f"[MEMORY] Restored Route: {app_name} -> {dev_name}")
                    
        except Exception as e:
            logger.error(f"[MEMORY] Failed to load state: {e}")

    def save_state(self):
        state = {
            "global_device": self.global_device_dropdown.get(),
            "app_routes": self.saved_app_routes
        }
        try:
            if os.path.exists(STATE_FILE):
                try: ctypes.windll.kernel32.SetFileAttributesW(STATE_FILE, 0x80)
                except Exception: pass

            with open(STATE_FILE, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=4)
            
            try: ctypes.windll.kernel32.SetFileAttributesW(STATE_FILE, 0x02)
            except Exception: pass 
                
            logger.info("[MEMORY] Application state successfully saved and hidden.")
            self._update_live_reports()
        except Exception as e:
            logger.error(f"[MEMORY] Failed to save state: {e}")

    # ---------- Diagnostic Extraction & Live Reports ----------
    def _update_live_reports(self):
        if not os.path.exists(LOG_FILE):
            return
        try:
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            recent_lines = lines[-15:]
            display_text = ""
            for line in recent_lines:
                clean_line = line.strip()
                if clean_line:
                    try:
                        decoded = base64.b64decode(clean_line).decode('utf-8')
                        display_text += decoded + "\n"
                    except Exception:
                        pass

            self.log_textbox.configure(state="normal")
            self.log_textbox.delete("1.0", "end")
            self.log_textbox.insert("1.0", display_text)
            self.log_textbox.yview("end")
            self.log_textbox.configure(state="disabled")
        except Exception as e:
            logger.debug(f"Live report update error: {e}")

    def _extract_diagnostic_report(self):
        if not os.path.exists(LOG_FILE):
            messagebox.showinfo("No Data", "No diagnostic logs found to collect.")
            return

        dest = filedialog.asksaveasfilename(defaultextension=".txt", initialfile="PebX_Diagnostic_Report.txt", title="Save Diagnostic Report", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if not dest: return

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
            self._update_live_reports() 
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
        if self._pulse_running: return
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
        threading.Thread(target=pulse, daemon=True).start()

    # ---------- apply wrappers that pulse ----------
    def _apply_global_device_with_pulse(self):
        self.apply_global_device()
        self.save_state()
        self._pulse_animation()

    def _apply_app_with_pulse(self):
        self.apply_app_routing()
        self.save_state()
        self._pulse_animation()

    def _mute_and_pulse(self):
        toggle_mute()
        self.save_state()
        self._pulse_animation()

    def _toggle_autostart(self):
        current = is_startup_enabled()
        if enable_startup(not current):
            self._update_autostart_label()
        self.save_state()

    def refresh_all(self):
        logger.info("Manual refresh triggered by user.")
        self.refresh_devices()
        self.refresh_apps()
        self.refresh_profiles()
        self._update_autostart_label()
        self._update_live_reports()
        self.save_state()

    def refresh_devices(self):
        self.devices = scan_output_devices()
        if self.devices:
            names = list(self.devices.keys())
            self.global_device_dropdown.configure(values=names)
            self.app_device_dropdown.configure(values=names)
            self.profile_device_dropdown.configure(values=names)
            
            if self.global_device_dropdown.get() not in names: self.global_device_dropdown.set(names[0])
            if self.app_device_dropdown.get() not in names: self.app_device_dropdown.set(names[0])
            if self.profile_device_dropdown.get() not in names: self.profile_device_dropdown.set(names[0])
        else:
            self.global_device_dropdown.configure(values=["No Devices"])
            self.app_device_dropdown.configure(values=["No Devices"])
            self.profile_device_dropdown.configure(values=["No Devices"])

    def refresh_apps(self):
        self.apps = scan_audio_apps()
        if self.apps:
            names = list(self.apps.keys())
            self.app_dropdown.configure(values=names)
            self.profile_app_dropdown.configure(values=names)
            
            if self.app_dropdown.get() not in names: self.app_dropdown.set(names[0])
            if self.profile_app_dropdown.get() not in names: self.profile_app_dropdown.set(names[0])
        else:
            self.app_dropdown.configure(values=["No Active Apps"])
            self.app_dropdown.set("No Active Apps")
            self.profile_app_dropdown.configure(values=["No Active Apps"])
            self.profile_app_dropdown.set("No Active Apps")

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
            self.saved_app_routes[app_name] = device_name