# Hunt settings: We need to use Borderless for screenshots, but Fullscreen for
#   the keyboard input to work!

import random

import json
import sys
import eel
import pyautogui
import pygetwindow
import tempfile
import tkinter as tk
from tkinter import filedialog
from PIL import ImageDraw, ImageFont
import uuid
import os
import subprocess
import platform

# We'll use module level state to avoid running more than one Hunt
# automation command at a time.
this = sys.modules[__name__]
this.busy = False

GAME_WINDOW_TITLE = "Hunt: Showdown"
EXPORT_FILE_WINDOW_TITLE = "Save loadouts to file"
IMPORT_FILE_WINDOW_TITLE = "Load loadouts from file"

COLOR_RED = (255, 0, 0)
COLOR_YELLOW = (255, 255, 0)
COLOR_GREEN = (0, 255, 0)

FRONTEND_LOADOUT_ITEM_SLOT_KEYS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
ALL_UI_COORDINATE_KEYS = [
    *FRONTEND_LOADOUT_ITEM_SLOT_KEYS,
    "search_box",
    "remove_filters_button",
    "first_item_in_list",
]


def busy_locked(func):
    def inner(*args, **kwargs):
        if this.busy:
            return
        this.busy = True
        try:
            return func(*args, **kwargs)
        finally:
            this.busy = False

    return inner


def set_hunt_showdown_as_foreground_window() -> bool:
    game_window = None
    for window in pygetwindow.getWindowsWithTitle(GAME_WINDOW_TITLE):
        if window.title == GAME_WINDOW_TITLE:
            game_window = window
            break
    if not game_window:
        message = f"Window titled '{GAME_WINDOW_TITLE}' could not be found"
        print(message)
        eel.feedback(message, 3000, "error", "mdi-alert-outline")
        return False

    game_window.minimize()
    game_window.restore()

    return True


def put_hunt_showdown_window_to_background() -> bool:
    game_window = None
    for window in pygetwindow.getWindowsWithTitle(GAME_WINDOW_TITLE):
        if window.title == GAME_WINDOW_TITLE:
            game_window = window
            break
    if not game_window:
        message = f"Window titled '{GAME_WINDOW_TITLE}' could not be found"
        print(message)
        eel.feedback(message, 3000, "error", "mdi-alert-outline")
        return False

    game_window.minimize()

    return True


def get_move_time(
    minimum: float = 0.05, maximum: float = 0.15, num_decimals: int = 2
) -> float:
    return round(random.uniform(minimum, maximum), num_decimals)


def get_type_interval(
    minimum: float = 0.005, maximum: float = 0.025, num_decimals: int = 2
) -> float:
    return round(random.uniform(minimum, maximum), num_decimals)


def smooth_move(x, y, random_offset_up_to=10):
    x = int(x)
    y = int(y)

    offset_x, offset_y = 0, 0
    if random_offset_up_to:
        offset_x = random.randint(-random_offset_up_to, random_offset_up_to)
        offset_y = random.randint(-random_offset_up_to, random_offset_up_to)

    pyautogui.moveTo(
        x + offset_x,
        y + offset_y,
        get_move_time(),
        pyautogui.easeOutQuad,
    )


def reset_filters(x, y):
    smooth_move(x, y)
    pyautogui.click()


def focus_search_box(x, y):
    smooth_move(x, y)
    pyautogui.click()


def select_item_slot(x, y):
    smooth_move(x, y)
    pyautogui.click()


def unequip_item_slot(x, y):
    smooth_move(x, y)
    pyautogui.doubleClick()


def search_for(text):
    pyautogui.write(text, interval=get_type_interval())
    pyautogui.press("enter")


def buy_and_assign_first_item_to_selected_slot(x, y):
    smooth_move(x, y)
    pyautogui.doubleClick()


def equip_loadout(loadout: dict, ui_coordinates: dict) -> None:
    ui_first_item_in_list = ui_coordinates["first_item_in_list"]
    ui_remove_filters_button = ui_coordinates["remove_filters_button"]
    ui_search_box = ui_coordinates["search_box"]

    for slot_index in FRONTEND_LOADOUT_ITEM_SLOT_KEYS:
        ui_item = ui_coordinates[int(slot_index) - 1]

        exclude_item_slot = loadout.get("excludes", {}).get(slot_index, False)
        if exclude_item_slot:
            continue

        item_name = loadout[slot_index]
        if not item_name:
            unequip_item_slot(ui_item["x"], ui_item["y"])
            continue

        select_item_slot(ui_item["x"], ui_item["y"])

        reset_filters(ui_remove_filters_button["x"], ui_remove_filters_button["y"])
        focus_search_box(ui_search_box["x"], ui_search_box["y"])
        search_for(item_name)

        buy_and_assign_first_item_to_selected_slot(
            ui_first_item_in_list["x"], ui_first_item_in_list["y"]
        )


@busy_locked
@eel.expose()
def put_hunt_in_foreground_and_debug_ui_coordinates_in_screenshot(ui_coordinates: dict):
    """Create screenshot with coordinates overlayed and display it."""

    if not set_hunt_showdown_as_foreground_window():
        return

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
    put_hunt_showdown_window_to_background()


def get_userdir_memory_filepath():
    home = os.path.expanduser("~")
    return os.path.join(home, "hunt_showdown_outfitter.json")


def save_last_filepath_to_userdir(filepath):
    memory_filepath = get_userdir_memory_filepath()
    data = {"last_filepath": filepath}
    with open(memory_filepath, "w") as f:
        f.write(json.dumps(data, indent=2, sort_keys=True))


@busy_locked
@eel.expose()
def load_data_from_last_filepath_in_userdir():
    memory_filepath = get_userdir_memory_filepath()
    if not os.path.isfile(memory_filepath):
        return
    try:
        with open(memory_filepath) as f:
            data = json.loads(f.read())
            last_filepath = data["last_filepath"]

        with open(last_filepath) as f:
            data = json.loads(f.read())
            eel.loadFileData(data)
            eel.feedback(
                f"Loadouts imported from last file: {last_filepath}",
                2000,
                "info",
                "mdi-information-outline",
            )

    except Exception as err:
        print(err)


@busy_locked
@eel.expose()
def choose_file_and_export_to(data):
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
    save_last_filepath_to_userdir(filepath)

    eel.feedback(
        f"File written to: {filepath}", 3000, "info", "mdi-information-outline"
    )


@busy_locked
@eel.expose()
def choose_file_and_import_from():
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
    eel.feedback(
        f"Loadouts imported from: {filepath}", 2000, "info", "mdi-information-outline"
    )

    save_last_filepath_to_userdir(filepath)


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
    if not set_hunt_showdown_as_foreground_window():
        return

    equip_loadout(loadout, ui_coordinates)


def open_gui():
    page = "index.html"
    size = (1280, 900)
    port = 8066

    eel.init("frontend")
    try:
        eel.start(page, size=size, port=port)
    except EnvironmentError:
        # If default browser (Chrome) isn't found, fallback to Microsoft Edge on Win10 or greater
        # https://github.com/ChrisKnott/Eel/blob/master/examples/07%20-%20CreateReactApp/eel_CRA.py#L68-L70
        if sys.platform in ["win32", "win64"] and int(platform.release()) >= 10:
            eel.start(page, size=size, port=port)
        else:
            raise


if __name__ == "__main__":
    open_gui()
