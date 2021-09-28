# Hunt settings: We need to use Borderless for screenshots, but Fullscreen for
#   the keyboard input to work!

import json
import platform
import sys

import click
import eel

from hunt_showdown_outfitter import api  # This exposes the eel functions.
from hunt_showdown_outfitter import ui_automation


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

    ui_coordinates = file_data["settings"]["uiCoordinates"]
    ui_automation.equip_loadout(loadout, ui_coordinates)


@click.command()
@click.option(
    "--no-gui",
    is_flag=True,
    help="Enables the commandline interface instead of opening the GUI",
)
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
def cli(no_gui, input_file, loadout):
    if not no_gui:
        return open_gui()

    if not (input_file and loadout):
        print("You must pass both --input-file and --loadout arguments, see --help")
        return
    equip_loadout_from_cli_args(input_file, loadout)


if __name__ == "__main__":
    cli()
