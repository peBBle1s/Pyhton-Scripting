import pystray
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
