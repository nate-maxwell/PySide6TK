"""
# Labeled Spin Box

* Descriptions

    A UI component class that is a label and a spinbox. This is mostly
    for eliminating boilerplate for tools that have a labeled row that
    contains a spinbox.
"""

from typing import Union

from PySide6 import QtWidgets

from PySide6TK.enums import Orient


class LabeledSpinBox(QtWidgets.QWidget):
    """A composite widget combining a label and a numeric spin box.

    This class provides a labeled input field for numeric values, supporting
    both integer and floating-point modes. The label can be positioned either
    to the left of or above the spin box depending on layout orientation.
    Useful for parameter entry fields in tool panels or property editors.

    Example:
        >>> size_field = LabeledSpinBox('Size', double=True)
        >>> size_field.set_value(1.25)
        >>> print(size_field.value())

    Attributes:
        layout_main (QtWidgets.QLayout): The main layout managing the label
            and spin box widgets, set to ``QHBoxLayout`` or ``QVBoxLayout``
            depending on the ``vertical`` argument.
        label (QtWidgets.QLabel): The descriptive label displayed next to or
            above the spin box.
        spinbox (QtWidgets.QAbstractSpinBox): The numeric input field, either
            a ``QSpinBox`` for integers or a ``QDoubleSpinBox`` for floats.

    Args:
        text (str): The label text displayed beside or above the spin box.
        double (bool): If ``True``, uses a ``QDoubleSpinBox`` for floating-point
            input; otherwise, uses a ``QSpinBox`` for integer input.
            Defaults to ``False``.
        label_pos (PySide6TK.enums.Orient): Whether to put the label on
            ``Top``, ``Bottom``, ``Left``, or ``Right`` of the combobox.
            Defaults to ``Left``.
    """

    def __init__(self, text: str, double: bool = False,
                 label_pos: Orient = Orient.Left) -> None:
        super().__init__()

        if double:
            self.spinbox = QtWidgets.QDoubleSpinBox()
        else:
            self.spinbox = QtWidgets.QSpinBox()
        self.spinbox.setMaximum(2 ** 31 - 1)

        self.label = QtWidgets.QLabel(text)

        match label_pos:
            case Orient.Top:
                self.layout_main = QtWidgets.QVBoxLayout()
                self.layout_main.addWidget(self.label)
                self.layout_main.addWidget(self.spinbox)
            case Orient.Bottom:
                self.layout_main = QtWidgets.QVBoxLayout()
                self.layout_main.addWidget(self.spinbox)
                self.layout_main.addWidget(self.label)
            case Orient.Left:
                self.layout_main = QtWidgets.QHBoxLayout()
                self.layout_main.addWidget(self.label)
                self.layout_main.addWidget(self.spinbox)
            case Orient.Right:
                self.layout_main = QtWidgets.QHBoxLayout()
                self.layout_main.addWidget(self.spinbox)
                self.layout_main.addWidget(self.label)

        self.layout_main.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout_main)

    def set_value(self, v: Union[int, float]) -> None:
        self.spinbox.setValue(v)

    def value(self) -> Union[int, float]:
        return self.spinbox.value()

    def set_label_expanding(self, expand: bool) -> None:
        """Sets the label as expanding if True, and preferred if False."""
        if expand:
            policy = QtWidgets.QSizePolicy.Policy.Expanding
        else:
            policy = QtWidgets.QSizePolicy.Policy.Preferred
        self.label.setSizePolicy(policy, QtWidgets.QSizePolicy.Policy.Preferred)
