import os
import json
from pathlib import Path

BASE_DIR = Path("audio_router")
ASSETS_DIR = BASE_DIR / "assets"

FILES = {
    BASE_DIR / "__init__.py": "",

    BASE_DIR / "main.py": """from tray import start_tray
from hotkeys import register_hotkeys

if __name__ == "__main__":
    print("Starting Audio Router...")
    register_hotkeys()
    start_tray()
""",

    BASE_DIR / "router.py": """import subprocess

SVV_PATH = "SoundVolumeView.exe"

def route_app(app_exe, device_id):
    for role in [0,1,2]:
        subprocess.run([
            SVV_PATH,
            "/SetAppDefault",
            device_id,
            str(role),
            app_exe
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
""",

    BASE_DIR / "profiles.py": """import json

PROFILE_FILE = "profiles.json"

def load_profiles():
    with open(PROFILE_FILE, "r") as f:
        return json.load(f)

def apply_profile(name, route_func):
    profiles = load_profiles()
    if name not in profiles:
        print("Profile not found.")
        return

    for app, device in profiles[name].items():
        route_func(app, device)
""",

    BASE_DIR / "foreground.py": """import win32gui
import win32process
import psutil

def get_foreground_process():
    hwnd = win32gui.GetForegroundWindow()
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    return psutil.Process(pid).name()
""",

    BASE_DIR / "hotkeys.py": """import keyboard
from profiles import apply_profile
from router import route_app

def register_hotkeys():
    keyboard.add_hotkey("ctrl+alt+1", lambda: apply_profile("Gaming", route_app))
    keyboard.add_hotkey("ctrl+alt+2", lambda: apply_profile("Work", route_app))
    keyboard.add_hotkey("ctrl+alt+3", lambda: apply_profile("Meeting", route_app))
""",

    BASE_DIR / "tray.py": """import pystray
from PIL import Image
from profiles import apply_profile
from router import route_app

def start_tray():
    image = Image.new("RGB", (64, 64), color="black")

    menu = pystray.Menu(
        pystray.MenuItem("Gaming Mode", lambda: apply_profile("Gaming", route_app)),
        pystray.MenuItem("Work Mode", lambda: apply_profile("Work", route_app)),
        pystray.MenuItem("Meeting Mode", lambda: apply_profile("Meeting", route_app)),
        pystray.MenuItem("Exit", lambda icon, item: icon.stop())
    )

    icon = pystray.Icon("AudioRouter", image, menu=menu)
    icon.run()
""",

    BASE_DIR / "gui.py": """import customtkinter as ctk

def start_gui():
    app = ctk.CTk()
    app.title("Audio Router")
    app.geometry("400x300")
    app.mainloop()
""",

    BASE_DIR / "config.py": """APP_NAME = "Audio Router"
VERSION = "1.0.0"
""",

    "profiles.json": json.dumps({
        "Gaming": {
            "discord.exe": "HEADSET_DEVICE_ID",
            "chrome.exe": "SPEAKERS_DEVICE_ID"
        },
        "Work": {
            "msedge.exe": "SPEAKERS_DEVICE_ID",
            "teams.exe": "HEADSET_DEVICE_ID"
        },
        "Meeting": {
            "zoom.exe": "HEADSET_DEVICE_ID"
        }
    }, indent=4),

    "requirements.txt": """pywin32
psutil
keyboard
pystray
pillow
customtkinter
""",

    ".gitignore": """__pycache__/
*.pyc
venv/
env/
build/
dist/
*.exe
*.spec
apps.csv
""",

    "README.md": """# Audio Router

Advanced Windows Audio Routing Utility

Features:
- Per-app audio routing
- Profiles (Gaming / Work / Meeting)
- Global hotkeys
- System tray integration

Build EXE:
pip install -r requirements.txt
pyinstaller --onefile --noconsole audio_router/main.py
"""
}

def create_structure():
    BASE_DIR.mkdir(exist_ok=True)
    ASSETS_DIR.mkdir(exist_ok=True)

    for path, content in FILES.items():
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    print("Audio Router project structure created successfully!")

if __name__ == "__main__":
    create_structure()
