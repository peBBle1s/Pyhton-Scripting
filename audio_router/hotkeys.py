import keyboard
from profiles import apply_profile
from router import route_app

def register_hotkeys():
    keyboard.add_hotkey("ctrl+alt+1", lambda: apply_profile("Gaming", route_app))
    keyboard.add_hotkey("ctrl+alt+2", lambda: apply_profile("Work", route_app))
    keyboard.add_hotkey("ctrl+alt+3", lambda: apply_profile("Meeting", route_app))
