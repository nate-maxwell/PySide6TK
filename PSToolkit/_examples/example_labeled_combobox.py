from PSToolkit import app
from PSToolkit.main_window import MainWindow
from PSToolkit.labeled_combobox import LabeledComboBox


class Foo(MainWindow):
    def __init__(self) -> None:
        super().__init__('Combo Box')
        self.wid = LabeledComboBox('Option:', appendable=True)
        self.wid.add_items(['alpha', 'bravo', 'charlie', 'echo'])
        self.setFixedWidth(400)
        self.setCentralWidget(self.wid)


if __name__ == '__main__':
    app.exec_app(Foo, 'ExampleComboBox')
