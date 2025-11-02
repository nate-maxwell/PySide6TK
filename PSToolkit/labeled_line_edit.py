"""
# Labeled Line Edit

* Descriptions

    A UI component class that is a label and a line edit. This is mostly
    for eliminating boilerplate for tools that have a labeled row that
    contains a line edit.
"""


from PySide6 import QtWidgets


class LabeledLineEdit(QtWidgets.QWidget):
    def __init__(self, text: str, vertical: bool = False) -> None:
        super().__init__()
        if vertical:
            self.layout_main = QtWidgets.QVBoxLayout()
        else:
            self.layout_main = QtWidgets.QHBoxLayout()

        self.layout_main.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout_main)
        self.label = QtWidgets.QLabel(text)
        self.line_edit = QtWidgets.QLineEdit()
        self.layout_main.addWidget(self.label)
        self.layout_main.addWidget(self.line_edit)

    @property
    def text(self) -> str:
        """Returns the current line edit text."""
        return self.line_edit.text()

    def set_text(self, s: str) -> None:
        """Sets the text of the line edit."""
        self.line_edit.setText(s)

    def set_placeholder_text(self, s: str) -> None:
        """Sets the placeholder text of the line edit."""
        self.line_edit.setPlaceholderText(s)

    def clear(self) -> None:
        """Shortened namespace to clear text."""
        self.line_edit.clear()
