# pip install pillow
# pip install pyautogui
# pip install pygetwindow

# Hunt settings: We need to use Borderless for screenshots, but Fullscreen for
#   the keyboard input to work!

import random
import sys
from collections import namedtuple

import eel
import pyautogui
import pygetwindow
from PIL import ImageDraw, ImageFont

GAME_WINDOW_TITLE = "Hunt: Showdown"

COLOR_RED = (255, 0, 0)
COLOR_YELLOW = (255, 255, 0)

Point = namedtuple("Point", ["x", "y"])

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

LOADOUTS = [
    None,  # Placeholder so we start at 1
    {
        1: "Vetterli 71 Karabiner",
        2: "Nagant M1895 Officer",
        3: "Knuckle Knife",
        4: "First Aid Kit",
        5: "Fusees",
        6: "Choke Bombs",
        7: "Vitality Shot",
        8: "Fire Bomb",
        9: "Weak Antidote Shot",
        10: "Dynamite Stick",
    },
    {
        1: "The Reckoning",
        2: "Copperhead",
        3: "The Tanto",
        4: "The Marrow",
        5: "Dusters",
        6: "Choke Bombs",
        7: "Vitality Shot",
        8: "Fire Bomb",
        9: "Weak Antidote Shot",
        10: "Frag Bomb",
    },
    {
        1: None,
        2: None,
        3: "Knuckle Knife",
        4: "First Aid Kit",
        5: "Fusees",
        6: "Choke Bombs",
        7: "Vitality Shot",
        8: "Fire Bomb",
        9: "Weak Antidote Shot",
        10: "Dynamite Stick",
    },
]


# [primary_weapon]
# x = 100
# y = 100

# [secondary_weapon]
# x = 100
# y = 100

# [tools_1]
# x = 100
# y = 100

# [tools_2]
# x = 100
# y = 100

# [tools_3]
# x = 100
# y = 100

# [tools_4]
# x = 100
# y = 100

# [consumables_1]
# x = 100
# y = 100

# [consumables_2]
# x = 100
# y = 100

# [consumables_3]
# x = 100
# y = 100

# [consumables_4]
# x = 100
# y = 100


# primary_weapon   = Vetterli 71 Karabiner
# secondary_weapon = Nagant M1895 Officer
# tools_1          = Knuckle Knife
# tools_2          = First Aid Kit
# tools_3          = Fusees
# tools_4          = Choke Bombs
# consumables_1    = Vitality Shot
# consumables_2    = Fire Bomb
# consumables_3    = Weak Antidote Shot
# consumables_4    = Dynamite Stick


def set_hunt_showdown_as_foreground_window() -> bool:
    windows = pygetwindow.getWindowsWithTitle(GAME_WINDOW_TITLE)
    try:
        game_window = windows[0]
    except IndexError:
        print(f"Window titled '{GAME_WINDOW_TITLE}' could not be found")
        return False

    game_window.activate()
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
    for slot_index in sorted(loadout.keys()):
        item_slot = ITEM_SLOTS[slot_index - 1]

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


def main(loadout_index):
    if not set_hunt_showdown_as_foreground_window():
        return

    if not loadout_index:
        unequip_all()
    else:
        equip_loadout(LOADOUTS[loadout_index])

    # _debug_item_slots_in_screenshot()


def open_gui():
    eel.init("frontend")
    eel.start("index.html", size=(520, 560), port=8066)


if __name__ == "__main__":
    open_gui()
    # args = sys.argv[1:]
    # try:
    #     loadout_index = int(args[0])
    # except (IndexError, TypeError):
    #     print("Usage: python main.py <loadout-index>")
    #     sys.exit(1)

    # main(loadout_index)
