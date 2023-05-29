"""
Name: RaceMenu Interface Patcher (RIP)
Author: Cutleast
License: Attribution-NonCommercial-NoDerivatives 4.0 International
Python Version: 3.11.2
Qt Version: 6.5.1
"""

import logging
import os
import sys
from pathlib import Path

import qtpy.QtCore as qtc
import qtpy.QtGui as qtg
import qtpy.QtWidgets as qtw

import utils
import errors


class MainApp(qtw.QApplication):
    """
    Main application class.
    """

    # Application properties
    name = "RaceMenu Interface Patcher"
    version = "1.0"

    def __init__(self):
        super().__init__()

        # Set up protocol structure
        self.log = logging.getLogger(self.__repr__())
        log_fmt = "[%(asctime)s.%(msecs)03d]"
        log_fmt += "[%(levelname)s]"
        log_fmt += "[%(threadName)s.%(name)s.%(funcName)s]: "
        log_fmt += "%(message)s"
        self.log_fmt = logging.Formatter(
            log_fmt,
            datefmt="%d.%m.%Y %H:%M:%S"
        )
        self.std_handler = utils.StdoutHandler(self)
        self.log_str = logging.StreamHandler(self.std_handler)
        self.log_str.setFormatter(self.log_fmt)
        self.log.addHandler(self.log_str)
        self.log_level = 10 # Debug level
        self.log.setLevel(self.log_level)

        self.root = qtw.QWidget()
        self.root.setWindowTitle(f"{self.name} v{self.version}")
        self.root.setStyleSheet((Path(".") / "assets" / "style.qss").read_text())
        self.root.setMinimumWidth(1000)

        self.layout = qtw.QVBoxLayout()
        self.root.setLayout(self.layout)

        self.conf_layout = qtw.QGridLayout()
        self.layout.addLayout(self.conf_layout)

        racemenu_path_label = qtw.QLabel("Choose path to RaceMenu folder:")
        self.conf_layout.addWidget(racemenu_path_label, 0, 0)
        self.racemenu_path_entry = qtw.QLineEdit()
        self.conf_layout.addWidget(self.racemenu_path_entry, 0, 1)
        racemenu_path_button = qtw.QPushButton("Browse...")

        def browse_racemenu_path():
            file_dialog = qtw.QFileDialog(self.root)
            file_dialog.setWindowTitle("Browse RaceMenu...")
            path = Path(self.racemenu_path_entry.text()) if self.racemenu_path_entry.text() else Path(".")
            path = path.resolve()
            file_dialog.setDirectory(str(path.parent))
            file_dialog.setFileMode(qtw.QFileDialog.FileMode.Directory)
            if file_dialog.exec():
                folder = file_dialog.selectedFiles()[0]
                folder = os.path.normpath(folder)
                self.racemenu_path_entry.setText(folder)
        racemenu_path_button.clicked.connect(browse_racemenu_path)

        self.conf_layout.addWidget(racemenu_path_button, 0, 2)

        patch_path_label = qtw.QLabel("Choose path to RaceMenu patch folder:")
        self.conf_layout.addWidget(patch_path_label, 1, 0)
        self.patch_path_entry = qtw.QLineEdit()
        self.conf_layout.addWidget(self.patch_path_entry, 1, 1)
        patch_path_button = qtw.QPushButton("Browse...")

        def browse_patch():
            file_dialog = qtw.QFileDialog(self.root)
            file_dialog.setWindowTitle("Browse RaceMenu Patch...")
            path = Path(self.patch_path_entry.text()) if self.patch_path_entry.text() else Path(".")
            path = path.resolve()
            file_dialog.setDirectory(str(path.parent))
            file_dialog.setFileMode(qtw.QFileDialog.FileMode.Directory)
            if file_dialog.exec():
                folder = file_dialog.selectedFiles()[0]
                folder = os.path.normpath(folder)
                self.patch_path_entry.setText(folder)
        patch_path_button.clicked.connect(browse_patch)

        self.conf_layout.addWidget(patch_path_button, 1, 2)

        self.protocol_widget = qtw.QTextEdit()
        self.protocol_widget.setReadOnly(True)
        self.protocol_widget.setObjectName("protocol")
        self.layout.addWidget(self.protocol_widget, 1)

        self.patch_button = qtw.QPushButton("Patch!")
        self.patch_button.clicked.connect(self.run_patcher)
        # self.patch_button.setDisabled(True)
        self.layout.addWidget(self.patch_button)

        self.std_handler.output_signal.connect(self.handle_stdout)

        self.log.debug("Program started!")

        self.root.show()

    def __repr__(self):
        return "MainApp"

    def handle_stdout(self, text):
        self.protocol_widget.moveCursor(qtg.QTextCursor.MoveOperation.End)
        self.protocol_widget.insertPlainText(text)
    
    def run_patcher(self):
        try:
            self.patcher = patcher.Patcher(
                self,
                Path(self.patch_path_entry.text()).resolve(),
                Path(self.racemenu_path_entry.text()).resolve()
            )
            print(self.patcher.patch_data)
        except errors.InvalidPatchError:
            self.log.error("Selected patch is invalid!")


if __name__ == "__main__":
    import patcher

    app = MainApp()
    app.exec()