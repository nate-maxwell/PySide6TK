from PySide6 import QtGui

from PySide6TK import QtWrappers


def on_color_changed(color: QtGui.QColor) -> None:
    print(f'Color changed to: {color.name()}')


class ExampleColorPicker(QtWrappers.MainWindow):
    def __init__(self) -> None:
        super().__init__('Example Color Picker')
        self.picker = QtWrappers.ColorPickerPanel(self)
        self.setCentralWidget(self.picker)
        self.picker.colorChanged.connect(on_color_changed)


if __name__ == '__main__':
    QtWrappers.exec_app(ExampleColorPicker, 'ExampleColorPicker')
