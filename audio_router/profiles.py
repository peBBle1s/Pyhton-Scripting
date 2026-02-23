import json
import os
import ctypes
from config import PROFILES_FILE, logger

def load_profiles():
    if not os.path.exists(PROFILES_FILE):
        return {}
    try:
        with open(PROFILES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load profiles: {e}")
        return {}

def save_profiles(profiles):
    try:
        # 0. UN-CLOAK
        if os.path.exists(PROFILES_FILE):
            try:
                ctypes.windll.kernel32.SetFileAttributesW(PROFILES_FILE, 0x80)
            except Exception: pass
            
        # 1. WRITE
        with open(PROFILES_FILE, "w", encoding="utf-8") as f:
            json.dump(profiles, f, indent=4)
            
        # 2. RE-CLOAK
        try:
            ctypes.windll.kernel32.SetFileAttributesW(PROFILES_FILE, 0x02)
        except Exception: pass
    except Exception as e:
        logger.error(f"Failed to save profiles: {e}")

def save_profile(name, device_id):
    profiles = load_profiles()
    profiles[name] = device_id
    save_profiles(profiles)

def get_profile(name):
    profiles = load_profiles()
    return profiles.get(name)