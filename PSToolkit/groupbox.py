"""
# Group Box

* Descriptions

    Small wrapper for a Qt group box to eliminate writing the layout
    setting, saving a few lines.
"""


from PySide6 import QtWidgets

import PSToolkit.layout


class GroupBox(QtWidgets.QGroupBox):
    def __init__(self, label: str = '', collapsable: bool = False,
                 horizontal: bool = False) -> None:
        super().__init__(label)
        if horizontal:
            self.layout = QtWidgets.QHBoxLayout()
        else:
            self.layout = QtWidgets.QVBoxLayout()

        if collapsable:
            self.setCheckable(True)
            self.setChecked(True)
            self.toggled.connect(self.on_toggle)

        self.setLayout(self.layout)

    def add_widget(self, widget: QtWidgets.QWidget) -> None:
        self.layout.addWidget(widget)

    def add_layout(self, layout: QtWidgets.QLayout) -> None:
        self.layout.addLayout(layout)

    def add_stretch(self) -> None:
        self.layout.addStretch()

    def on_toggle(self, checked: bool) -> None:
        PSToolkit.layout.set_layout_visible(self.layout, checked)
