# Hunt settings: We need to use Borderless for screenshots, but Fullscreen for
#   the keyboard input to work!

import random
from collections import namedtuple

import json
import sys
import eel
import pyautogui
import pygetwindow
import tkinter as tk
from tkinter import filedialog
from PIL import ImageDraw, ImageFont

import os

# We'll use module level state to avoid running more than one Hunt
# automation command at a time.
this = sys.modules[__name__]
this.busy = False

GAME_WINDOW_TITLE = "Hunt: Showdown"
EXPORT_FILE_WINDOW_TITLE = "Save loadouts to file"
IMPORT_FILE_WINDOW_TITLE = "Load loadouts from file"

COLOR_RED = (255, 0, 0)
COLOR_YELLOW = (255, 255, 0)

Point = namedtuple("Point", ["x", "y"])

FRONTEND_LOADOUT_ITEM_SLOT_KEYS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]

ITEM_SLOTS = (
    # Primary and secondary Weapon
    Point(x=1810, y=305),
    Point(x=1810, y=455),
    # Tools
    Point(x=1810, y=600),
    Point(x=1900, y=600),
    Point(x=1990, y=600),
    Point(x=2085, y=600),
    # Consumables
    Point(x=1810, y=750),
    Point(x=1900, y=750),
    Point(x=1990, y=750),
    Point(x=2085, y=750),
)

# UI
SEARCH_BOX = Point(x=870, y=230)
FIRST_ITEM_IN_LIST = Point(x=950, y=310)
REMOVE_FILTERS_BUTTON = Point(x=1660, y=225)


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


def get_move_time(
    minimum: float = 0.05, maximum: float = 0.15, num_decimals: int = 2
) -> float:
    return round(random.uniform(minimum, maximum), num_decimals)


def get_type_interval(
    minimum: float = 0.005, maximum: float = 0.025, num_decimals: int = 2
) -> float:
    return round(random.uniform(minimum, maximum), num_decimals)


def smooth_move(x, y, random_offset_up_to=10):
    offset_x, offset_y = 0, 0
    if random_offset_up_to:
        offset_x = random.randint(-random_offset_up_to, random_offset_up_to)
        offset_y = random.randint(-random_offset_up_to, random_offset_up_to)
    pyautogui.moveTo(x + offset_x, y + offset_y, get_move_time(), pyautogui.easeOutQuad)


def reset_filters():
    smooth_move(REMOVE_FILTERS_BUTTON.x, REMOVE_FILTERS_BUTTON.y)
    pyautogui.click()


def focus_search_box():
    smooth_move(SEARCH_BOX.x, SEARCH_BOX.y)
    pyautogui.click()


def select_item_slot(item_slot):
    smooth_move(item_slot.x, item_slot.y)
    pyautogui.click()


def unequip_item_slot(item_slot):
    smooth_move(item_slot.x, item_slot.y)
    pyautogui.doubleClick()


def search_for(text):
    pyautogui.write(text, interval=get_type_interval())
    pyautogui.press("enter")


def buy_and_assign_first_item_to_selected_slot():
    smooth_move(FIRST_ITEM_IN_LIST.x, FIRST_ITEM_IN_LIST.y)
    pyautogui.doubleClick()


def equip_loadout(loadout: dict) -> None:
    for slot_index in FRONTEND_LOADOUT_ITEM_SLOT_KEYS:
        item_slot = ITEM_SLOTS[int(slot_index) - 1]

        item_name = loadout[slot_index]
        if not item_name:
            unequip_item_slot(item_slot)
            continue

        select_item_slot(item_slot)

        reset_filters()
        focus_search_box()
        search_for(item_name)

        buy_and_assign_first_item_to_selected_slot()


def unequip_all():
    for item_slot in ITEM_SLOTS:
        unequip_item_slot(item_slot)


def _debug_item_slots_in_screenshot():
    image = pyautogui.screenshot("screenshot.png")
    font = ImageFont.truetype("arial.ttf", 24)
    drawing = ImageDraw.Draw(image)

    for i, slot in enumerate(ITEM_SLOTS):
        drawing.ellipse(
            (
                (slot.x - 3, slot.y - 3),
                (slot.x + 3, slot.y + 3),
            ),
            fill=COLOR_RED,
        )
        slot_index = i + 1
        drawing.text(
            (slot.x + 10, slot.y),
            text=str(slot_index),
            fill=COLOR_YELLOW,
            font=font,
            stroke_width=1,
        )

    image.save()


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
                f"Loadouts imported from: {last_filepath}",
                6000,
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
        f"Loadouts imported from: {filepath}", 3000, "info", "mdi-information-outline"
    )

    save_last_filepath_to_userdir(filepath)


@busy_locked
@eel.expose()
def put_hunt_in_foreground_and_equip_loadout(loadout: dict):
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

    Please note all incoming keys are strings, not numbers.

    """
    if not set_hunt_showdown_as_foreground_window():
        return

    equip_loadout(loadout)


def open_gui():
    eel.init("frontend")
    eel.start("index.html", size=(1280, 800), port=8066)


if __name__ == "__main__":
    open_gui()
