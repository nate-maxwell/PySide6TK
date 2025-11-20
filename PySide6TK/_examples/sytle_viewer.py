"""
# Stylesheet Viewer

* Description:

    A UI theme and color viewer with example widgets.
"""


from pathlib import Path

from PySide6 import QtCore
from PySide6 import QtWidgets

from PySide6TK import QtWrappers


_styles = QtWrappers.STYLE_PATH.glob('*')
_sheets = [i.name for i in _styles]


class ExampleWidget(QtWidgets.QWidget):
    """A widget filled with example items for theme and color testing."""
    def __init__(self) -> None:
        super().__init__()
        self._create_widgets()
        self._create_layout()

    def _create_widgets(self) -> None:
        self.layout_main = QtWidgets.QHBoxLayout()

        self.sl_items = QtWrappers.SearchableList('Style Library')
        self.sl_items.populate_column(_sheets)
        self.sl_items.item_selected = self._on_item_selected

        self.cmb_example = QtWidgets.QComboBox()
        self.cmb_example.addItems(['One', 'Two', 'Three'])

        self.le_example = QtWidgets.QLineEdit()
        self.le_example.setPlaceholderText("Line Edit")

        self.sbx_example = QtWidgets.QSpinBox()
        self.fsbx_example = QtWidgets.QDoubleSpinBox()
        self.cbx_example = QtWidgets.QCheckBox('Check Box')
        self.rdo_example = QtWidgets.QRadioButton('Radio Button')
        self.btn_example = QtWidgets.QPushButton('Push Button')
        self.btn_example.setFixedWidth(200)
        self.dial_example = QtWidgets.QDial()
        self.slider_example = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.slider_example.setValue(50)
        self.grp_example = QtWrappers.GroupBox('Group Box')

    def _create_layout(self) -> None:
        self.setLayout(self.layout_main)

        self.grp_example.add_widget(QtWidgets.QLabel('Combo Box'))
        self.grp_example.add_widget(self.cmb_example)
        self.grp_example.add_widget(QtWrappers.HorizontalLine())
        self.grp_example.add_widget(self.le_example)
        self.grp_example.add_widget(QtWrappers.HorizontalLine())
        self.grp_example.add_widget(QtWidgets.QLabel('Spin Box'))
        self.grp_example.add_widget(self.sbx_example)
        self.grp_example.add_widget(QtWrappers.HorizontalLine())
        self.grp_example.add_widget(QtWidgets.QLabel('Double Spin Box'))
        self.grp_example.add_widget(self.fsbx_example)
        self.grp_example.add_widget(QtWrappers.HorizontalLine())
        self.grp_example.add_widget(self.cbx_example)
        self.grp_example.add_widget(self.rdo_example)
        self.grp_example.add_widget(QtWrappers.HorizontalLine())
        self.grp_example.add_widget(self.btn_example)
        self.grp_example.add_widget(QtWrappers.HorizontalLine())
        self.grp_example.add_widget(QtWidgets.QLabel('Dial'))
        self.grp_example.add_widget(self.dial_example)
        self.grp_example.add_widget(QtWrappers.HorizontalLine())
        self.grp_example.add_widget(QtWidgets.QLabel('Slider'))
        self.grp_example.add_widget(self.slider_example)
        self.grp_example.add_stretch()

        self.layout_main.addWidget(self.sl_items)
        self.layout_main.addWidget(self.grp_example)

    def _on_item_selected(self) -> None:
        p = Path(QtWrappers.STYLE_PATH, f'{self.sl_items.selected_item()}')
        if self.sl_items.selected_items is None or not p.exists():
            return

        QtWrappers.set_style(self, p)


class StyleViewer(QtWrappers.MainWindow):
    def __init__(self) -> None:
        super().__init__('Style Library Viewer',
                         (0, 0), (0, 0))
        self.setCentralWidget(ExampleWidget())
        self.setFixedWidth(600)


if __name__ == '__main__':
    QtWrappers.exec_app(StyleViewer, 'StyleViewer')
