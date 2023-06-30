"""
Part of Dynamic RaceMenu Interface Patcher (DRIP).
Contains Patcher class.

Licensed under Attribution-NonCommercial-NoDerivatives 4.0 International
"""


import html
import logging
import os
import re
import shutil
import tempfile as tmp
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List

import jstyleson as json
from bethesda_structs.archive.bsa import BSAArchive

import errors
import ffdec
import utils
from main import MainApp


class Patcher:
    """
    Class for Patcher.
    """

    patch_data: dict = None
    patch_path: Path = None
    racemenu_path: Path = None
    ffdec_interface: ffdec.FFDec = None
    patch_dir: Path = None
    tmpdir: Path = None

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
        """
        Loads patch data from patch.json.
        """

        self.log.info(f"Loading patch '{self.patch_path.name}'...")
        patch_data_file = self.patch_path / "patch.json"

        if not patch_data_file.is_file():
            raise errors.InvalidPatchError("Found no 'patch.json'!")

        with open(patch_data_file, "r", encoding="utf8") as file:
            self.patch_data: dict = json.load(file)

        self.log.info("Loaded patch!")

    def _extract_bsa(self):
        bsa_path = self.racemenu_path / "RaceMenu.bsa"
        if not bsa_path.is_file():
            self.log.error("RaceMenu.bsa could not be found!")
            raise errors.BSANotFoundError

        self.log.debug("Extracting RaceMenu.bsa...")

        output_path = self.tmpdir / bsa_path.stem
        
        os.mkdir(output_path)
        archive = BSAArchive.parse_file(str(bsa_path))
        archive.extract(output_path)

        self.log.debug("Extracted BSA.")
        return output_path

    def _patch_xml(self, xml_file: Path, patch_data: dict):
        self.log.info("Reading XML file...")

        xml_data = ET.parse(str(xml_file))
        xml_root = xml_data.getroot()
        xml_tags = xml_root[1]

        self.log.info("Patching XML file...")

        # Patch header
        if header:= patch_data.get("header", {}):
            display_rect = header.get("displayRect", None)

            if display_rect is not None:
                display_rect_item = xml_root[0]

                for key, value in display_rect.items():
                    display_rect_item.attrib[key] = value

        # Patch shape bounds
        for c, shape in enumerate(patch_data.get("shapes", [])):
            if not shape.get("shapeBounds"):
                continue
            self.log.info(f"Patching shape bounds of shape {c}...")
            for index in shape["index"]:
                id = index
                shape_item = xml_tags.find(f"./item[@shapeId='{id}']")
                if shape_item is None:
                    self.log.warning(
                        f"Failed to patch shape with id '{id}': Shape not found in XML!"
                    )
                    continue
                bonds_item = shape_item.find(f"./shapeBounds")
                if bonds_item is None:
                    self.log.warning(
                        f"Failed to patch shape with id '{id}': Shape has no shape bounds!"
                    )
                    continue
                for key, value in shape["shapeBounds"].items():
                    bonds_item.attrib[key] = str(value).lower()

        # Patch sprites
        for c, sprite in enumerate(patch_data.get("sprites", [])):
            id = sprite["SpriteID"]
            char_id: List[str] = sprite["CharacterID"]
            depth: List[str] = sprite["Depth"]
            if id != "*":
                self.log.info(f"Patching sprite {c+1} of {len(patch_data['sprites'])}...")
                sprite_item = xml_tags.find(f"./item[@spriteId='{id}']")
                if sprite_item is None:
                    self.log.warning(
                        f"Failed to patch sprite with id '{id}': Sprite not found in XML!"
                    )
                    continue
                
                # Patch matrix
                if sprite.get("MATRIX", None) is not None:
                    matrix_items: List[ET.Element] = []

                    if "*" in char_id and "*" in depth:
                        matrix_items = sprite_item.findall(
                            f"./subTags/item[@characterId][@depth]/matrix"
                        )
                    elif "*" not in char_id and "*" in depth:
                        for id in char_id:
                            matrix_items += sprite_item.findall(
                                f"./subTags/item[@characterId='{id}'][@depth]/matrix"
                            )
                    elif "*" in char_id and "*" not in depth:
                        for d in depth:
                            matrix_items += sprite_item.findall(
                                f"./subTags/item[@characterId][@depth='{d}']/matrix"
                            )
                    else:
                        for id in char_id:
                            for d in depth:
                                matrix_items += sprite_item.findall(
                                    f"./subTags/item[@characterId='{id}'][@depth='{d}']/matrix"
                                )

                    if not matrix_items:
                        self.log.warning(
                            f"Failed to patch sprite with id '{id}': No matrix found for character id '{char_id}' with depth '{depth}'!"
                        )
                        continue
                    for matrix_item in matrix_items:
                        for key, value in sprite["MATRIX"].items():
                            matrix_item.attrib[key] = str(value).lower()
                # Patch color transforms
                if sprite.get("colorTransform", None) is not None:
                    transform_items: List[ET.Element] = []

                    if "*" in char_id and "*" in depth:
                        transform_items = sprite_item.findall(
                            f"./subTags/item[@characterId][@depth]/colorTransform"
                        )
                    elif "*" not in char_id and "*" in depth:
                        for id in char_id:
                            transform_items += sprite_item.findall(
                                f"./subTags/item[@characterId='{id}'][@depth]/colorTransform"
                            )
                    elif "*" in char_id and "*" not in depth:
                        for d in depth:
                            transform_items += sprite_item.findall(
                                f"./subTags/item[@characterId][@depth='{d}']/colorTransform"
                            )
                    else:
                        for id in char_id:
                            for d in depth:
                                transform_items += sprite_item.findall(
                                    f"./subTags/item[@characterId='{id}'][@depth='{d}']/colorTransform"
                                )
                    
                    if not transform_items:
                        # self.log.warning(
                        #     f"Failed to patch sprite with id '{id}': No color transform item found for character id '{char_id}' with depth '{depth}'!"
                        # )
                        # continue
                        self.log.debug(f"Creating color transform item for sprite id '{id}' and character id '{char_id}'...")
                        print("Before:", sprite_item)
                        transform_item = ET.Element(
                            "colorTransform",
                            {
                                "type": "CXFORMWITHALPHA",
                                "alphaAddTerm": "0",
                                "alphaMultTerm": "0",
                                "blueAddTerm": "0",
                                "blueMultTerm": "0",
                                "greenAddTerm": "0",
                                "greenMultTerm": "0",
                                "hasAddTerms": "false",
                                "hasMultTerms": "false",
                                "nbits": "10",
                                "redAddTerm": "0",
                                "redMultTerm": "0"
                            }
                        )
                        sprite_item.append(
                            transform_item
                        )
                        sprite_item.attrib["placeFlagHasColorTransform"] = "true"
                        transform_items.append(transform_item)
                        print("Before:", sprite_item)

                    for transform_item in transform_items:
                        for key, value in sprite["colorTransform"].items():
                            transform_item.attrib[key] = str(value).lower()
            else:
                self.log.info(f"Patching sprites...")
                sprite_items = xml_tags.findall(f"./item[@spriteId]")
                for sprite_item in sprite_items:
                    # Patch matrix
                    if sprite.get("MATRIX", None) is not None:
                        matrix_items: List[ET.Element] = []

                        if "*" in char_id and "*" in depth:
                            matrix_items = sprite_item.findall(
                                f"./subTags/item[@characterId][@depth]/matrix"
                            )
                        elif "*" not in char_id and "*" in depth:
                            for id in char_id:
                                matrix_items += sprite_item.findall(
                                    f"./subTags/item[@characterId='{id}'][@depth]/matrix"
                                )
                        elif "*" in char_id and "*" not in depth:
                            for d in depth:
                                matrix_items += sprite_item.findall(
                                    f"./subTags/item[@characterId][@depth='{d}']/matrix"
                                )
                        else:
                            for id in char_id:
                                for d in depth:
                                    matrix_items += sprite_item.findall(
                                        f"./subTags/item[@characterId='{id}'][@depth='{d}']/matrix"
                                    )

                        if not matrix_items:
                            self.log.warning(
                                f"Failed to patch sprite with id '{id}': No matrix found for character id '{char_id}' with depth '{depth}'!"
                            )
                            continue
                        for matrix_item in matrix_items:
                            for key, value in sprite["MATRIX"].items():
                                matrix_item.attrib[key] = str(value).lower()
                    # Patch color transforms
                    if sprite.get("colorTransform", None) is not None:
                        transform_items: List[ET.Element] = []

                        if "*" in char_id and "*" in depth:
                            transform_items = sprite_item.findall(
                                f"./subTags/item[@characterId][@depth]/colorTransform"
                            )
                        elif "*" not in char_id and "*" in depth:
                            for id in char_id:
                                transform_items += sprite_item.findall(
                                    f"./subTags/item[@characterId='{id}'][@depth]/colorTransform"
                                )
                        elif "*" in char_id and "*" not in depth:
                            for d in depth:
                                transform_items += sprite_item.findall(
                                    f"./subTags/item[@characterId][@depth='{d}']/colorTransform"
                                )
                        else:
                            for id in char_id:
                                for d in depth:
                                    transform_items += sprite_item.findall(
                                        f"./subTags/item[@characterId='{id}'][@depth='{d}']/colorTransform"
                                    )
                        
                        if not transform_items:
                            # self.log.warning(
                            #     f"Failed to patch sprite with id '{id}': No color transform item found for character id '{char_id}' with depth '{depth}'!"
                            # )
                            # continue
                            self.log.debug(f"Creating color transform item for sprite id '{id}' and character id '{char_id}'...")
                            transform_item = ET.Element(
                                "colorTransform",
                                {
                                    "type": "CXFORMWITHALPHA",
                                    "alphaAddTerm": "0",
                                    "alphaMultTerm": "0",
                                    "blueAddTerm": "0",
                                    "blueMultTerm": "0",
                                    "greenAddTerm": "0",
                                    "greenMultTerm": "0",
                                    "hasAddTerms": "false",
                                    "hasMultTerms": "false",
                                    "nbits": "10",
                                    "redAddTerm": "0",
                                    "redMultTerm": "0"
                                }
                            )
                            sprite_item.append(
                                transform_item
                            )
                            sprite_item.attrib["placeFlagHasColorTransform"] = "true"
                            transform_items.append(transform_item)

                        for transform_item in transform_items:
                            for key, value in sprite["colorTransform"].items():
                                transform_item.attrib[key] = str(value).lower()

        # Patch texts
        for c, text in enumerate(patch_data.get("text", [])):
            char_ids = text["index"]
            self.log.info(f"Patching text {c+1} of {len(patch_data['text'])}...")
            font_id = text.get("font", None)
            outlines = text.get("useOutlines", None)
            hex_color = text.get("color", None)
            rgb_color = utils.hex_to_rgb(hex_color) if hex_color is not None else None

            text_items = []
            if "*" in char_ids:
                text_items = xml_tags.findall(
                    f"./item[@type='DefineEditTextTag'][@characterID]"
                )
                if not text_items:
                    self.log.warning(
                        f"Failed to patch texts: Found no text items in XML!"
                    )
            else:
                for char_id in char_ids:
                    text_items += xml_tags.findall(
                        f"./item[@type='DefineEditTextTag'][@characterID='{char_id}']"
                    )
                    if not text_items:
                        self.log.warning(
                            f"Failed to patch text with character id '{char_id}': Text not found in XML!"
                        )
                        continue

            for text_item in text_items:
                # Patch font id
                if font_id is not None:
                    text_item.attrib["fontId"] = str(font_id)

                # Patch outlines
                if outlines is not None:
                    text_item.attrib["useOutlines"] = str(outlines).lower()

                # Patch color
                if hex_color is not None:
                    # Patch initial text
                    init_text = text_item.attrib["initialText"]
                    init_text_dec = html.unescape(init_text)
                    init_text_dec = re.sub('color="(.*?)"', f'color="#{hex_color[0:6]}"', init_text_dec)
                    # init_text_enc = html.escape(init_text_dec)
                    init_text_enc = init_text_dec
                    text_item.attrib["initialText"] = init_text_enc

                    # Patch textColor tag
                    text_color = text_item.find("./textColor[@type='RGBA']")
                    text_color.attrib["red"] = str(rgb_color[0])
                    text_color.attrib["green"] = str(rgb_color[1])
                    text_color.attrib["blue"] = str(rgb_color[2])
                    text_color.attrib["alpha"] = str(rgb_color[3])

        self.log.info("Writing XML file...")
        with open(xml_file, "wb") as file:
            xml_data.write(file, encoding="utf8")

        # Optional debug XML file
        _debug_xml = (Path(".") / f"{xml_file.stem}.xml").resolve()
        with open(_debug_xml, "wb") as file:
            xml_data.write(_debug_xml, encoding="utf8")
        self.log.debug(f"Debug written to '{_debug_xml}'.")

        self.log.info("Patched XML file.")

    def _patch_shapes(self, patch_data: dict):
        shapes: Dict[Path, List[int]] = {}
        for shape_data in patch_data.get("shapes", []):
            shape_path = self.patch_path / shape_data["filePath"]
            if shape_path in shapes:
                shapes[shape_path] += shape_data["index"]
            else:
                shapes[shape_path] = shape_data["index"]

        self.ffdec_interface.replace_shapes(shapes)                

    def _patch_swf(self, swf_path: Path, patch_data: dict):
        # 2) Initialize FFDec interface
        self.ffdec_interface = ffdec.FFDec(swf_path, self.app)

        _xml: bool = False

        # 3) Patch shapes into SWF
        if patch_data.get("shapes") is not None:
            self._patch_shapes(patch_data)

            for shape in patch_data["shapes"]:
                if shape.get("shapeBounds", None):
                    _xml = True
                    break

        if not _xml:
            _xml = patch_data.get("text") or patch_data.get("sprites") or patch_data.get("header")

        # 4) Check if XML has to be done
        if _xml:
            # 4) Convert SWF to XML
            xml_file = self.ffdec_interface.swf2xml()

            # 5) Patch XML
            self._patch_xml(xml_file, patch_data)

            # 6) Convert XML back to SWF
            patched_swf = self.ffdec_interface.xml2swf(xml_file).resolve()
        else:
            patched_swf = swf_path.resolve()

        # 7) Copy patched SWF to current directory
        output_path = Path(".").resolve().parent / swf_path.relative_to(self.tmpdir / "RaceMenu")
        self.log.info(f"Writing output to '{output_path}'")
        output_path = output_path.resolve()
        os.makedirs(output_path.parent, exist_ok=True)
        if output_path.is_file():
            self.log.warning("Existing file gets overwritten!")
            os.remove(output_path)
        shutil.copyfile(
            patched_swf,
            output_path
        )

    def patch(self):
        """
        Patches RaceMenu through following process:
            1. Extract RaceMenu BSA to a temp folder.
            2. Initialize FFDec commandline interface.
            3. Patch shapes.
            4. Convert SWF to XML.
            5. Patch XML.
            6. Convert XML back to SWF.
            7. Copy SWF to current directory.
        """

        self.log.info("Patching RaceMenu...")

        # 0) Create Temp folder
        with tmp.TemporaryDirectory(prefix="DRIP_") as tmpdir:
            self.tmpdir = Path(tmpdir).resolve()

            # 1) Extract RaceMenu BSA to Temp folder
            bsa_path = self._extract_bsa()

            # 2) Patch SWFs according to patch data
            for c, (file, patch_data) in enumerate(self.patch_data.items()):
                file: Path = bsa_path / "interface" / file
                self.log.info(f"Patching file '{file.name}'... ({c+1}/{len(self.patch_data)})")

                self._patch_swf(file, patch_data)

        self.log.info("Patch complete!")
        self.app.done_signal.emit()

