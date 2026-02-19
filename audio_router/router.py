import subprocess
import csv
import os
from config import SOUND_VOLUME_VIEW, DEVICES_FILE


# -------------------- DEVICE SCAN --------------------

def scan_output_devices():
    devices = {}

    try:
        subprocess.run(
            [SOUND_VOLUME_VIEW, "/scomma", DEVICES_FILE],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        with open(DEVICES_FILE, newline="", encoding="utf-8-sig") as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                if row.get("Type") == "Device" and row.get("Direction") == "Render":
                    friendly_name = row.get("Device Name")
                    device_id = row.get("Item ID")

                    if friendly_name and device_id:
                        devices[friendly_name] = device_id

    except Exception as e:
        print("Device scan error:", e)

    return devices


# -------------------- APP SCAN --------------------

def scan_audio_apps():
    apps = {}

    try:
        subprocess.run(
            [SOUND_VOLUME_VIEW, "/scomma", DEVICES_FILE],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        with open(DEVICES_FILE, newline="", encoding="utf-8-sig") as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                if row.get("Type") == "Application" and row.get("Process Path"):
                    friendly_name = row.get("Name")
                    process_path = row.get("Process Path")
                    exe_name = os.path.basename(process_path)

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
                stderr=subprocess.DEVNULL
            )
    except Exception as e:
        print("Set default error:", e)


# -------------------- PER APP ROUTING --------------------

def set_app_device(device_id, app_exe):
    try:
        for role in ["0", "1", "2"]:
            subprocess.run(
                [
                    SOUND_VOLUME_VIEW,
                    "/SetAppDefault",
                    device_id,
                    role,
                    app_exe
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
    except Exception as e:
        print("App routing error:", e)


# -------------------- VOLUME CONTROL --------------------

def set_master_volume(volume_percent):
    try:
        subprocess.run(
            [SOUND_VOLUME_VIEW, "/SetVolume", volume_percent],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception as e:
        print("Volume set error:", e)


def toggle_mute():
    try:
        subprocess.run(
            [SOUND_VOLUME_VIEW, "/Mute", "Toggle"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception as e:
        print("Mute error:", e)


# -------------------- WINDOWS MIXER --------------------

def open_windows_audio_settings():
    os.system("start ms-settings:apps-volume")
