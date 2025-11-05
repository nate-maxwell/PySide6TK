"""
# File Selector

* Description

    A simple gui class that lets users specify file paths through a QFileDialog
    and then displays and stores the path.
"""

from pathlib import Path

from PySide6 import QtWidgets

from PySide6TK.labeled_line_edit import LabeledLineEdit


class FileSelector(QtWidgets.QWidget):
    def __init__(self, name: str) -> None:
        """Label text before line edit."""
        super().__init__()
        self.name = name
        self._create_widgets()
        self._create_layout()
        self._create_connections()

    def _create_widgets(self) -> None:
        self.hlayout_main = QtWidgets.QHBoxLayout()
        self.le_path = LabeledLineEdit(self.name)
        self.le_path.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,
                                   QtWidgets.QSizePolicy.Policy.Preferred)
        self.btn_exe = QtWidgets.QPushButton('Open')

    def _create_layout(self) -> None:
        self.hlayout_main.addWidget(self.le_path)
        self.hlayout_main.addWidget(self.btn_exe)
        self.setLayout(self.hlayout_main)

    def _create_connections(self) -> None:
        self.btn_exe.clicked.connect(self.find_path)

    def find_path(self) -> None:
        directory = ''
        if self.le_path.text():
            directory = self.le_path.text()
        location, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', directory)
        if location:
            self.le_path.set_text(location)

    @property
    def path(self) -> Path:
        return Path(self.le_path.text())
