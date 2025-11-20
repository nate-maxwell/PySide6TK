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


class HorizontalSpacer(QtWidgets.QWidget):
    def __init__(self, width: int) -> None:
        super().__init__()
        self.setFixedWidth(width)
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Preferred)


class VerticalSpacer(QtWidgets.QWidget):
    def __init__(self, height: int) -> None:
        super().__init__()
        self.setFixedHeight(height)
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
