"""
# Qt Basic Shapes

* Description:

    Basic shape library to eliminate boilerplate.
"""


from PySide6 import QtWidgets


class HorizontalLine(QtWidgets.QFrame):
    def __init__(self, sunken: bool = True) -> None:
        super().__init__()
        self.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        if sunken:
            self.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)


class VerticalLine(QtWidgets.QFrame):
    def __init__(self, sunken: bool = True) -> None:
        super().__init__()
        self.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        if sunken:
            self.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
