from PySide6 import QtWidgets

from PySide6TK import QtWrappers
from PySide6TK import Core


class ExampleWindow(QtWrappers.MainWindow):
    def __init__(self) -> None:
        super().__init__("Example Labeled Components")
        self.widget_main = QtWidgets.QWidget()
        self.setCentralWidget(self.widget_main)
        self.layout_main = QtWidgets.QVBoxLayout()
        self.widget_main.setLayout(self.layout_main)
        self.setFixedWidth(400)

        self._create_widgets()
        self._create_layout()

    def _create_widgets(self) -> None:
        # -----Labeled---------------------------------------------------------
        self.group_labeled = QtWrappers.GroupBox("Labeled On Widget")

        items_dyn = ["alpha", "bravo", "charlie", "echo"]
        self.combo_dynamic = QtWrappers.LabeledComboBox(
            "Dynamic Combobox", items_dyn, True
        )

        item_stc = ["1", "2", "3", "4", "5"]
        self.combo_static = QtWrappers.LabeledComboBox("Static Combobox", item_stc)

        self.line_edit = QtWrappers.LabeledLineEdit("Line Edit")
        self.line_edit.set_placeholder_text("Don't read this.")

        self.spinbox_int = QtWrappers.LabeledSpinBox("Spinbox Int")
        self.spinbox_int.set_value(41)
        self.spinbox_float = QtWrappers.LabeledSpinBox("Spinbox Float", True)
        self.spinbox_float.set_value(21.4)

        # -----Unlabeled-------------------------------------------------------
        self.group_unlabeled = QtWrappers.GroupBox(
            "Unlabeled Widget, Labels in GridLayout"
        )

        items_dyn = ["alpha", "bravo", "charlie", "echo"]
        self.un_combo_dynamic = QtWrappers.LabeledComboBox("", items_dyn, True)

        item_stc = ["1", "2", "3", "4", "5"]
        self.un_combo_static = QtWrappers.LabeledComboBox("", item_stc)

        self.un_line_edit = QtWrappers.LabeledLineEdit("")
        self.un_line_edit.set_placeholder_text("Don't read this.")

        self.un_spinbox_int = QtWrappers.LabeledSpinBox("")
        self.un_spinbox_int.set_value(41)
        self.un_spinbox_float = QtWrappers.LabeledSpinBox("", True)
        self.un_spinbox_float.set_value(21.4)

        self.grid_layout = QtWrappers.GridLayout()

        # -----Directions------------------------------------------------------
        self.group_positions = QtWrappers.GroupBox("Label Positions")
        self.spinbox_top = QtWrappers.LabeledSpinBox("Top", label_pos=Core.Orient.Top)
        self.spinbox_bot = QtWrappers.LabeledSpinBox(
            "Right", label_pos=Core.Orient.Right
        )
        self.spinbox_lft = QtWrappers.LabeledSpinBox(
            "Bottom", label_pos=Core.Orient.Bottom
        )
        self.spinbox_rgt = QtWrappers.LabeledSpinBox("Left", label_pos=Core.Orient.Left)

    def _create_layout(self) -> None:
        # -----Labeled---------------------------------------------------------
        self.group_labeled.add_widget(self.combo_dynamic)
        self.group_labeled.add_widget(QtWrappers.HorizontalLine())
        self.group_labeled.add_widget(self.combo_static)
        self.group_labeled.add_widget(QtWrappers.HorizontalLine())
        self.group_labeled.add_widget(self.line_edit)
        self.group_labeled.add_widget(QtWrappers.HorizontalLine())
        self.group_labeled.add_widget(self.spinbox_int)
        self.group_labeled.add_widget(QtWrappers.HorizontalLine())
        self.group_labeled.add_widget(self.spinbox_float)
        self.layout_main.addWidget(self.group_labeled)

        # -----Unlabeled-------------------------------------------------------
        self.grid_layout.add_to_last_row(QtWidgets.QLabel("Dynamic Combobox"))
        self.grid_layout.add_to_last_row(self.un_combo_dynamic)
        self.grid_layout.add_to_new_row(QtWidgets.QLabel("Static Combobox"))
        self.grid_layout.add_to_last_row(self.un_combo_static)
        self.grid_layout.add_to_new_row(QtWidgets.QLabel("Line Edit"))
        self.grid_layout.add_to_last_row(self.un_line_edit)
        self.grid_layout.add_to_new_row(QtWidgets.QLabel("Spinbox Int"))
        self.grid_layout.add_to_last_row(self.un_spinbox_int)
        self.grid_layout.add_to_new_row(QtWidgets.QLabel("Spinbox Float"))
        self.grid_layout.add_to_last_row(self.un_spinbox_float)

        # -----Directions------------------------------------------------------
        self.group_positions.add_widget(self.spinbox_top)
        self.group_positions.add_widget(self.spinbox_bot)
        self.group_positions.add_widget(self.spinbox_lft)
        self.group_positions.add_widget(self.spinbox_rgt)

        # -----Main------------------------------------------------------------
        self.group_unlabeled.add_layout(self.grid_layout)
        self.layout_main.addWidget(self.group_unlabeled)
        self.layout_main.addWidget(self.group_positions)


if __name__ == "__main__":
    QtWrappers.exec_app(ExampleWindow, "ExampleLabeledComponents")
