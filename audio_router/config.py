# config.py
import os
import sys
import logging
import base64
import ctypes

APP_NAME = "PebX Signal Matrix"

# --- THE ONE-FILE PATH FINDER (For Hidden Assets inside the EXE) ---
def get_asset_path(relative_path):
    """Locates assets whether running as a Python script or a PyInstaller One-File EXE."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# --- THE APPDATA VAULT (For Permanent User Memory) ---
# Locate the Windows AppData\Roaming directory
appdata_base = os.getenv('APPDATA')
if not appdata_base:
    # Fallback to the user's home directory if AppData is somehow missing
    appdata_base = os.path.expanduser("~")

# Create a dedicated folder for your brand
USER_DATA_DIR = os.path.join(appdata_base, APP_NAME)

# ESSENTIAL ACID: Force Windows to create the folder if it doesn't exist yet
os.makedirs(USER_DATA_DIR, exist_ok=True)

# Core 'Vitamins' (Using the Path Finder so the App sees them!)
SOUND_VOLUME_VIEW = get_asset_path("SoundVolumeView.exe")
LOGO_APP = get_asset_path("logo2.ico")   
LOGO_TRAY = get_asset_path("logo2.ico")  

# Data Matrix Paths (Saved securely in the new AppData Vault)
DEVICES_FILE = os.path.join(USER_DATA_DIR, "devices.csv")
PROFILES_FILE = os.path.join(USER_DATA_DIR, "profiles.json")
STATE_FILE = os.path.join(USER_DATA_DIR, "state.json")
LOG_FILE = os.path.join(USER_DATA_DIR, "sound_matrix_activity.log")

class ObfuscatedHiddenFileHandler(logging.FileHandler):
    def __init__(self, filename, mode='a', encoding='utf-8', delay=False):
        super().__init__(filename, mode, encoding, delay)
        self._hide_file(filename)

    def _hide_file(self, filepath):
        """Applies the Windows 'Hidden' attribute to the file (Acid/Security)."""
        try:
            ctypes.windll.kernel32.SetFileAttributesW(filepath, 0x02)
        except Exception:
            pass

    def emit(self, record):
        """Intercepts the log, encodes it to unreadable Base64, and writes it."""
        try:
            msg = self.format(record)
            encoded_bytes = base64.b64encode(msg.encode('utf-8'))
            encoded_msg = encoded_bytes.decode('utf-8')
            
            stream = self.stream
            stream.write(encoded_msg + self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)

# Configure essential tracking
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        ObfuscatedHiddenFileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(APP_NAME)

def check_dependencies():
    """Validates that essential routing components are present."""
    if not os.path.exists(SOUND_VOLUME_VIEW):
        logger.critical(f"Missing essential component: {SOUND_VOLUME_VIEW} not found.")
        return False
    return True