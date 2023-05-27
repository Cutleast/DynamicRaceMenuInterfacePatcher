"""
Part of RaceMenu Interface Patcher (RIP).
Contains utility classes and functions.

Licensed under Attribution-NonCommercial-NoDerivatives 4.0 International
"""

import os
import sys
from pathlib import Path
from typing import Callable

import qtpy.QtCore as qtc
import qtpy.QtGui as qtg
import qtpy.QtWidgets as qtw


class Thread(qtc.QThread):
    """
    Proxy class for QThread.
    Takes a callable function or method
    as additional parameter
    that is executed in the QThread.
    """

    def __init__(self, target: Callable, name: str = None, parent: qtw.QWidget = None):
        super().__init__(parent)

        self.target = target

        if name is not None:
            self.setObjectName(name)

    def run(self):
        self.target()


class StdoutHandler(qtc.QObject):
    output_signal = qtc.Signal(object)

    def __init__(self, parent: qtc.QObject):
        super().__init__(parent)

        self._stream = sys.stdout
        sys.stdout = self

    def write(self, text: str):
        self._stream.write(text)
        self.output_signal.emit(text)

    def __getattr__(self, name: str):
        return getattr(self._stream, name)

    def __del__(self):
        try:
            sys.stdout = self._stream
        except AttributeError:
            pass
