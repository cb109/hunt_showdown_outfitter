import ctypes
import json
import os
import random
from typing import Tuple

import eel
import keyboard
import pyautogui
import pygetwindow

from hunt_showdown_outfitter.constants import FRONTEND_LOADOUT_ITEM_SLOT_KEYS
from hunt_showdown_outfitter.constants import GAME_WINDOW_TITLE
from hunt_showdown_outfitter.constants import MEMORY_FILENAME


def get_userdir_memory_filepath():
    home = os.path.expanduser("~")
    return os.path.join(home, MEMORY_FILENAME)


def save_last_filepath_to_userdir(filepath):
    memory_filepath = get_userdir_memory_filepath()
    data = {"last_filepath": filepath}
    with open(memory_filepath, "w") as f:
        f.write(json.dumps(data, indent=2, sort_keys=True))


def get_screen_size() -> Tuple[int, int]:
    user32 = ctypes.windll.user32
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)


def get_move_time(
    minimum: float = 0.05, maximum: float = 0.15, num_decimals: int = 2
) -> float:
    return round(random.uniform(minimum, maximum), num_decimals)


def get_type_interval(
    minimum: float = 0.005, maximum: float = 0.015, num_decimals: int = 2
) -> float:
    return round(random.uniform(minimum, maximum), num_decimals)


def skipped_by_escape_key(func):
    """Skip function call when escape key is being pressed.

    Use as a function decorator.

    """

    def inner(*args, **kwargs):
        if keyboard.is_pressed("esc"):
            return
        return func(*args, **kwargs)

    return inner


@skipped_by_escape_key
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


@skipped_by_escape_key
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


@skipped_by_escape_key
def smooth_move(x, y, random_offset_up_to=5):
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


@skipped_by_escape_key
def reset_filters(x, y):
    smooth_move(x, y)
    pyautogui.click()


@skipped_by_escape_key
def focus_search_box(x, y):
    smooth_move(x, y)
    pyautogui.click()


@skipped_by_escape_key
def select_item_slot(x, y):
    smooth_move(x, y)
    pyautogui.click()


@skipped_by_escape_key
def unequip_item_slot(x, y):
    smooth_move(x, y)
    pyautogui.doubleClick()


@skipped_by_escape_key
def maybe_get_rid_of_dialog(x, y):
    smooth_move(x, y)
    pyautogui.click()


@skipped_by_escape_key
def search_for(text):
    pyautogui.write(text, interval=get_type_interval())
    pyautogui.press("enter")


@skipped_by_escape_key
def buy_and_assign_first_item_to_selected_slot(x, y):
    smooth_move(x, y)
    pyautogui.doubleClick()


@skipped_by_escape_key
def equip_loadout(loadout: dict, ui_coordinates: dict) -> None:
    for item_slot_index in FRONTEND_LOADOUT_ITEM_SLOT_KEYS:
        equip_loadout_item_slot(loadout, item_slot_index, ui_coordinates)


@skipped_by_escape_key
def equip_loadout_item_slot(
    loadout: dict, item_slot_index: str, ui_coordinates: dict
) -> None:
    ui_discard_item_dialog_yes_button = ui_coordinates["discard_item_dialog_yes_button"]
    ui_first_item_in_list = ui_coordinates["first_item_in_list"]
    ui_item = ui_coordinates[item_slot_index]
    ui_remove_filters_button = ui_coordinates["remove_filters_button"]
    ui_search_box = ui_coordinates["search_box"]
    ui_transaction_not_possible_dialog_ok_button = ui_coordinates[
        "transaction_not_possible_dialog_ok_button"
    ]

    exclude_item_slot = loadout.get("excludes", {}).get(item_slot_index, False)
    if exclude_item_slot:
        return

    select_item_slot(ui_item["x"], ui_item["y"])
    unequip_item_slot(ui_item["x"], ui_item["y"])
    maybe_get_rid_of_dialog(
        ui_discard_item_dialog_yes_button["x"], ui_discard_item_dialog_yes_button["y"]
    )

    item_name = loadout[item_slot_index]
    if not item_name:
        return

    reset_filters(ui_remove_filters_button["x"], ui_remove_filters_button["y"])
    focus_search_box(ui_search_box["x"], ui_search_box["y"])
    search_for(item_name)

    buy_and_assign_first_item_to_selected_slot(
        ui_first_item_in_list["x"], ui_first_item_in_list["y"]
    )
    maybe_get_rid_of_dialog(
        ui_transaction_not_possible_dialog_ok_button["x"],
        ui_transaction_not_possible_dialog_ok_button["y"],
    )
