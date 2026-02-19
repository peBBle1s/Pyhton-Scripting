# main.py
from gui import PebXGUI
from tray import start_tray

if __name__ == "__main__":
    app = PebXGUI()
    # start system tray in background
    start_tray(app)
    app.mainloop()
