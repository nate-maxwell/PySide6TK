
from PySide6 import QtWidgets

from PySide6TK import QtWrappers


class ExampleWindow(QtWrappers.MainWindow):
    def __init__(self) -> None:
        super().__init__('Example Grid Layout')
        self.grid_layout = QtWrappers.GridLayout()
        self.widget_main = QtWidgets.QWidget()
        self.widget_main.setLayout(self.grid_layout)
        self.setCentralWidget(self.widget_main)
        self.setMinimumWidth(300)

        # Have you ever been 14 rows deep in a grid layout while manually
        # inserting row indexes, and you suddenly have to insert something
        # after row 5?
        # You think to yourself "I should probably do this with a dict + loop
        # next time, but this time I'm committed".
        # Yet somehow you find yourself in the same circle of hell again...

        self.grid_layout.add_to_new_row(QtWidgets.QLabel('First Name:'))
        self.grid_layout.add_to_last_row(QtWidgets.QLabel('Thomas'))

        self.grid_layout.add_to_new_row(QtWidgets.QLabel('Last Name:'))
        self.grid_layout.add_to_last_row(QtWidgets.QLabel('Anderson'))

        self.grid_layout.add_to_new_row(QtWidgets.QLabel('Alias:'))
        self.grid_layout.add_to_last_row(QtWidgets.QLabel('Neo'))


if __name__ == '__main__':
    QtWrappers.exec_app(ExampleWindow, 'ExampleGridLayout')
