# Hunt settings: We need to use Borderless for screenshots, but Fullscreen for
#   the keyboard input to work!

import sys
import eel
import platform

from hunt_showdown_outfitter import api  # This exposes the eel functions.


def open_gui():
    page = "index.html"
    eel_kwargs = {
        "size": (1280, 800),
        "port": 8066,
    }

    eel.init("frontend")
    try:
        eel.start(page, **eel_kwargs)
    except EnvironmentError:
        # If default browser (Chrome) isn't found, fallback to Microsoft Edge on Win10 or greater
        # https://github.com/ChrisKnott/Eel/blob/master/examples/07%20-%20CreateReactApp/eel_CRA.py#L68-L70
        if sys.platform in ["win32", "win64"] and int(platform.release()) >= 10:
            eel.start(page, mode="edge", **eel_kwargs)
        else:
            raise


if __name__ == "__main__":
    open_gui()
