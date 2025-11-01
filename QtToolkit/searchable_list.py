"""
# Searchable Scrollable List

* Descriptions

    A UI component class responsible for handling lists of strings. This
    includes a scroll box and a search box at the top for filtering by
    sub-strings.
"""


from typing import Optional

from PySide6 import QtCore
from PySide6 import QtWidgets


class SearchableList(QtWidgets.QWidget):
    """
    A component class representing a list of items.
    This is primarily intended for file/asset/folder listing within the Mythos
    pipeline directory structure.

    `Args`:
        column_label(str):
        Name of the column, displayed above the column.

        index(int):
        An index, or int id, number to
        keep track of each instantiated SearchableList.
        Defaults to 0.

        multi_select(bool):
        Whether the user can select more than one item at a time
        in the list widget.

    `Methods`:
        populate_column(contents: list):
        Populates the column from a list of items.

        clear_list:
        Clears the items from the QListWidget component.
    """
    def __init__(self, column_label: str, index: int = 0, multi_select: bool = False):
        super().__init__()
        self.column_label = column_label
        self.index = index

        self.layout_main = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout_main)
        self.layout_main.setContentsMargins(0, 0, 0, 0)

        self.le_search = QtWidgets.QLineEdit()
        self.le_search.setPlaceholderText('Search')
        self.list_column = QtWidgets.QListWidget()
        if multi_select:
            self.list_column.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.lbl_column = QtWidgets.QLabel(column_label)
        self.lbl_column.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.contents: list

        self.layout_main.addWidget(self.lbl_column)
        self.layout_main.addWidget(self.le_search)
        self.layout_main.addWidget(self.list_column)

        self.list_column.currentRowChanged.connect(self.item_selected)
        self.le_search.textChanged.connect(self._search_list)

    def populate_column(self, contents: list):
        """Adds a list of items to the QListWidget."""
        self.contents = contents
        self.list_column.clear()
        if contents:
            self.list_column.addItems(contents)

    def trigger_search_list(self):
        """Refines the search based on input substring."""
        # This is a separate func from self._search_list so that it provides some
        # code context when it is called.
        self._search_list()

    def _search_list(self):
        """
        Refines the items to the input text of self.le_search. Uses self.contents,
        set in self.populate_column(), to retain original items.
        """
        filtered_list = []
        self.clear_list()
        if len(self.le_search.text()) != 0:
            for item in self.contents:
                if self.le_search.text().upper() in item.upper():
                    filtered_list.append(item)
        else:
            filtered_list = self.contents

        self.list_column.addItems(filtered_list)

    @property
    def selected_item(self) -> Optional[str]:
        if self.list_column.currentItem():
            return self.list_column.currentItem().text()
        else:
            return None

    @property
    def selected_items(self) -> Optional[list[str]]:
        temp = []
        if self.list_column.currentItem():
            for i in self.list_column.selectedItems():
                temp.append(i.text())
            return temp
        else:
            return None

    def clear_list(self):
        self.list_column.clear()

    def set_selected(self, value: str):
        for i in range(self.list_column.count()):
            item = self.list_column.item(i)
            if item.text() == value:
                self.list_column.setCurrentItem(item)
                break

    def item_selected(self):
        """
        A function connected to the on click event of an item in the
        QListWidget.
        This can be overridden in manager/parent classes to conveniently
        connect method calls to item selection.
        """
