import os

APP_NAME = "PebX Audio Router"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SOUND_VOLUME_VIEW = os.path.join(BASE_DIR, "SoundVolumeView.exe")
DEVICES_FILE = os.path.join(BASE_DIR, "devices.csv")
PROFILES_FILE = os.path.join(BASE_DIR, "profiles.json")
