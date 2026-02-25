import sys
import threading
import keyboard
import tkinter.messagebox as messagebox
from gui import PebXGUI
from tray import start_tray
from hotkeys import register_hotkeys
from config import check_dependencies, logger, APP_NAME

def run_hotkey_listener():
    """Essential background thread for shortcut detection."""
    try:
        register_hotkeys()
        # Keeps the thread alive to continuously track key presses
        keyboard.wait()
    except Exception as e:
        logger.error(f"Hotkey tracking failed: {e}")

if __name__ == "__main__":
    logger.info(f"Initializing {APP_NAME}...")
    
    # Essential Dependency Validation
    if not check_dependencies():
        messagebox.showerror(
            "Critical Error", 
            f"SoundVolumeView.exe is missing from the application folder.\n\nThis is essential for {APP_NAME} to perfectly route audio. Please place it in the root directory."
        )
        sys.exit(1)
        
    try:
        app = PebXGUI()
        app.title(f"{APP_NAME} — Signal Control")
        
        # --- LEVEL 3: STEP 1 (METABOLISM START) ---
        # This activates the hardware listener so it can auto-refresh
        app.start_device_watchdog()
        
        # Start the hotkey tracker in a daemon thread so it closes with the app
        hk_thread = threading.Thread(target=run_hotkey_listener, daemon=True)
        hk_thread.start()
        
        # Start system tray tracking
        start_tray(app)
        
        logger.info(f"{APP_NAME} UI and Tray started successfully. Live tracking active.")
        app.mainloop()
    except Exception as e:
        logger.critical(f"Fatal application crash: {e}")