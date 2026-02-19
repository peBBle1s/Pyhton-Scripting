# tray.py
import threading
import sys
from PIL import Image, ImageDraw
import pystray
from router import is_startup_enabled, enable_startup

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
    icon = None

    def on_show(icon, item):
        try:
            app.deiconify()
            app.lift()
        except Exception:
            pass

    def on_hide(icon, item):
        try:
            app.withdraw()
        except Exception:
            pass

    def on_toggle_autostart(icon, item):
        current = is_startup_enabled()
        enable_startup(not current)

    def on_quit(icon, item):
        try:
            icon.stop()
        finally:
            try:
                app.quit()
            except Exception:
                pass
            sys.exit(0)

    menu = pystray.Menu(
        pystray.MenuItem("Show", on_show),
        pystray.MenuItem("Hide", on_hide),
        pystray.MenuItem("Toggle Auto-Start", on_toggle_autostart),
        pystray.MenuItem("Quit", on_quit)
    )

    icon = pystray.Icon("pebx", _make_icon(), "PebX", menu)
    icon.run()

def start_tray(app):
    t = threading.Thread(target=_tray_worker, args=(app,), daemon=True)
    t.start()
    return t
