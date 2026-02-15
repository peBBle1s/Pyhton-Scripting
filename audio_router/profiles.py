import json
import os
from config import PROFILES_FILE


def load_profiles():
    if not os.path.exists(PROFILES_FILE):
        return {}

    with open(PROFILES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_profiles(profiles):
    with open(PROFILES_FILE, "w", encoding="utf-8") as f:
        json.dump(profiles, f, indent=4)


def save_profile(name, device_id):
    profiles = load_profiles()
    profiles[name] = device_id
    save_profiles(profiles)


def get_profile(name):
    profiles = load_profiles()
    return profiles.get(name)
