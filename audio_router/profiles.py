# profiles.py
import json
import os
import ctypes
from config import PROFILES_FILE, logger

BASE_PROFILES = ["Gaming", "Work", "Meeting"]
MAX_CUSTOM_PROFILES = 2

def load_profiles():
    """Tracks and loads saved routing states."""
    if not os.path.exists(PROFILES_FILE):
        return {}
    try:
        with open(PROFILES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load profiles: {e}")
        return {}

def save_profiles(profiles):
    """Safely writes profile data while maintaining stealth attributes."""
    try:
        if os.path.exists(PROFILES_FILE):
            try: ctypes.windll.kernel32.SetFileAttributesW(PROFILES_FILE, 0x80)
            except Exception: pass
            
        with open(PROFILES_FILE, "w", encoding="utf-8") as f:
            json.dump(profiles, f, indent=4)
            
        try: ctypes.windll.kernel32.SetFileAttributesW(PROFILES_FILE, 0x02)
        except Exception: pass
    except Exception as e:
        logger.error(f"Failed to save profiles: {e}")

# --- Custom Profile Management (The Acids & Validation) ---

def get_custom_profiles():
    """Tracks the current active custom profiles."""
    profiles = load_profiles()
    # Filter out base profiles and direct 1:1 auto-switch mappings (usually ending in .exe)
    customs = [p for p in profiles.keys() if p not in BASE_PROFILES and not p.lower().endswith(".exe")]
    return customs

def create_custom_profile(name):
    """Safely constructs a new profile if limits allow."""
    if not name or name.strip() == "":
        return False, "Profile name cannot be empty."
        
    name = name.strip()
    profiles = load_profiles()
    
    if name in BASE_PROFILES or name in profiles:
        return False, "Profile already exists."
        
    customs = get_custom_profiles()
    if len(customs) >= MAX_CUSTOM_PROFILES:
        return False, f"Maximum of {MAX_CUSTOM_PROFILES} custom profiles reached."
        
    profiles[name] = {}
    save_profiles(profiles)
    logger.info(f"Created new custom profile matrix: {name}")
    return True, "Profile created successfully."

def delete_custom_profile(name):
    """Removes a custom profile, shielding base profiles from deletion."""
    if name in BASE_PROFILES:
        return False, "Core base profiles cannot be deleted."
        
    profiles = load_profiles()
    if name in profiles:
        del profiles[name]
        save_profiles(profiles)
        logger.info(f"Deleted custom profile matrix: {name}")
        return True, "Profile deleted successfully."
        
    return False, "Profile not found."

# --- The Smart Brain Functions (Direct 1:1 Mapping) ---

def save_profile(name, device_id):
    profiles = load_profiles()
    profiles[name] = device_id
    save_profiles(profiles)

def get_profile(name):
    profiles = load_profiles()
    data = profiles.get(name)
    if isinstance(data, str):
        return data
    return None

# --- The Matrix Builder Functions (Grouped Mapping) ---

def add_app_to_profile(profile_name, app_name, device_id):
    profiles = load_profiles()
    if profile_name not in profiles or not isinstance(profiles[profile_name], dict):
        profiles[profile_name] = {}
    profiles[profile_name][app_name] = device_id
    save_profiles(profiles)
    logger.info(f"Assigned {app_name} to {profile_name} matrix.")

def apply_profile(profile_name, routing_function):
    profiles = load_profiles()
    if profile_name in profiles:
        target_data = profiles[profile_name]
        if isinstance(target_data, dict):
            for app_name, device_id in target_data.items():
                routing_function(device_id, app_name)
            logger.info(f"Successfully applied profile matrix: {profile_name}")
        elif isinstance(target_data, str):
            routing_function(target_data, profile_name)
    else:
        logger.warning(f"Profile '{profile_name}' lacks essential tracking data in JSON.")