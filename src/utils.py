"""
Part of Dynamic RaceMenu Interface Patcher (DRIP).
Contains utility classes and functions.

Licensed under Attribution-NonCommercial-NoDerivatives 4.0 International
"""

import ctypes
import sys
import os
import subprocess
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
    
    def __repr__(self):
        return self.objectName()

    def __str__(self):
        return self.objectName()


class StdoutHandler(qtc.QObject):
    """
    Redirector class for sys.stdout.

    Redirects sys.stdout to self.output_signal [QtCore.Signal].
    """

    output_signal = qtc.Signal(object)

    def __init__(self, parent: qtc.QObject):
        super().__init__(parent)

        self._stream = sys.stdout
        sys.stdout = self
        self._content = ""

    def write(self, text: str):
        self._stream.write(text)
        self._content += text
        self.output_signal.emit(text)

    def __getattr__(self, name: str):
        return getattr(self._stream, name)

    def __del__(self):
        try:
            sys.stdout = self._stream
        except AttributeError:
            pass


def hex_to_rgb(value: str):
    """
    Converts hexadecimal color values
    to a tuple containing the values in rgb.    
    """

    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

def lower_dict(nested_dict: dict):
    new_dict = {}

    for key, value in nested_dict.items():
        if isinstance(value, dict):
            new_dict[key] = lower_dict(value)
        elif isinstance(value, str):
            new_dict[key] = value.lower()
        else:
            new_dict[key] = value

    return new_dict

def apply_dark_title_bar(widget: qtw.QWidget):
    """
    Applies dark title bar to <widget>.

    
    More information here:

    https://docs.microsoft.com/en-us/windows/win32/api/dwmapi/ne-dwmapi-dwmwindowattribute
    """

    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    set_window_attribute = ctypes.windll.dwmapi.DwmSetWindowAttribute
    hwnd = widget.winId()
    rendering_policy = DWMWA_USE_IMMERSIVE_DARK_MODE
    value = 2
    value = ctypes.c_int(value)
    set_window_attribute(
        hwnd,
        rendering_policy,
        ctypes.byref(value),
        ctypes.sizeof(value)
    )

def check_java():
    """
    Checks if java is installed and added to PATH.
    """

    try:
        subprocess.check_call(
            ["java", "-version"],
            shell=True,
            stdout=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return True
    except subprocess.CalledProcessError:
        return False
