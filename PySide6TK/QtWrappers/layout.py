"""
# Layout

* Descriptions

    Helpers for generic layout handling.
"""


import PySide6.QtWidgets as QtWidgets


def set_layout_visibility(layout: QtWidgets.QLayout, visible: bool) -> None:
    """Hide or show all children inside a layout.

    Args:
        layout (QtWidgets.QLayout): The layout whose contents to toggle.
        visible (bool): True to show, False to hide.
    """
    if layout is None:
        return

    for i in range(layout.count()):
        item = layout.itemAt(i)
        if item is None:
            continue

        widget = item.widget()
        if widget is not None:
            widget.setVisible(visible)
        else:
            child_layout = item.layout()
            if child_layout is not None:
                set_layout_visibility(child_layout, visible)


def clear_layout(layout: QtWidgets.QLayout) -> None:
    """Recursively empties a layout of its contents."""
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()
        elif item.layout() is not None:
            clear_layout(item.layout())


def remove_layout(layout: QtWidgets.QLayout) -> None:
    """Recursively empties and deletes a layout."""
    clear_layout(layout)
    layout.deleteLater()
