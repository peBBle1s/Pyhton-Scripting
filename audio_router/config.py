# config.py
import os
import logging
import base64
import ctypes

APP_NAME = "PebX Signal Matrix"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Core 'Vitamins' (Dependencies & Assets)
SOUND_VOLUME_VIEW = os.path.join(BASE_DIR, "SoundVolumeView.exe")
LOGO_APP = os.path.join(BASE_DIR, "logo1.jpg")   # Top-left window & Taskbar
LOGO_TRAY = os.path.join(BASE_DIR, "logo2.png")  # System tray icon (can also be .ico)

# Data Matrix Paths
DEVICES_FILE = os.path.join(BASE_DIR, "devices.csv")
PROFILES_FILE = os.path.join(BASE_DIR, "profiles.json")

# Memory & Stealth System
STATE_FILE = os.path.join(BASE_DIR, "state.json")
LOG_FILE = os.path.join(BASE_DIR, "sound_matrix_activity.log")

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