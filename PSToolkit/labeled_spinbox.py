"""
# Labeled Spin Box

* Descriptions

    A UI component class that is a label and a spinbox. This is mostly
    for eliminating boilerplate for tools that have a labeled row that
    contains a spinbox.
"""

from typing import Union

from PySide6 import QtWidgets


class LabeledSpinBox(QtWidgets.QWidget):
    def __init__(self, text: str, double: bool = False,
                 vertical: bool = False) -> None:
        super().__init__()
        if vertical:
            self.layout_main = QtWidgets.QVBoxLayout()
        else:
            self.layout_main = QtWidgets.QHBoxLayout()

        self.layout_main.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout_main)

        if double:
            self.spinbox = QtWidgets.QDoubleSpinBox()
        else:
            self.spinbox = QtWidgets.QSpinBox()

        self.label = QtWidgets.QLabel(text)
        self.layout_main.addWidget(self.label)
        self.layout_main.addWidget(self.spinbox)

    def set_value(self, v: Union[int, float]) -> None:
        self.spinbox.setValue(v)

    def value(self) -> Union[int, float]:
        return self.spinbox.value()
