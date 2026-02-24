# tray.py
import threading
import sys
import os
from PIL import Image, ImageDraw
import pystray
from router import is_startup_enabled, enable_startup
from config import LOGO_TRAY, APP_NAME, logger

ICON_SIZE = 64
ACCENT = (0, 229, 255)

def _make_icon():
    # simple circular cyan icon on transparent background
    img = Image.new('RGBA', (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    r = 18
    cx, cy = ICON_SIZE//2, ICON_SIZE//2
    draw.ellipse((cx-r, cy-r, cx+r, cy+r), fill=ACCENT+(255,))
    return img

def _tray_worker(app):
    def on_show(icon, item):
        try:
            app.deiconify()
            app.lift()
            logger.info("Application restored from System Tray.")
        except Exception:
            pass

    def on_hide(icon, item):
        try:
            app.withdraw()
            logger.info("Application hidden to System Tray.")
        except Exception:
            pass

    def on_toggle_autostart(icon, item):
        current = is_startup_enabled()
        enable_startup(not current)
        logger.info(f"Tray toggled Auto-Start to: {not current}")

    def on_quit(icon, item):
        logger.info("Application closed via System Tray.")
        try:
            icon.stop()
        finally:
            try:
                app.quit()
            except Exception:
                pass
            sys.exit(0)

    menu = pystray.Menu(
        pystray.MenuItem("Show Dashboard", on_show, default=True),
        pystray.MenuItem("Hide Dashboard", on_hide),
        pystray.MenuItem("Toggle Auto-Start", on_toggle_autostart),
        pystray.MenuItem("Quit", on_quit)
    )

    # Essential Tracker: Load logo2.ico if available, otherwise use your custom cyan circle
    if os.path.exists(LOGO_TRAY):
        image = Image.open(LOGO_TRAY)
    else:
        logger.warning(f"Tray logo ({LOGO_TRAY}) missing. Using fallback cyan circle.")
        image = _make_icon()

    icon = pystray.Icon("pebx", image, APP_NAME, menu)
    icon.run()

def start_tray(app):
    t = threading.Thread(target=_tray_worker, args=(app,), daemon=True)
    t.start()
    return t