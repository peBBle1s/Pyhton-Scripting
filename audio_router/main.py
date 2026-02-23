import sys
import tkinter.messagebox as messagebox
from gui import PebXGUI
from tray import start_tray
from config import check_dependencies, logger

if __name__ == "__main__":
    logger.info("Initializing PebX Signal Matrix...")
    
    # The Safety Check
    if not check_dependencies():
        messagebox.showerror(
            "Critical Error", 
            "SoundVolumeView.exe is missing from the application folder.\n\nThis is essential for routing audio. Please place it in the root directory and restart."
        )
        sys.exit(1)
        
        
    try:
        app = PebXGUI()
        # start system tray in background
        start_tray(app)
        logger.info("Application UI and Tray started successfully. Live tracking active.")
        app.mainloop()
    except Exception as e:
        logger.critical(f"Fatal application crash: {e}")