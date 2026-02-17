import subprocess
import csv
from config import SOUND_VOLUME_VIEW, DEVICES_FILE


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
                    name = row.get("Name")
                    device_id = row.get("Item ID")

                    if name and device_id:
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
