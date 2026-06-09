"""
# Commonly Created Dialog Boxes

* Description:

    A library of commonly created simple dialog boxes.
"""


from typing import Optional

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets


class SingleLineTextDialog(QtWidgets.QDialog):
    """Dialog that gathers single-line text with optional regex validation.

    Args:
        title (str): Window title.
        label (str): Prompt displayed above the input.
        initial_text (str): Pre-filled text for the line edit.
        placeholder (str): Placeholder text for the line edit.
        regex_validator (Optional[QtCore.QRegularExpression]): Optional Qt
            regular expression for validation. If provided, OK is only enabled
            when the input is 'Acceptable'.
        allow_empty (bool): If False, OK is disabled until non-empty text is entered.
        parent (Optional[QtWidgets.QWidget]): Optional parent widget.
    """

    def __init__(
        self,
        title: str = 'Enter Text',
        label: str = 'Please enter text:',
        initial_text: str = '',
        placeholder: str = '',
        regex_validator: Optional[QtCore.QRegularExpression] = None,
        allow_empty: bool = True,
        parent: Optional[QtWidgets.QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)

        prompt = QtWidgets.QLabel(label, self)
        prompt.setWordWrap(True)

        self._line_edit = QtWidgets.QLineEdit(self)
        self._line_edit.setText(initial_text)
        if placeholder:
            self._line_edit.setPlaceholderText(placeholder)
        if regex_validator is not None:
            self._line_edit.setValidator(QtGui.QRegularExpressionValidator(regex_validator, self))

        buttons = QtWidgets.QDialogButtonBox(parent=self)
        buttons.addButton(QtWidgets.QDialogButtonBox.StandardButton.Ok)
        buttons.addButton(QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        self._ok_button = buttons.button(QtWidgets.QDialogButtonBox.StandardButton.Ok)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(prompt)
        layout.addWidget(self._line_edit)
        layout.addWidget(buttons)

        self._allow_empty = allow_empty
        self._line_edit.textChanged.connect(self._update_ok_enabled)
        self._update_ok_enabled()

        self.resize(420, 150)

    def text(self) -> str:
        """Return the current text value."""
        return self._line_edit.text()

    def _is_valid(self) -> bool:
        if not self._allow_empty and not self._line_edit.text().strip():
            return False
        validator = self._line_edit.validator()
        if validator is not None:
            text = self._line_edit.text()
            state, _, _ = validator.validate(text, 0)
            return state == QtGui.QValidator.State.Acceptable
        return True

    def _update_ok_enabled(self) -> None:
        self._ok_button.setEnabled(self._is_valid())

    def _on_accept(self) -> None:
        if not self._is_valid():
            QtWidgets.QMessageBox.warning(self, 'Invalid Input', 'Please enter a valid value.')
            return
        self.accept()


class MultiLineTextDialog(QtWidgets.QDialog):
    """Dialog that gathers multi-line text.

    Args:
        title (str): Window title.
        label (str): Prompt displayed above the input.
        initial_text (str): Pre-filled text for the text edit.
        placeholder (str): Placeholder text for the text edit (supported in recent Qt).
        allow_empty (bool): If False, OK is disabled until non-empty text is entered.
        parent (Optional[QtWidgets.QWidget]): Optional parent widget.
    """

    def __init__(
        self,
        title: str = 'Enter Text',
        label: str = 'Please enter text:',
        initial_text: str = '',
        placeholder: str = '',
        allow_empty: bool = True,
        parent: Optional[QtWidgets.QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)

        prompt = QtWidgets.QLabel(label, self)
        prompt.setWordWrap(True)

        self._text_edit = QtWidgets.QTextEdit(self)
        if initial_text:
            self._text_edit.setPlainText(initial_text)
        if placeholder:
            self._text_edit.setPlaceholderText(placeholder)

        buttons = QtWidgets.QDialogButtonBox(parent=self)
        buttons.addButton(QtWidgets.QDialogButtonBox.StandardButton.Ok)
        buttons.addButton(QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        self._ok_button = buttons.button(QtWidgets.QDialogButtonBox.StandardButton.Ok)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(prompt)
        layout.addWidget(self._text_edit)
        layout.addWidget(buttons)

        self._allow_empty = allow_empty
        self._text_edit.textChanged.connect(self._update_ok_enabled)
        self._update_ok_enabled()

        self.resize(560, 360)

    def text(self) -> str:
        """Return the current text value."""
        return self._text_edit.toPlainText()

    def _is_valid(self) -> bool:
        if not self._allow_empty and not self._text_edit.toPlainText().strip():
            return False
        return True

    def _update_ok_enabled(self) -> None:
        self._ok_button.setEnabled(self._is_valid())

    def _on_accept(self) -> None:
        if not self._is_valid():
            QtWidgets.QMessageBox.warning(self, 'Empty Input', 'Please enter a value.')
            return
        self.accept()
