# Hunt settings: We need to use Borderless for screenshots, but Fullscreen for
#   the keyboard input to work!

import json
import os
import platform
import sys

import click
import eel

from hunt_showdown_outfitter import api  # This exposes the eel functions.
from hunt_showdown_outfitter import ui_automation


def open_electron_gui():
    def resource_path(rel_path):
        """ Get absolute path to resource, works for dev and for PyInstaller."""
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, rel_path)

    eel.init("frontend")
    eel.browsers.set_path(
        "electron", resource_path("node_modules/electron/dist/electron.exe")
    )
    eel.start("index.html", mode="electron", port=8066)


def equip_loadout_from_cli_args(input_file, loadout):
    with open(input_file) as f:
        file_data = json.loads(f.read())

    loadout_ident = loadout
    matching_loadout = None
    for loadout in file_data["loadouts"]:
        try:
            loadout_id = int(loadout_ident)
            if loadout["id"] == loadout_id:
                matching_loadout = loadout
                break
        except ValueError:
            if loadout["label"] == loadout_ident:
                matching_loadout = loadout
                break

    if not matching_loadout:
        print("No matching loadout found")
        return

    if not ui_automation.set_hunt_showdown_as_foreground_window():
        print("Hunt is not running")
        return

    ui_coordinates = file_data["settings"]["uiCoordinates"]
    print(f"Equipping: {loadout['label']}")
    ui_automation.equip_loadout(loadout, ui_coordinates)


@click.command()
@click.option(
    "-f",
    "--input-file",
    default=None,
    help="File containing loadouts and settings (.json)",
)
@click.option(
    "-l",
    "--loadout",
    default=None,
    help="Loadout to equip (matched by ID or name)",
)
def cli(input_file, loadout):
    if input_file and loadout:
        equip_loadout_from_cli_args(input_file, loadout)
        return

    open_electron_gui()


if __name__ == "__main__":
    cli()
