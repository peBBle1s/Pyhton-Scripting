# router.py
import subprocess
import csv
import os
import sys
import winreg
from config import SOUND_VOLUME_VIEW, DEVICES_FILE

# --------------------------------------------------
# INTERNAL
# --------------------------------------------------

def _generate_csv():
    try:
        subprocess.run(
            [SOUND_VOLUME_VIEW, "/scomma", DEVICES_FILE],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False
        )
    except Exception:
        pass


# --------------------------------------------------
# OUTPUT (Render)
# --------------------------------------------------

def scan_output_devices():
    devices = {}
    _generate_csv()

    try:
        with open(DEVICES_FILE, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("Type") == "Device" and row.get("Direction") == "Render":
                    name = row.get("Device Name") or row.get("Name")
                    device_id = row.get("Item ID")
                    if name and device_id:
                        devices[name] = device_id
    except Exception as e:
        print("Output scan error:", e)

    return devices


def get_current_default_output():
    _generate_csv()
    try:
        with open(DEVICES_FILE, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("Type") == "Device" and row.get("Direction") == "Render":
                    if (
                        row.get("Default") == "Render"
                        or row.get("Default Multimedia") == "Render"
                        or row.get("Default Communications") == "Render"
                    ):
                        return row.get("Device Name") or row.get("Name")
    except Exception:
        pass

    return None


# --------------------------------------------------
# INPUT (Microphone / Capture)
# --------------------------------------------------

def scan_input_devices():
    devices = {}
    _generate_csv()

    try:
        with open(DEVICES_FILE, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("Type") == "Device" and row.get("Direction") == "Capture":
                    name = row.get("Device Name") or row.get("Name")
                    device_id = row.get("Item ID")
                    if name and device_id:
                        devices[name] = device_id
    except Exception as e:
        print("Input scan error:", e)

    return devices


def get_current_default_input():
    _generate_csv()
    try:
        with open(DEVICES_FILE, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("Type") == "Device" and row.get("Direction") == "Capture":
                    if (
                        row.get("Default") == "Capture"
                        or row.get("Default Multimedia") == "Capture"
                        or row.get("Default Communications") == "Capture"
                    ):
                        return row.get("Device Name") or row.get("Name")
    except Exception:
        pass

    return None


# --------------------------------------------------
# APPLICATION SCAN
# --------------------------------------------------

def scan_audio_apps():
    apps = {}
    _generate_csv()

    try:
        with open(DEVICES_FILE, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("Type") == "Application" and row.get("Process Path"):
                    friendly_name = row.get("Name")
                    exe_name = os.path.basename(row.get("Process Path"))
                    if friendly_name and exe_name:
                        apps[friendly_name] = exe_name
    except Exception as e:
        print("App scan error:", e)

    return apps


# --------------------------------------------------
# GLOBAL SWITCH
# --------------------------------------------------

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


# --------------------------------------------------
# PER APP ROUTING
# --------------------------------------------------

def set_app_device(device_id, exe_name):
    try:
        for role in ["0", "1", "2"]:
            subprocess.run(
                [SOUND_VOLUME_VIEW, "/SetAppDefault", device_id, role, exe_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False
            )
    except Exception as e:
        print("App routing error:", e)


# --------------------------------------------------
# MISC
# --------------------------------------------------

def toggle_mute():
    subprocess.run(
        [SOUND_VOLUME_VIEW, "/Mute", "Toggle"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False
    )


def open_windows_audio_settings():
    os.system("start ms-settings:apps-volume")


# --------------------------------------------------
# STARTUP
# --------------------------------------------------

_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
_RUN_NAME = "PebX"

def enable_startup(enable: bool):
    try:
        exe_path = sys.executable
        base = os.path.dirname(os.path.abspath(__file__))
        main_py = os.path.join(base, "main.py")

        if getattr(sys, "frozen", False):
            value = f'"{exe_path}"'
        else:
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
    except Exception:
        return False


def is_startup_enabled():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _RUN_KEY, 0, winreg.KEY_READ) as key:
            val, _ = winreg.QueryValueEx(key, _RUN_NAME)
            return bool(val)
    except Exception:
        return False