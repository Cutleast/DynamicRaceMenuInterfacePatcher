"""
Name: Dynamic RaceMenu Interface Patcher (DRIP)
Author: Cutleast
License: Attribution-NonCommercial-NoDerivatives 4.0 International
Python Version: 3.11.2
Qt Version: 6.5.1
"""

import logging
import os
import shutil
import sys
import time
from pathlib import Path

import qtpy.QtCore as qtc
import qtpy.QtGui as qtg
import qtpy.QtWidgets as qtw

import errors
import utils


class MainApp(qtw.QApplication):
    """
    Main application class.
    """

    # Application properties
    name = "Dynamic RaceMenu Interface Patcher"
    version = "1.0"

    patcher_thread: utils.Thread = None
    done_signal = qtc.Signal()
    start_time: int = None

    def __init__(self):
        super().__init__()

        # Set up protocol structure
        self.log = logging.getLogger(self.__repr__())
        log_fmt = "[%(asctime)s.%(msecs)03d]"
        log_fmt += "[%(levelname)s]"
        log_fmt += "[%(name)s.%(funcName)s]: "
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
        self._excepthook = sys.excepthook
        sys.excepthook = self.handle_exception

        self.root = qtw.QWidget()
        self.root.setWindowTitle(f"{self.name} v{self.version}")
        self.root.setStyleSheet((Path(".") / "assets" / "style.qss").read_text())
        self.root.setWindowIcon(qtg.QIcon("./assets/icon.ico"))
        self.root.setMinimumWidth(1000)
        self.root.setMinimumHeight(500)

        self.layout = qtw.QVBoxLayout()
        self.root.setLayout(self.layout)

        self.conf_layout = qtw.QGridLayout()
        self.layout.addLayout(self.conf_layout)

        racemenu_path_label = qtw.QLabel("Choose path to RaceMenu folder:")
        self.conf_layout.addWidget(racemenu_path_label, 0, 0)
        self.racemenu_path_entry = qtw.QLineEdit()
        self.racemenu_path_entry.setText(self.scan_for_racemenu())
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
        self.patch_path_entry.setText(self.scan_for_patch())
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
        self.layout.addWidget(self.patch_button)

        self.std_handler.output_signal.connect(self.handle_stdout)
        self.std_handler.output_signal.emit(self.std_handler._content)
        self.done_signal.connect(self.done)

        self.log.debug("Program started!")

        self.root.show()

    def __repr__(self):
        return "MainApp"

    def handle_exception(self, exc_type, exc_value, exc_traceback):
        self.log.critical(
            "An uncaught exception occured:",
            exc_info=(exc_type, exc_value, exc_traceback)
        )

    def handle_stdout(self, text):
        self.protocol_widget.insertPlainText(text)
        self.protocol_widget.moveCursor(qtg.QTextCursor.MoveOperation.End)

    def run_patcher(self):
        try:
            self.patcher = patcher.Patcher(
                self,
                Path(self.patch_path_entry.text()).resolve(),
                Path(self.racemenu_path_entry.text()).resolve()
            )
            self.patcher_thread = utils.Thread(
                self.patcher.patch,
                "PatcherThread",
                self
            )
        except errors.InvalidPatchError as ex:
            self.log.error(f"Selected patch is invalid: {ex}")
            return

        self.patch_button.setText("Cancel")
        self.patch_button.clicked.disconnect(self.run_patcher)
        self.patch_button.clicked.connect(self.cancel_patcher)

        self.start_time = time.time()

        self.patcher_thread.start()

    def done(self):
        self.patch_button.setText("Patch!")
        self.patch_button.clicked.disconnect(self.cancel_patcher)
        self.patch_button.clicked.connect(self.run_patcher)

        self.log.info(f"Patching done in {(time.time() - self.start_time):.3f} second(s).")

    def cancel_patcher(self):
        self.patcher_thread.terminate()

        if self.patcher.ffdec_interface is not None:
            if self.patcher.ffdec_interface._pid is not None:
                os.system(f"taskkill /F /PID {self.patcher.ffdec_interface._pid}")
                self.log.info(f"Killed FFDec with pid {self.patcher.ffdec_interface._pid}.")
                self.patcher.ffdec_interface._pid = None

        if self.patcher.tmpdir is not None:
            if self.patcher.tmpdir.is_dir():
                time.sleep(3)
                shutil.rmtree(self.patcher.tmpdir)
                self.log.info("Cleaned up temporary folder.")

        self.done()
        self.log.warning("Patch incomplete!")

    def scan_for_racemenu(self):
        parent_folder = Path(".").resolve().parent.parent

        for folder in parent_folder.glob("**\\RaceMenu.bsa"):
            return str(folder.resolve().parent)

        return ""

    def scan_for_patch(self):
        parent_folder = Path(".").resolve().parent.parent

        for folder in parent_folder.glob("**\\patch.json"):
            return str(folder.resolve().parent)

        return ""


if __name__ == "__main__":
    import patcher

    app = MainApp()
    app.exec()
