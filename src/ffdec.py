"""
Part of Dynamic RaceMenu Interface Patcher (DRIP).
Contains FFDec (JPEXS Free Flash Decompiler) interface.

Licensed under Attribution-NonCommercial-NoDerivatives 4.0 International
"""

import logging
import subprocess
from pathlib import Path
from typing import Dict, List

from main import MainApp


class FFDec:
    """
    Class for FFDec commandline interface.
    """

    _bin_path = (Path(".") / "assets" / "ffdec" / "ffdec.bat").resolve()
    _swf_path = None
    _pid: int = None

    def __init__(self, swf_path: Path, app: MainApp):
        self.app = app

        self.log = logging.getLogger(self.__repr__())
        self.log.addHandler(self.app.log_str)
        self.log.setLevel(self.app.log.level)

        self._swf_path = swf_path

    def __repr__(self):
        return "FFDecInterface"

    def _exec_command(self, args: str):
        _cmd = f""""{self._bin_path}" {args}"""
        # self.log.debug(f"""Commandline: '{_cmd}'""")

        with subprocess.Popen(
            _cmd,
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
            encoding="utf8",
            errors="ignore"
        ) as process:
            self._pid = process.pid
            for line in process.stdout:
                self.log.info(f"[FFDec]: {line}")

        self._pid = None

    def replace_shapes(self, shapes: Dict[Path, List[int]]):
        """
        Replaces shapes in SWF by <shapes>.

        Params:
            shapes: dictionary, keys are svg paths and values are list with indexes
        """

        self.log.info("Patching shapes...")

        cmds: List[str] = []
        for c, (shape, indexes) in enumerate(shapes.items()):
            shape = shape.resolve()
            if not shape.is_file():
                self.log.error(f"Failed to patch shape {shape.name}: File does not exist!")
                continue
            if shape.suffix != ".svg":
                self.log.warning(f"File type '{shape.suffix}' ({shape.name}) is not supported or tested and may lead to issues!")

            for index in indexes:
                cmd = f"""{index}\n{shape}\n"""
                cmds.append(cmd)
        cmdfile = self._swf_path.parent / "shapes.txt"
        with open(cmdfile, "w", encoding="utf8") as file:
            file.writelines(cmds)
        
        cmd = f"""-replace "{self._swf_path}" "{self._swf_path}" "{cmdfile.resolve()}" """

        self._exec_command(cmd)

        self.log.info("Shapes patched.")
    
    def swf2xml(self):
        """
        Converts SWF file to XML file and returns file path.
        """

        self.log.info("Converting SWF to XML...")

        out_path = self._swf_path.with_suffix(".xml")

        args = f"""-swf2xml "{self._swf_path}" "{out_path}" """
        self._exec_command(args)

        self.log.info("Converted to XML.")

        return out_path
    
    def xml2swf(self, xml_file: Path):
        """
        Converts XML file to SWF file and returns file path.
        """

        self.log.info("Converting XML to SWF...")

        out_path = xml_file.with_suffix(".swf")

        args = f"""-xml2swf "{xml_file}" "{out_path}" """
        self._exec_command(args)

        self.log.info("Converted to SWF.")

        return out_path

