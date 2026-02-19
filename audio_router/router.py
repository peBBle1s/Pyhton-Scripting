# router.py
import subprocess
import csv
import os
import sys
import winreg
from config import SOUND_VOLUME_VIEW, DEVICES_FILE

# -------------------- DEVICE SCAN --------------------

def _generate_csv():
    """Run SoundVolumeView to regenerate devices.csv (silent)."""
    try:
        subprocess.run(
            [SOUND_VOLUME_VIEW, "/scomma", DEVICES_FILE],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False
        )
    except Exception:
        pass


def scan_output_devices():
    devices = {}
    _generate_csv()

    try:
        with open(DEVICES_FILE, newline="", encoding="utf-8-sig") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row.get("Type") == "Device" and row.get("Direction") == "Render":
                    friendly_name = row.get("Device Name") or row.get("Name")
                    device_id = row.get("Item ID")
                    if friendly_name and device_id:
                        devices[friendly_name] = device_id
    except Exception as e:
        print("Device scan error:", e)
    return devices


# -------------------- CURRENT DEFAULT --------------------

def get_current_default_device():
    """
    Returns the friendly name of the current default render device (or None).
    Checks Default, Default Multimedia, and Default Communications columns.
    """
    _generate_csv()
    try:
        with open(DEVICES_FILE, newline="", encoding="utf-8-sig") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row.get("Type") == "Device" and row.get("Direction") == "Render":
                    # Some exports mark the default in different columns.
                    if row.get("Default") == "Render" \
                       or row.get("Default Multimedia") == "Render" \
                       or row.get("Default Communications") == "Render":
                        return row.get("Device Name") or row.get("Name")
    except Exception as e:
        print("Current default read error:", e)
    return None


# -------------------- APP SCAN --------------------

def scan_audio_apps():
    apps = {}
    _generate_csv()

    try:
        with open(DEVICES_FILE, newline="", encoding="utf-8-sig") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row.get("Type") == "Application" and row.get("Process Path"):
                    friendly_name = row.get("Name")
                    process_path = row.get("Process Path")
                    exe_name = os.path.basename(process_path) if process_path else None
                    if friendly_name and exe_name:
                        apps[friendly_name] = exe_name
    except Exception as e:
        print("App scan error:", e)
    return apps


# -------------------- GLOBAL SWITCH --------------------

def set_default_device(device_id):
    try:
        for role in ["0", "1", "2"]:
            subprocess.run(
                [SOUND_VOLUME_VIEW, "/SetDefault", device_id, role],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False
            )
    except Exception as e:
        print("Set default error:", e)


# -------------------- PER APP ROUTING --------------------

def set_app_device(device_id, app_exe):
    try:
        for role in ["0", "1", "2"]:
            subprocess.run(
                [SOUND_VOLUME_VIEW, "/SetAppDefault", device_id, role, app_exe],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False
            )
    except Exception as e:
        print("App routing error:", e)


# -------------------- MUTE / WINDOWS --------------------

def toggle_mute():
    try:
        subprocess.run([SOUND_VOLUME_VIEW, "/Mute", "Toggle"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    except Exception as e:
        print("Mute error:", e)


def open_windows_audio_settings():
    # Safe cross-call to MS settings
    os.system("start ms-settings:apps-volume")


# -------------------- STARTUP (Auto-run) --------------------

_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
_RUN_NAME = "PebX"

def enable_startup(enable: bool):
    """
    Enable or disable autostart at user login.
    When enabled, sets the run key to run the packaged exe if present, else
    uses current python executable + main.py path.
    """
    try:
        exe_path = getattr(sys, "frozen", False) and sys.executable or sys.executable
        # prefer exe if running as exe; otherwise point to python and main.py
        base = os.path.dirname(os.path.abspath(__file__))
        main_py = os.path.join(base, "main.py")
        if getattr(sys, "frozen", False):
            value = f'"{sys.executable}"'
        else:
            # use python -m to avoid store alias issues
            value = f'"{exe_path}" "{main_py}"'

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _RUN_KEY, 0, winreg.KEY_ALL_ACCESS) as key:
            if enable:
                winreg.SetValueEx(key, _RUN_NAME, 0, winreg.REG_SZ, value)
            else:
                try:
                    winreg.DeleteValue(key, _RUN_NAME)
                except FileNotFoundError:
                    pass
        return True
    except Exception as e:
        print("Enable startup error:", e)
        return False


def is_startup_enabled():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _RUN_KEY, 0, winreg.KEY_READ) as key:
            val, _ = winreg.QueryValueEx(key, _RUN_NAME)
            return bool(val)
    except FileNotFoundError:
        return False
    except Exception:
        return False
