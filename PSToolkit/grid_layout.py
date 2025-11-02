"""
# Grid Layout

* Descriptions

    Small wrapper for a Qt grid layout to eliminate writing the layout
    setting, providing helpers for last row/column interactions, and saving a
    few lines.
"""

from PySide6 import QtWidgets

import PSToolkit


class GridLayout(QtWidgets.QGridLayout):
    """Grid layout with convenience functions for adding to latest columns and
    rows.
    """

    def __init__(self) -> None:
        super().__init__()

    def get_last_occupied_row(self) -> int:
        """Gets the integer row number of the last occupied row in the grid
         layout.

        Returns:
            int: The last occupied row number. If there are no occupied rows,
             -1 is returned instead.
        """
        last_row = -1
        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                if self.itemAtPosition(row, col):
                    last_row = max(last_row, row)

        return last_row

    def get_last_occupied_column(self, row: int) -> int:
        """Gets the integer column number of the last occupied column in the
        given row number in the grid layout.

        Args:
            row(int): Which row to get the last occupied column from.
        Returns:
            int: The last occupied column of the given row from the grid
             layout. If there are no occupied rows, -1 is returned instead.
        """
        last_column = -1
        for col in range(self.columnCount()):
            if self.itemAtPosition(row, col):
                last_column = col

        return last_column

    def add_to_new_row(self, item: PSToolkit.QT_COMMON_TYPE) -> None:
        """Adds item to a new row in the given layout.

        Args:
            item(Union[QtWidgets.QWidget, QtWidgets.QLayout]): The widget or
             layout to add.
        """
        last_row = self.get_last_occupied_row()
        next_row = 0 if last_row == -1 else last_row + 1

        if isinstance(item, QtWidgets.QWidget):
            self.addWidget(item, next_row, 0)
        elif isinstance(item, QtWidgets.QLayout):
            self.addLayout(item, next_row, 0)
        else:
            raise ValueError('item is not a layout or widget!')

    def add_to_last_row(self, item: PSToolkit.QT_COMMON_TYPE) -> None:
        """Adds item to a new column of the last occupied row of the given
         layout.

        Args:
            item(Union[QtWidgets.QWidget, QtWidgets.QLayout]): The widget or
             layout to add.
        """
        last_row = self.get_last_occupied_row()
        last_row = 0 if last_row == -1 else last_row
        last_column = self.get_last_occupied_column(last_row)
        next_column = 0 if last_column == -1 else last_column + 1

        if isinstance(item, QtWidgets.QWidget):
            self.addWidget(item, last_row, next_column)
        elif isinstance(item, QtWidgets.QLayout):
            self.addLayout(item, last_row, next_column)
        else:
            raise ValueError('item is not a layout or widget!')
