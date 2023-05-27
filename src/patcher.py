"""
Part of RaceMenu Interface Patcher (RIP).
Contains Patcher class.

Licensed under Attribution-NonCommercial-NoDerivatives 4.0 International
"""


import jstyleson as json
import logging
from pathlib import Path

from main import MainApp
import ffdec
import errors


class Patcher:
    """
    Class for Patcher.
    """

    patch_data: dict = None
    patch_path: Path = None
    racemenu_path: Path = None

    def __init__(self, app: MainApp, patch_path: Path, racemenu_path: Path):
        self.app = app
        self.patch_path = patch_path
        self.racemenu_path = racemenu_path

        self.log = logging.getLogger(self.__repr__())
        self.log.addHandler(self.app.log_str)
        self.log.setLevel(self.app.log.level)

        self.load_patch_data()

    def __repr__(self):
        return "Patcher"

    def load_patch_data(self):
        self.log.info(f"Loading patch '{self.patch_path.name}'...")
        patch_data_file = self.patch_path / "patch.json"

        if not patch_data_file.is_file():
            raise errors.InvalidPatchError
        
        with open(patch_data_file, "r", encoding="utf8") as file:
            self.patch_data: dict = json.load(file)
        
        self.log.info("Loaded patch!")

    def patch(self):
        self.log.info("Patching RaceMenu...")

        # 1) Extract racesex_menu.swf from RaceMenu BSA to Temp folder

        # 2) Create FFDec jobs from patch data

        # 3) Run FFDec jobs

        # 4) Copy patched SWF to current directory

        # 5) Delete Temp folder

        self.log.info("Patch complete!")

