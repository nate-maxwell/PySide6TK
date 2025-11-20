"""
# Column Based Browser

* Description:

    A Qt browser utilizing the SearchableList widget to create a MacOS-like
    browser.
"""


from typing import Optional

from PySide6 import QtWidgets

from PySide6TK.main_window import MainWindow
from PySide6TK.searchable_list import SearchableList


class ColumnBrowser(MainWindow):
    """
    A column based selection manager for file browsers. This is a QMainWindow
    widget that can be extended to build any layout needed, or inserted into
    another widget.

    Args:
        window_name(str): The name of the window, displayed on the top window bar.

        min_size(tuple[int]): Vec2 list for the min x and y size of the window.
            Setting this to (0, 0) will not set the minimum size.

        max_size(tuple[int]): Vec2 list for the max x and y size of the window.
            Setting this to (0, 0) will not set the maximum size.

        column_labels(list[str]): List of column names if static, or the
            starting column name.

        parent (Optional[QtWidgets.QWidget]): Defaults to None.

    Attributes:
        hlayout_columns(QHBoxLayout):
            The horizontal layout that holds the

        tokens(dict{int: str}):
            A dictionary containing the indexes of each
            column, left to right in hlayout_columns, and the selected item
            in the column. Will read '' until item is selected.

        columns(list):
            The list of _CBList classes currently under the hlayout_columns

    Methods:
        column_action(index: int):
        This method should be overwritten in derived classes to call
        a function based on the received index: int, item: str.

        clear_columns_right_of(index: int):
            Clears the items from all columns to the right of the given index.

        add_column_to_right(index: int):
            Adds a column to the right of the given index.

        remove_columns_to_right_of(index: int):
            Removes and deletes columns + items to the right of the given index.
    """

    def __init__(self, window_name: str, min_size: tuple[int, int], max_size: tuple[int, int], column_labels: list[str],
                 parent: Optional[QtWidgets.QWidget] = None):
        super(ColumnBrowser, self).__init__(window_name, parent=parent)

        self.column_labels = column_labels

        self.window_name = window_name
        self.setWindowTitle(self.window_name)

        self.resize(min_size[0], min_size[1])
        if not min_size == (0, 0):
            self.setMinimumSize(min_size[0], min_size[1])
        if not max_size == (0, 0):
            self.setMaximumSize(max_size[0], max_size[1])

        self.tokens: dict[int, str] = {}
        self.columns: list[SearchableList] = []
        self.hlayout_columns = QtWidgets.QHBoxLayout()
        self.hlayout_columns.setContentsMargins(0, 0, 0, 0)

        for label in self.column_labels:
            self.add_column_to_right(label)
            self.tokens[self.column_labels.index(label)] = ''

    def column_listener(self, index: int, item: str):
        """_CBList children will call this on parent to update self.tokens and trigger self.column_action"""
        self.tokens[index] = item
        self.column_action(index)

    def column_action(self, index: int):
        """
        This method should be overwritten in derived classes to call
        a function based on the received index: int, item: str.
        """
        pass

    def clear_columns_right_of(self, index: int):
        """Empties the _CBList of items if they are after the given index in self.columns."""
        for column in self.columns:
            if self.columns.index(column) > index:
                column.clear_list()
                self.tokens[self.columns.index(column)] = ''

    def add_column_to_right(self, column_label: str):
        """Adds an _CBList to the right side of the list horizontal box layout."""
        index = len(self.columns)
        self.tokens[index] = ''
        self.columns.append(_CBList(self, column_label, index))
        self.hlayout_columns.addWidget(self.columns[-1])

    def remove_columns_to_right_of(self, index: int):
        """Removes all _CBList to the right of the specified index in self.columns."""
        if len(self.columns) > 1:
            self.columns = self.columns[:index + 1]

            for child in self.hlayout_columns.children():
                if child not in self.columns:
                    self.hlayout_columns.removeItem(child)

            keys = list(self.tokens)
            for k in keys:
                if keys.index(k) > index:
                    self.tokens.pop(k)

    def get_selected_by_column_label(self, label: str) -> Optional[str]:
        """
        Gets the selected item of the column with the given label.

        Args:
            label(str): The label to match the columns by.

        Returns:
            str: The selected value of the found column. Returns None
            if no column was found.
        """
        for i in self.columns:
            if i.column_label == label:
                return i.selected_item()
        else:
            return None


class _CBList(SearchableList):
    """
    A component class representing a list of items to populate ColumnBrowser.
    This is primarily intended for file/asset/folder listing within the
    directory structure.

    Args:
        column_browser(ColumnBrowser):
        A ref to the parent widget that instantiated the _CBList.

        column_label(str):
        Name of the column, displayed above the column.

        index(int):
        An index, or int id, number for ColumnBrowser class to
        keep track of each instantiated _CBList.

    Methods:
        item_selected(item):
        The connection to selecting an item from the QListWidget.
        This will send info back to the ColumnBrowser through
        _column_listener().
    """

    def __init__(self, column_browser: ColumnBrowser, column_label: str, index: int):
        super().__init__(column_label)
        self.index = index
        self.column_browser = column_browser
        self.list_column.itemClicked.connect(self.item_selected)

    def item_selected(self, item):
        """Sends information back to MythosBrowser class."""
        if type(item) is int:
            return
        self.column_browser.column_listener(self.index, item.text())
