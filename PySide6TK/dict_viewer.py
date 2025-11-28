"""
# Dictionary Viewer

* Description:

    A menu that displays keys and values of a dictionary, recursively
    generating for nested dictionaries.
"""

from collections.abc import Mapping
from collections.abc import Sequence
from typing import Any

from PySide6 import QtWidgets

from PySide6TK import shapes
from PySide6TK.groupbox import GroupBox
from PySide6TK.labeled_line_edit import LabeledLineEdit


class DictViewer(GroupBox):
    """A collapsible widget for visualizing nested dictionary data structures.

    This class provides a hierarchical, collapsible UI for displaying
    dictionary-like mappings in a structured and readable form. Each key-value
    pair is rendered as a labeled row; nested dictionaries are represented as
    additional collapsible :class:`DictViewer` instances.

    Example:
        >>> data = {
        ...     'Project': 'Lucid',
        ...     'Settings': {
        ...         'Resolution': '4K',
        ...         'Framerate': 24,
        ...     },
        ... }
        >>> viewer = DictViewer('Project Data', data, default_closed=False)
        >>> viewer.refresh()

    Attributes:
        data (Mapping): The dictionary or mapping object being visualized.
        default_closed (bool): Whether the top-level group starts in a
            collapsed state. Defaults to ``False``.

    Args:
        menu_title (str): The title displayed in the collapsible group box.
        data (Mapping): The dictionary data to visualize.
        default_closed (bool): If ``True``, the group starts collapsed by
            default. Defaults to ``False``.

    Notes:
        - Nested dictionaries are automatically converted into nested
          :class:`DictViewer` widgets.
        - Non-dictionary values are displayed as read-only line edits.
        - Calling :meth:`refresh` rebuilds the layout to reflect updated data.
        - A thin horizontal separator line is added between each entry for
          visual clarity.
    """

    def __init__(self,
                 menu_title: str,
                 data: Mapping,
                 default_closed: bool = False) -> None:
        super().__init__(menu_title, True)
        self.default_closed = default_closed
        self.setMinimumWidth(250)
        self.data = data
        self.refresh()
        self.add_stretch()
        if self.default_closed:
            self.setChecked(False)

    def refresh(self) -> None:
        """Redraws the menu from self.data."""
        self.clear()
        self._refresh(self.data)

    def _refresh(self, data: Mapping) -> None:
        """Recursive call for refreshing.
        Data values could be nested dictionaries.
        Keys are cast to str and single row value are cast to str, while dict
        values are kept the same.
        """
        for k, v in data.items():
            self.add_widget(shapes.HorizontalLine())
            if isinstance(v, Mapping):
                self._add_row_mapping(str(k), v)
            elif not isinstance(v, (str, bytes, bytearray)) and isinstance(v, Sequence):
                self._add_row_sequence(str(k), v)
            else:
                self._add_row_str(str(k), str(v))

    def _add_row_mapping(self, label: str, data: Mapping) -> None:
        """Adds a nested DictViewer if the value of the instanced data var
        was another dictionary.
        """
        wid_value = DictViewer(label, data, False)
        self.add_widget(wid_value)

    def _add_row_sequence(self, label: str, data: Sequence[Any]) -> None:
        """Adds a nested dict viewer showing element numbers to values."""
        group_box = GroupBox(label)
        for i in data:
            if isinstance(i, Mapping):
                self._add_row_mapping('', i)
            else:
                line_edit = QtWidgets.QLineEdit(str(i))
                line_edit.setReadOnly(True)
                line_edit.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,
                                        QtWidgets.QSizePolicy.Policy.Preferred)
                group_box.add_widget(line_edit)

        if group_box.layout.count():
            self.add_widget(group_box)

    def _add_row_str(self, label: str, value: str) -> None:
        """Adds a row with a label and read-only line edit containing a str()
        version of the given value.
        """
        labeled_line_edit = LabeledLineEdit(label)
        labeled_line_edit.set_text(value)
        labeled_line_edit.set_label_expanding(True)
        labeled_line_edit.set_read_only(True)
        self.add_widget(labeled_line_edit)
