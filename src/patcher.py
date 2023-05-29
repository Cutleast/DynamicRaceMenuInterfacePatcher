"""
Part of RaceMenu Interface Patcher (RIP).
Contains Patcher class.

Licensed under Attribution-NonCommercial-NoDerivatives 4.0 International
"""


import logging
import os
import shutil
import tempfile as tmp
import xmltodict as xml2d
import dicttoxml2 as d2xml
from pathlib import Path
from typing import Dict, List

import jstyleson as json
from bethesda_structs.archive.bsa import BSAArchive

import errors
import ffdec
from main import MainApp


class Patcher:
    """
    Class for Patcher.
    """

    patch_data: dict = None
    patch_path: Path = None
    racemenu_path: Path = None
    ffdec_interface: ffdec.FFDec = None

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

    def _extract_bsa(self, tmpdir: Path):
        bsa_path = self.racemenu_path / "RaceMenu.bsa"
        if not bsa_path.is_file():
            self.log.error("RaceMenu.bsa could not be found!")
            raise errors.BSANotFoundError

        self.log.debug("Extracting RaceMenu.bsa...")
        
        os.mkdir(tmpdir / bsa_path.stem)
        archive = BSAArchive.parse_file(str(bsa_path))
        archive.extract(tmpdir / bsa_path.stem)

        self.log.debug("Extracted BSA.")
        return tmpdir / bsa_path.stem

    def _patch_xml(self, xml_file: Path):
        self.log.info("Reading XML file...")

        xml_data = xml2d.parse(xml_file.read_text())

        # WIP: No patching takes place, yet
        self.log.info("Patching XML file...")

        self.log.info("Writing XML file...")
        xml_file.write_bytes(d2xml.dicttoxml(xml_data))

        self.log.info("Patched XML file.")

    def _patch_shapes(self):
        shapes: Dict[Path, List[int]] = {}
        for shape in self.patch_data.get("shapes", []):
            shape = self.patch_path / shape
            if shape in shapes:
                shapes[shape] += shape["index"]
            else:
                shapes[shape] = shape["index"]
        
        self.ffdec_interface.replace_shapes(shapes)

    def patch(self):
        self.log.info("Patching RaceMenu...")
        
        # 0) Create Temp folder
        with tmp.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # 1) Extract RaceMenu BSA to Temp folder
            bsa_path = self._extract_bsa(tmpdir)

            # 2) Initialize FFDec interface
            swf_path = bsa_path / "interface" / "racesex_menu.swf"
            self.ffdec_interface = ffdec.FFDec(swf_path, self.app)

            # 3) Patch shapes into SWF
            self._patch_shapes(tmpdir)

            # 4) Convert SWF to XML
            xml_file = self.ffdec_interface.swf2xml()

            # 5) Patch XML
            self._patch_xml(xml_file)

            # 6) Convert XML back to SWF
            patched_swf = self.ffdec_interface.xml2swf(xml_file)

            # 7) Copy patched SWF to current directory
            os.mkdir(Path(".") / "interface")
            shutil.copyfile(
                patched_swf,
                Path(".") / "interface" / "racesex_menu.swf"
            )

        self.log.info("Patch complete!")
        self.app.done_signal.emit()

