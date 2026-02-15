import subprocess
import csv
from config import SOUND_VOLUME_VIEW, DEVICES_FILE


def scan_output_devices():
    """
    Returns dictionary:
    {
        "Device Name": "Device ID"
    }
    """

    devices = {}

    try:
        # Generate devices.csv
        subprocess.run(
            [SOUND_VOLUME_VIEW, "/scomma", DEVICES_FILE],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # Read CSV
        with open(DEVICES_FILE, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                if row["Type"] == "Device" and row["Direction"] == "Render":
                    name = row["Name"]
                    device_id = row["Item ID"]
                    devices[name] = device_id

    except Exception as e:
        print("Device scan error:", e)

    return devices


def set_default_device(device_id):
    """
    Sets device as:
    0 = Console default
    2 = Multimedia default
    """

    try:
        subprocess.run(
            [SOUND_VOLUME_VIEW, "/SetDefault", device_id, "0"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        subprocess.run(
            [SOUND_VOLUME_VIEW, "/SetDefault", device_id, "2"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    except Exception as e:
        print("Set default error:", e)
