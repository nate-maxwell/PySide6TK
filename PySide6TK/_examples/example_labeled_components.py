from PySide6 import QtWidgets

from PySide6TK import QtWrappers


class ExampleWindow(QtWrappers.MainWindow):
    def __init__(self) -> None:
        super().__init__('Example Labeled Components')
        self.widget_main = QtWidgets.QWidget()
        self.setCentralWidget(self.widget_main)
        self.layout_main = QtWidgets.QVBoxLayout()
        self.widget_main.setLayout(self.layout_main)
        self.setFixedWidth(400)

        # -----Labeled---------------------------------------------------------
        self.group_labeled = QtWrappers.GroupBox('Labeled On Widget')

        items_dyn = ['alpha', 'bravo', 'charlie', 'echo']
        self.combo_dynamic = QtWrappers.LabeledComboBox('Dynamic Combobox', items_dyn, True)

        item_stc = ['1', '2', '3', '4', '5']
        self.combo_static = QtWrappers.LabeledComboBox('Static Combobox', item_stc)

        self.line_edit = QtWrappers.LabeledLineEdit('Line Edit')
        self.line_edit.set_placeholder_text("Don't read this.")

        self.spinbox_int = QtWrappers.LabeledSpinBox('Spinbox Int')
        self.spinbox_int.set_value(41)
        self.spinbox_float = QtWrappers.LabeledSpinBox('Spinbox Float', True)
        self.spinbox_float.set_value(21.4)

        # -----Unlabeled-------------------------------------------------------
        self.group_unlabeled = QtWrappers.GroupBox('Unlabeled Widget, Labels in GridLayout')

        items_dyn = ['alpha', 'bravo', 'charlie', 'echo']
        self.un_combo_dynamic = QtWrappers.LabeledComboBox('', items_dyn, True)

        item_stc = ['1', '2', '3', '4', '5']
        self.un_combo_static = QtWrappers.LabeledComboBox('', item_stc)

        self.un_line_edit = QtWrappers.LabeledLineEdit('')
        self.un_line_edit.set_placeholder_text("Don't read this.")

        self.un_spinbox_int = QtWrappers.LabeledSpinBox('')
        self.un_spinbox_int.set_value(41)
        self.un_spinbox_float = QtWrappers.LabeledSpinBox('', True)
        self.un_spinbox_float.set_value(21.4)

        self.grid_layout = QtWrappers.GridLayout()
        self.grid_layout.add_to_last_row(QtWidgets.QLabel('Dynamic Combobox'))
        self.grid_layout.add_to_last_row(self.un_combo_dynamic)
        self.grid_layout.add_to_new_row(QtWidgets.QLabel('Static Combobox'))
        self.grid_layout.add_to_last_row(self.un_combo_static)
        self.grid_layout.add_to_new_row(QtWidgets.QLabel('Line Edit'))
        self.grid_layout.add_to_last_row(self.un_line_edit)
        self.grid_layout.add_to_new_row(QtWidgets.QLabel('Spinbox Int'))
        self.grid_layout.add_to_last_row(self.un_spinbox_int)
        self.grid_layout.add_to_new_row(QtWidgets.QLabel('Spinbox Float'))
        self.grid_layout.add_to_last_row(self.un_spinbox_float)

        # -----Layout----------------------------------------------------------

        self.group_labeled.add_widget(self.combo_dynamic)
        self.group_labeled.add_widget(self.combo_static)
        self.group_labeled.add_widget(self.line_edit)
        self.group_labeled.add_widget(self.spinbox_int)
        self.group_labeled.add_widget(self.spinbox_float)
        self.layout_main.addWidget(self.group_labeled)

        self.group_unlabeled.add_layout(self.grid_layout)
        self.layout_main.addWidget(self.group_unlabeled)


if __name__ == '__main__':
    QtWrappers.exec_app(ExampleWindow, 'ExampleLabeledComponents')
