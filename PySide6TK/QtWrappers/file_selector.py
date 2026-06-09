"""
# File Selector

* Description

    A simple gui class that lets users specify file paths through a QFileDialog
    and then displays and stores the path.
"""

from pathlib import Path

from PySide6 import QtWidgets

from PySide6TK.QtWrappers.labeled_line_edit import LabeledLineEdit


class FileSelector(QtWidgets.QWidget):
    """A labeled file path selector with an integrated browse button.

    This class combines a labeled line edit and an “Open” button to create
    a simple UI component for selecting files from disk. When the button is
    pressed, a file dialog is opened, and the chosen path is displayed in
    the line edit. The selected path can then be accessed via the ``path``
    property.

    Example:
        >>> file_selector = FileSelector('File Path:')
        >>> print(file_selector.path)
        >>> # Opens a dialog to choose a file
        >>> file_selector.find_path()

    Attributes:
        name (str): The label text displayed before the input field.
        hlayout_main (QtWidgets.QHBoxLayout): The horizontal layout managing
            the label, line edit, and open button.
        le_path (LabeledLineEdit): The labeled line edit used to display and
            edit the selected file path.
        btn_exe (QtWidgets.QPushButton): The button that opens the file
            browser dialog.

    Args:
        text (str): The label text to display before the line edit.

    Notes:
        - The “Open” button launches a standard ``QFileDialog``.
        - If the line edit already contains a valid path, the file dialog
          will start in that directory.
        - The selected file path is stored internally and can be accessed as
          a ``pathlib.Path`` via the :attr:`path` property.
    """

    def __init__(self, text: str) -> None:
        """Label text before line edit."""
        super().__init__()
        self.name = text
        self._create_widgets()
        self._create_layout()
        self._create_connections()

    def _create_widgets(self) -> None:
        self.hlayout_main = QtWidgets.QHBoxLayout()
        self.le_path = LabeledLineEdit(self.name)
        self.le_path.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Preferred,
        )
        self.btn_exe = QtWidgets.QPushButton("Open")

    def _create_layout(self) -> None:
        self.hlayout_main.addWidget(self.le_path)
        self.hlayout_main.addWidget(self.btn_exe)
        self.setLayout(self.hlayout_main)

    def _create_connections(self) -> None:
        self.btn_exe.clicked.connect(self.find_path)

    def find_path(self) -> None:
        directory = ""
        if self.le_path.text():
            directory = self.le_path.text()
        location, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open File", directory
        )
        if location:
            self.le_path.set_text(location)

    @property
    def path(self) -> Path:
        return Path(self.le_path.text())
