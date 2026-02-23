import os
import logging
import base64
import ctypes

APP_NAME = "PebX Audio Router"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SOUND_VOLUME_VIEW = os.path.join(BASE_DIR, "SoundVolumeView.exe")
DEVICES_FILE = os.path.join(BASE_DIR, "devices.csv")
PROFILES_FILE = os.path.join(BASE_DIR, "profiles.json")

# -------------------- MEMORY & STEALTH SYSTEM --------------------
STATE_FILE = os.path.join(BASE_DIR, "state.json")
LOG_FILE = os.path.join(BASE_DIR, "peb_activity.audio.log")

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

# -------------------- DEPENDENCY VALIDATION --------------------
def check_dependencies():
    """Validates that essential routing components exist (Vitamin)."""
    exists = os.path.exists(SOUND_VOLUME_VIEW)
    if not exists:
        logger.critical(f"Missing essential component: {SOUND_VOLUME_VIEW} not found.")
    return exists