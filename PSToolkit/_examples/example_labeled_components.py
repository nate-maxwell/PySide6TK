from PySide6 import QtWidgets

import PSToolkit.app
import PSToolkit.main_window
from PSToolkit.labeled_combobox import LabeledComboBox
from PSToolkit.labeled_line_edit import LabeledLineEdit
from PSToolkit.labeled_spinbox import LabeledSpinBox


class ExampleWindow(PSToolkit.main_window.MainWindow):
    def __init__(self) -> None:
        super().__init__('Example Labeled Components')
        self.widget_main = QtWidgets.QWidget()
        self.setCentralWidget(self.widget_main)
        self.layout_main = QtWidgets.QVBoxLayout()
        self.widget_main.setLayout(self.layout_main)
        self.setFixedWidth(300)

        items = ['alpha', 'bravo', 'charlie', 'echo']
        self.combo = LabeledComboBox('Combobox', items, True)

        self.line_edit = LabeledLineEdit('Line Edit')
        self.line_edit.set_placeholder_text("Don't read this.")

        self.spinbox_int = LabeledSpinBox('Spinbox Int')
        self.spinbox_int.set_value(41)
        self.spinbox_float = LabeledSpinBox('Spinbox Float', True)
        self.spinbox_float.set_value(21.4)

        self.layout_main.addWidget(self.combo)
        self.layout_main.addWidget(self.line_edit)
        self.layout_main.addWidget(self.spinbox_int)
        self.layout_main.addWidget(self.spinbox_float)


if __name__ == '__main__':
    PSToolkit.app.exec_app(ExampleWindow, 'ExampleLabeledComponents')
