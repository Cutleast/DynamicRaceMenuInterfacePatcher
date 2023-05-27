"""
Part of RaceMenu Interface Patcher (RIP).
Contains FFDec (JPEXS Free Flash Decompiler) interface.

Licensed under Attribution-NonCommercial-NoDerivatives 4.0 International
"""

from dataclasses import dataclass
import subprocess
import os
import logging
import sys
from typing import List
from pathlib import Path
from main import MainApp


@dataclass
class Job:
    """
    Job class for commandline interface.
    """

    name: str
    cmd: str # commandline args
    status: str = None # 'pending', 'running' or 'done'

    def __repr__(self):
        return self.name


class FFDec:
    """
    Class for FFDec commandline interface.
    """

    _bin_path = Path(".") / "assets" / "ffdec" / "ffdec.bat"
    _swf_path = None
    _queue: List[Job] = None
    _pid: int = None

    def __init__(self, swf_path: Path, app: MainApp):
        self.app = app

        self.log = logging.getLogger(self.__repr__())
        self.log.addHandler(self.app.log_str)
        self.log.setLevel(self.app.log.level)

        self._swf_path = swf_path

        self._queue = []

    def run_job(self, job: Job):
        _arg = job.cmd
        _arg = _arg.replace("[SWF_FILE]", f'"{self._swf_path}"')

        self.log.debug(f"Running job '{job.name}'...")

        with subprocess.Popen(
            args=_arg,
            executable=self._bin_path,
            shell=True,
            stdin=subprocess.PIPE,
            stdout=sys.stdout,
            text=True,
            encoding="utf8",
            errors="ignore") as process:
            job.status = "running"
            self._pid = process.pid
        
        job.status = "done"
        self._pid = None

        self.log.debug("Job ran successfully!")

    def run(self):
        for job in self._queue:
            self.run_job(job)

    @staticmethod
    def replace_job(file: Path, id: str, args: str = ""):
        """
        Creates replace job and returns it.        
        """

        cmd = f"""-replace [SWF_FILE] [SWF_FILE] {id} "{file}" {args}"""
        name = f"Replace_{id}"
        job = Job(name, cmd)

        return job

