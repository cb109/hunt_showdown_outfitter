import json
import os
import subprocess
import sys
import tempfile
import tkinter as tk
import uuid
import webbrowser
from tkinter import filedialog
from typing import Optional
from typing import Tuple

import eel
import pyautogui
from PIL import ImageDraw, ImageFont

from hunt_showdown_outfitter import __version__
from hunt_showdown_outfitter import ui_automation
from hunt_showdown_outfitter.constants import ALL_UI_COORDINATE_KEYS
from hunt_showdown_outfitter.constants import COLOR_GREEN
from hunt_showdown_outfitter.constants import EXPORT_FILE_WINDOW_TITLE
from hunt_showdown_outfitter.constants import GITHUB_PAGE
from hunt_showdown_outfitter.constants import IMPORT_FILE_WINDOW_TITLE

# We'll use module level state to avoid running more than one Hunt
# automation command at a time.
this = sys.modules[__name__]
this.busy = False


def busy_locked(func):
    """Skip function call when module state indicates 'already busy'.

    Also toggles the state during function call. Use as a function
    decorator.

    """

    def inner(*args, **kwargs):
        if this.busy:
            return
        this.busy = True
        try:
            return func(*args, **kwargs)
        finally:
            this.busy = False

    return inner


@busy_locked
@eel.expose()
def put_hunt_in_foreground_and_debug_ui_coordinates_in_screenshot(ui_coordinates: dict):
    """Create screenshot with coordinates overlayed and display it."""

    # Allow screenshot even if Hunt is not running.
    ui_automation.set_hunt_showdown_as_foreground_window()

    tempdir = tempfile.gettempdir()
    screenshot_filepath = os.path.join(
        tempdir, f"hunt_showdown_outfitter_screenshot_{uuid.uuid4()}.png"
    )
    with open(screenshot_filepath, "w") as f:
        f.write("")
    screenshot_filepath = os.path.abspath(screenshot_filepath)

    image = pyautogui.screenshot()
    font = ImageFont.truetype("arial.ttf", 24)
    drawing = ImageDraw.Draw(image)

    for key in ALL_UI_COORDINATE_KEYS:
        coords = ui_coordinates[key]
        x = int(coords["x"])
        y = int(coords["y"])

        drawing.ellipse(
            (
                (x - 3, y - 3),
                (x + 3, y + 3),
            ),
            fill=COLOR_GREEN,
        )
        drawing.text(
            (x + 10, y),
            text=str(key),
            fill=COLOR_GREEN,
            font=font,
        )

    image.save(screenshot_filepath)

    subprocess.run(["explorer", screenshot_filepath], shell=True)
    ui_automation.put_hunt_showdown_window_to_background()


@busy_locked
@eel.expose()
def get_primary_screen_size() -> Tuple[int, int]:
    return ui_automation.get_screen_size()


@busy_locked
@eel.expose()
def load_data_from_last_filepath_in_userdir() -> Optional[str]:
    memory_filepath = ui_automation.get_userdir_memory_filepath()
    if not os.path.isfile(memory_filepath):
        return
    try:
        with open(memory_filepath) as f:
            data = json.loads(f.read())
            last_filepath = data["last_filepath"]
            if not last_filepath:
                return

        with open(last_filepath) as f:
            data = json.loads(f.read())
            eel.loadFileData(data)

            eel.feedback(
                f"Opened most recent file: {last_filepath}",
                2000,
                "info",
                "mdi-information-outline",
            )
            return last_filepath

    except Exception as err:
        print(err)


@busy_locked
@eel.expose()
def save_to_file(data: dict, filepath: str):
    with open(filepath, "w") as file_handle:
        file_handle.write(json.dumps(data, indent=2, sort_keys=True))
        file_handle.close()

        ui_automation.save_last_filepath_to_userdir(filepath)

        eel.feedback(f"Saved to: {filepath}", 2000)


@busy_locked
@eel.expose()
def choose_file_and_export_to(data) -> Optional[str]:
    root = tk.Tk()
    root.withdraw()

    file_handle = filedialog.asksaveasfile(
        parent=root,
        title=EXPORT_FILE_WINDOW_TITLE,
        defaultextension=".json",
        filetypes=(("JSON", "*.json"),),
    )
    if not file_handle:
        return
    file_handle.write(json.dumps(data, indent=2, sort_keys=True))
    file_handle.close()

    filepath = file_handle.name
    ui_automation.save_last_filepath_to_userdir(filepath)

    eel.feedback(f"File saved as: {filepath}", 3000, "info", "mdi-information-outline")
    return filepath


@busy_locked
@eel.expose()
def choose_file_and_import_from() -> Optional[str]:
    root = tk.Tk()
    root.withdraw()

    file_handle = filedialog.askopenfile(
        parent=root,
        title=IMPORT_FILE_WINDOW_TITLE,
        defaultextension=".json",
        filetypes=(("JSON", "*.json"),),
    )
    if not file_handle:
        return
    try:
        data = json.loads(file_handle.read())
    except Exception as err:
        print(err)
        return
    finally:
        file_handle.close()

    filepath = file_handle.name

    eel.loadFileData(data)
    eel.feedback(f"Opened file: {filepath}", 2000, "info", "mdi-information-outline")

    ui_automation.save_last_filepath_to_userdir(filepath)
    return filepath


@busy_locked
@eel.expose()
def put_hunt_in_foreground_and_equip_loadout(loadout: dict, ui_coordinates: dict):
    """Equip given loadout in the running Hunt instance.

    Example for the shape of a loadout:

        {
            "id": 2,
            "label": 'Sparks / Frag',
            "1": "The Reckoning",
            "2": "Copperhead",
            "3": "The Tanto",
            "4": "The Marrow",
            "5": "Dusters",
            "6": "Choke Bombs",
            "7": "Vitality Shot",
            "8": "Fire Bomb",
            "9": "Weak Antidote Shot",
            "10": "Frag Bomb",
        }

    Example for the shape of ui_coordinates:

        {
            "1": {"x": 1810, "y": 305},
            "2": {"x": 1810, "y": 455},
            "3": {"x": 1810, "y": 600},
            "4": {"x": 1900, "y": 600},
            "5": {"x": 1990, "y": 600},
            "6": {"x": 2085, "y": 600},
            "7": {"x": 1810, "y": 750},
            "8": {"x": 1900, "y": 750},
            "9": {"x": 1990, "y": 750},
            "10": {"x": 2085, "y": 750},
            "search_box": {"x": 870, "y": 230},
            "first_item_in_list": {"x": 950, "y": 310},
            "remove_filters_button": {"x": 1660, "y": 225},
        }

    Please note all incoming keys are strings, not numbers.

    """
    if not ui_automation.set_hunt_showdown_as_foreground_window():
        return

    ui_automation.equip_loadout(loadout, ui_coordinates)


@busy_locked
@eel.expose()
def put_hunt_in_foreground_and_equip_loadout_item_slot(
    loadout: dict, item_slot_index: int, ui_coordinates: dict
):
    if not ui_automation.set_hunt_showdown_as_foreground_window():
        return

    ui_automation.equip_loadout_item_slot(loadout, str(item_slot_index), ui_coordinates)


@busy_locked
@eel.expose()
def open_git_hub_page_in_default_browser():
    webbrowser.open_new(GITHUB_PAGE)


@busy_locked
@eel.expose()
def forget_last_filepath():
    ui_automation.save_last_filepath_to_userdir("")


@busy_locked
@eel.expose()
def get_version():
    return __version__
