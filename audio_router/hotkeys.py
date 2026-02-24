import keyboard
from profiles import apply_profile
from router import set_app_device  

def register_hotkeys():
    """Registers global shortcuts to trigger full profile matrices."""
    
    # Trigger all apps assigned to "Gaming"
    keyboard.add_hotkey("ctrl+alt+1", lambda: apply_profile("Gaming", set_app_device))
    
    # Trigger all apps assigned to "Work"
    keyboard.add_hotkey("ctrl+alt+2", lambda: apply_profile("Work", set_app_device))
    
    # Trigger all apps assigned to "Meeting"
    keyboard.add_hotkey("ctrl+alt+3", lambda: apply_profile("Meeting", set_app_device))