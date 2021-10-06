GAME_WINDOW_TITLE = "Hunt: Showdown"
EXPORT_FILE_WINDOW_TITLE = "Save loadouts to file"
IMPORT_FILE_WINDOW_TITLE = "Load loadouts from file"

MEMORY_FILENAME = "hunt_showdown_outfitter.json"

COLOR_RED = (255, 0, 0)
COLOR_YELLOW = (255, 255, 0)
COLOR_GREEN = (0, 255, 0)

FRONTEND_LOADOUT_ITEM_SLOT_KEYS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
FRONTEND_LOADOUT_SPECIAL_AMMO_KEYS = [
    "1_special_large_1",
    "1_special_large_2",
    "1_special_medium_1",
    "1_special_medium_2",
    "1_special_small",
    "2_special_large_1",
    "2_special_large_2",
    "2_special_medium_1",
    "2_special_medium_2",
    "2_special_small",
]
FRONTEND_EXTRA_UI_ELEMENTS_KEYS = [
    "search_box",
    "first_item_in_list",
    "remove_filters_button",
    "discard_item_dialog_yes_button",
    "transaction_not_possible_dialog_ok_button",
]
ALL_UI_COORDINATE_KEYS = [
    *FRONTEND_LOADOUT_ITEM_SLOT_KEYS,
    *FRONTEND_LOADOUT_SPECIAL_AMMO_KEYS,
    *FRONTEND_EXTRA_UI_ELEMENTS_KEYS,
]

GITHUB_RELEASES_PAGE = "https://github.com/cb109/hunt_showdown_outfitter/releases"
