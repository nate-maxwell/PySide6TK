"""
An example file browser using PySide6TK.column_browser.ColumnBrowser
-
Toggle STATIC and run this file to see examples, found at bottom.
"""


import os
from pathlib import Path

from PySide6 import QtWidgets

import PySide6TK.app
from PySide6TK.column_browser import ColumnBrowser


def list_folder_contents(path: Path) -> list[str]:
    return [p.name for p in path.glob('*')]


class ExampleStaticBrowser(ColumnBrowser):
    def __init__(self):
        super().__init__('Example Static Browser', (950, 550), (950, 550), ['first', 'second', 'third', 'fourth'])

        # Default values
        self.default_path = Path('K:/')

        self.columns[0].populate_column(list_folder_contents(self.default_path))

        self._create_widgets()
        self._create_layout()
        self.setCentralWidget(self.main_widget)

    def _create_widgets(self):
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_widget = QtWidgets.QWidget()

    def _create_layout(self):
        # Add self.hlayout_columns
        self.main_layout.addLayout(self.hlayout_columns)
        self.main_widget.setLayout(self.main_layout)

    def column_action(self, index: int):
        # This could also be an if/elif chain for unique functions.
        # First column
        if index == 0:
            self.clear_columns_right_of(0)
            self.fill_column_at_index(1)

        # Last column
        elif index == len(self.column_labels):
            pass

        # Middle columns
        else:
            self.fill_column_at_index(index + 1)

    def fill_column_at_index(self, index: int):
        if '.' not in self.tokens[index - 1]:
            self.clear_columns_right_of(index - 1)
            path = self.default_path
            for i in range(index + 1):
                path = Path(path, self.tokens.get(i))

            if os.path.exists(path):
                self.columns[index].populate_column(list_folder_contents(path))


class ExampleDynamicBrowser(ColumnBrowser):
    def __init__(self):
        super().__init__('Example Dynamic Browser', (950, 550), (950, 950), ['shows'])

        # Default values
        self.default_path = Path('K:/')

        self.columns[0].populate_column(list_folder_contents(self.default_path))

        self._create_widgets()
        self._create_layout()
        self.setCentralWidget(self.main_widget)

    def _create_widgets(self):
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_widget = QtWidgets.QWidget()

    def _create_layout(self):
        self.main_layout.addLayout(self.hlayout_columns)
        self.main_widget.setLayout(self.main_layout)

    def column_action(self, index: int):
        if not '.' in self.tokens[index]:
            self.remove_columns_to_right_of(index)
            self.add_column_to_right(self.tokens[index])
            self.fill_column_at_index(len(self.columns) - 1)
        else:
            pass

    def fill_column_at_index(self, index: int):
        self.clear_columns_right_of(index - 1)
        path = self.default_path
        for i in range(index + 1):
            path = Path(path, self.tokens.get(i))

        if os.path.exists(path):
            self.columns[index].populate_column(list_folder_contents(path))


if __name__ == '__main__':
    STATIC = True

    if STATIC:
        browser_window = ExampleStaticBrowser
    else:
        browser_window = ExampleDynamicBrowser

    PySide6TK.app.exec_app(browser_window, 'ExampleColumnBrowser')
