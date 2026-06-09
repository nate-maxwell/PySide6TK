"""
# Scroll Area

* Descriptions

    Small wrapper for a Qt scroll area to eliminate writing the layout
    setting, saving a few lines.
"""


from PySide6 import QtWidgets


class ScrollArea(QtWidgets.QScrollArea):
    """A scrollable container widget supporting vertical or horizontal layout.

    This class wraps a standard ``QScrollArea`` and provides a simplified
    interface for building scrollable UI regions. The contained layout can be
    either vertical or horizontal, determined at construction. Widgets or
    layouts can then be appended using convenience methods.

    Example:
        >>> scroll = ScrollArea(horizontal=True)
        >>> scroll.add_widget(QtWidgets.QPushButton('Click Me'))
        >>> scroll.add_stretch()

    Attributes:
        widget_main (QtWidgets.QWidget): The main content widget that holds
            the scrollable layout.
        layout (QtWidgets.QLayout): The active layout for the scrollable area,
            either ``QVBoxLayout`` or ``QHBoxLayout`` depending on the
            constructor argument.

    Args:
        horizontal (bool): If ``True``, the layout will be horizontal
            (``QHBoxLayout``); otherwise, vertical (``QVBoxLayout``).
            Defaults to ``False``.
    """

    def __init__(self, horizontal: bool = False) -> None:
        super().__init__()
        self.setWidgetResizable(True)
        self.widget_main = QtWidgets.QWidget()
        self.widget_main.setContentsMargins(0, 0, 0, 0)
        self.setWidget(self.widget_main)
        if horizontal:
            self.layout = QtWidgets.QHBoxLayout()
        else:
            self.layout = QtWidgets.QVBoxLayout()
        self.widget_main.setLayout(self.layout)

    def add_widget(self, widget: QtWidgets.QWidget) -> None:
        self.layout.addWidget(widget)

    def add_layout(self, layout: QtWidgets.QLayout) -> None:
        self.layout.addLayout(layout)

    def add_stretch(self) -> None:
        self.layout.addStretch()
