"""
# Group Box

* Descriptions

    Small wrapper for a Qt group box to eliminate writing the layout
    setting, saving a few lines.
"""

from PySide6 import QtWidgets

import PySide6TK.QtWrappers.layout


class GroupBox(QtWidgets.QGroupBox):
    """A labeled container widget that groups related UI elements.

    This class extends ``QGroupBox`` to provide optional collapsible and
    orientation-based grouping of widgets and layouts. It simplifies
    organization of interface sections, allowing sections to expand or
    collapse dynamically if configured as collapsible.

    Example:
        >>> general_settings = GroupBox('General Settings', collapsible=True)
        >>> general_settings.add_widget(QtWidgets.QLabel('Username:'))
        >>> general_settings.add_widget(QtWidgets.QLineEdit())

    Attributes:
        layout (QtWidgets.QLayout): The main layout managing the grouped
            child widgets and sub-layouts. Uses ``QVBoxLayout`` or
            ``QHBoxLayout`` depending on the ``horizontal`` argument.

    Args:
        label (str): The title displayed at the top of the group box.
            Defaults to an empty string.
        collapsible (bool): If ``True``, the group box becomes checkable,
            allowing users to collapse or expand its contents by toggling
            the checkbox beside the label. Defaults to ``False``.
        horizontal (bool): If ``True``, uses a horizontal layout for its
            children; otherwise, uses a vertical layout. Defaults to ``False``.

    Notes:
        - When ``collapsible`` is enabled, the group box height dynamically
          adjusts to its collapsed or expanded state.
        - The helper function :func:`PySide6TK.QtWrappers.layout.clear_layout` is used
          to remove existing layout contents in :meth:`clear`.
        - Visibility changes are recursively applied via
          :func:`PySide6TK.QtWrappers.layout.set_layout_visibility` in
          :meth:`on_toggle`.
    """

    def __init__(
        self, label: str = "", collapsible: bool = False, horizontal: bool = False
    ) -> None:
        super().__init__(label)
        if horizontal:
            self.layout = QtWidgets.QHBoxLayout()
        else:
            self.layout = QtWidgets.QVBoxLayout()

        if collapsible:
            self.setCheckable(True)
            self.setChecked(True)
            self.toggled.connect(self.on_toggle)

        self.setLayout(self.layout)

    def clear(self) -> None:
        PySide6TK.QtWrappers.layout.clear_layout(self.layout)

    def add_widget(self, widget: QtWidgets.QWidget) -> None:
        self.layout.addWidget(widget)

    def add_layout(self, layout: QtWidgets.QLayout) -> None:
        self.layout.addLayout(layout)

    def add_stretch(self) -> None:
        self.layout.addStretch()

    def on_toggle(self, expanded: bool) -> None:
        """Recursively sets the visibility of items in the layout."""
        PySide6TK.QtWrappers.layout.set_layout_visibility(self.layout, expanded)
        self.setMaximumHeight(
            self.sizeHint().height() if expanded else self.fontMetrics().height() * 2
        )
        self.layout.invalidate()
        self.updateGeometry()
