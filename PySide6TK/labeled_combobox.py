"""
# Labeled Combo Box

* Descriptions

    A UI component class that is a label and a combobox. This is mostly
    for eliminating boilerplate for tools that have a labeled row that
    contains a combobox.
"""

from typing import Optional

from PySide6 import QtCore
from PySide6 import QtWidgets

import PySide6TK.regx
import PySide6TK.dialogs
from PySide6TK.enums import Orient


class LabeledComboBox(QtWidgets.QWidget):
    """A composite widget combining a label and a combo box.

    This class provides a labeled drop-down selection field with optional
    support for dynamically adding new items. The layout can be horizontal
    or vertical, depending on the use case. It simplifies UI construction
    for settings panels, tool dialogs, and configurable parameter groups.

    Example:
        >>> quality_box = LabeledComboBox('Quality', ['Low', 'Medium', 'High'])
        >>> print(quality_box.current_text())

        >>> appendable_box = LabeledComboBox('Category', appendable=True)
        >>> appendable_box._append_item()  # Prompts user to add a new entry

    Attributes:
        layout_main (QtWidgets.QLayout): The main layout managing the label,
            combo box, and optional add button. Uses either ``QHBoxLayout``
            or ``QVBoxLayout`` depending on the ``vertical`` argument.
        label (QtWidgets.QLabel): The descriptive label displayed next to or
            above the combo box.
        cmb_box (QtWidgets.QComboBox): The drop-down selection widget.
        btn_add (Optional[QtWidgets.QPushButton]): Optional “+” button for
            appending new combo box entries when ``appendable`` is ``True``.

    Args:
        text (str): The label text displayed beside or above the combo box.
        contents (Optional[list[str]]): The initial list of items to populate
            the combo box with. Defaults to ``None``.
        appendable (bool): If ``True``, adds a “+” button allowing users to
            append new items interactively via a text dialog. Defaults to
            ``False``.
        label_pos (PySide6TK.enums.Orient): Whether to put the label on
            ``Top``, ``Bottom``, ``Left``, or ``Right`` of the combobox.
            Defaults to ``Left``.

    Notes:
        - The combo box automatically resizes horizontally to fill available
          space.
        - When ``appendable`` is enabled, new items are sorted alphabetically
          after being added.
    """

    def __init__(self,
                 text: str,
                 contents: Optional[list[str]] = None,
                 appendable: bool = False,
                 label_pos: Orient = Orient.Left) -> None:
        super().__init__()

        self.label = QtWidgets.QLabel(text)
        self.new_item_text: str = 'Name:'
        self.cmb_box = QtWidgets.QComboBox()
        self.cmb_box.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,
                                   QtWidgets.QSizePolicy.Policy.Fixed)
        self.hlayout_box = QtWidgets.QHBoxLayout()  # for box + button

        match label_pos:
            case Orient.Top:
                self.layout_main = QtWidgets.QVBoxLayout()
                self.layout_main.addWidget(self.label)
                self.layout_main.addLayout(self.hlayout_box)
            case Orient.Bottom:
                self.layout_main = QtWidgets.QVBoxLayout()
                self.layout_main.addLayout(self.hlayout_box)
                self.layout_main.addWidget(self.label)
            case Orient.Left:
                self.layout_main = QtWidgets.QHBoxLayout()
                self.layout_main.addWidget(self.label)
                self.layout_main.addLayout(self.hlayout_box)
            case Orient.Right:
                self.layout_main = QtWidgets.QHBoxLayout()
                self.layout_main.addLayout(self.hlayout_box)
                self.layout_main.addWidget(self.label)

        self.layout_main.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout_main)

        self.hlayout_box.addWidget(self.cmb_box)

        if contents:
            self.cmb_box.addItems(contents)

        if appendable:
            self.btn_add = QtWidgets.QPushButton('+')
            self.hlayout_box.addWidget(self.btn_add)
            self.btn_add.clicked.connect(self._add_button_connection)

    def current_text(self) -> str:
        """Shortened namespace way to get current selected item."""
        return self.cmb_box.currentText()

    def set_current_text(self, s: str) -> None:
        """Shortened namespace way to set current combo box text."""
        self.cmb_box.setCurrentText(s)

    def get_items(self) -> list[str]:
        return [self.cmb_box.itemText(i) for i in range(self.cmb_box.count())]

    def item_is_alphanum(self) -> bool:
        """Returns whether the current item does not contain non-alpha-numeric
        or non-underscore characters.
        """
        return PySide6TK.regx.validation_no_special_chars(
            self.cmb_box.currentText())

    def clear(self) -> None:
        """Shortened namespace way to clear items."""
        self.cmb_box.clear()

    def add_items(self, items: list[str] = None):
        """Adds items much like QtWidgets.QComboBox.addItems()."""
        if items is None:
            return
        self.cmb_box.addItems(items)

    def add_unique(self, item: str) -> None:
        if self.cmb_box.findText(item) == -1:
            self.cmb_box.addItem(item)

    def _add_button_connection(self) -> None:
        item_added = self._append_item()
        if item_added:
            self.on_button_clicked()

    def on_button_clicked(self) -> None:
        """A hook for adding functionality to the user adding an item to
        the box.
        """
        pass

    def _append_item(self) -> bool:
        dlg = PySide6TK.dialogs.SingleLineTextDialog('New Item', self.new_item_text)
        if dlg.exec():
            new_item = self.append_item_formatter(dlg.text())
            if new_item == '':
                return False

            self.add_unique(new_item)
            self.cmb_box.model().sort(0, QtCore.Qt.SortOrder.AscendingOrder)
            self.cmb_box.setCurrentText(new_item)
            return True

        return False

    def append_item_formatter(self, raw: str) -> str:
        """Overridable method for formatting the text captured by the dialog box
        before adding it to the combobox contents.

        If the method returns an empty string, the item is not added.
        """
        return raw

    def set_current_index(self, index: int):
        """Sets the combobox active index much like
        QtWidgets.QComboBox.setCurrentIndex().
        """
        self.cmb_box.setCurrentIndex(index)

    def set_label_expanding(self, expand: bool) -> None:
        """Sets the label as expanding if True, and preferred if False."""
        if expand:
            policy = QtWidgets.QSizePolicy.Policy.Expanding
        else:
            policy = QtWidgets.QSizePolicy.Policy.Preferred
        self.label.setSizePolicy(policy, QtWidgets.QSizePolicy.Policy.Preferred)
