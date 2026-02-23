import win32gui
import win32process
import psutil
from config import logger

def get_foreground_process():
    """Detects the active window and safely handles permission errors."""
    try:
        hwnd = win32gui.GetForegroundWindow()
        if hwnd:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            return psutil.Process(pid).name()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass # Expected background OS behavior, ignore safely
    except Exception as e:
        logger.debug(f"Foreground tracking error: {e}")
    return None