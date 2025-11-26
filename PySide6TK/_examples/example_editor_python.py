from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

from PySide6TK import QtWrappers


example_code = """import os
from typing import Union


values: list[dict[str, str]] = []

for i, (k, v) in enumerate(os.environ.items()):
    values.append({'key': k, 'value': v})


# As long as 'results' is given a list of dicts or dict value,
# the table will generate!
result: Union[list, dict] = values
"""


class DictionaryViewer(QtWrappers.MainWindow):
    def __init__(self) -> None:
        super().__init__('Dictionary Viewer', (1200, 800))
        self.sg = None

        self._create_widgets()
        self._create_layout()
        self._create_connections()
        self.code_editor.setPlainText(example_code)

    def _create_widgets(self) -> None:
        self.widget_main = QtWidgets.QWidget()
        self.layout_main = QtWidgets.QVBoxLayout()
        self.splitter_code = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)
        self.splitter_results = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)

        font = QtGui.QFont('Courier')
        font.setPointSize(10)

        # -----Code Editor-----
        self.code_widget = QtWidgets.QWidget()
        self.code_layout = QtWidgets.QVBoxLayout()
        self.code_label = QtWidgets.QLabel('Query Code:')
        self.code_label.setStyleSheet('font-weight: bold; font-size: 12px;')

        self.code_editor = QtWrappers.CodeEditor()
        self.code_editor.setFont(font)
        self.code_editor.setMinimumHeight(150)
        self.code_editor.setPlaceholderText(example_code)

        # -----Message/Errors-----
        self.traceback_widget = QtWidgets.QWidget()
        self.traceback_layout = QtWidgets.QVBoxLayout()
        self.traceback_label = QtWidgets.QLabel('Messages / Errors:')
        self.traceback_label.setStyleSheet('font-weight: bold; font-size: 12px;')

        self.traceback_display = QtWidgets.QTextEdit()
        self.traceback_display.setReadOnly(True)
        self.traceback_display.setPlaceholderText(
            'Error messages and tracebacks will appear here...'
        )
        self.traceback_display.setFont(font)
        self.traceback_display.setMinimumHeight(50)

        # -----Results-----
        self.results_widget = QtWidgets.QWidget()
        self.results_layout = QtWidgets.QVBoxLayout()
        self.results_label = QtWidgets.QLabel('Results:')
        self.results_label.setStyleSheet('font-weight: bold; font-size: 12px;')

        self.results_table = QtWidgets.QTableWidget()
        self.results_table.setMinimumHeight(200)
        self.results_table.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.Interactive
        )
        self.results_table.horizontalHeader().setStretchLastSection(True)

        self.btn_execute_query = QtWidgets.QPushButton(
            text='Run',
            icon=self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MediaPlay)
        )

    def _create_layout(self) -> None:
        # -----Code Editor-----
        self.code_widget.setLayout(self.code_layout)
        self.code_layout.addWidget(self.code_label)
        self.code_layout.addWidget(self.code_editor)
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.btn_execute_query)
        self.code_layout.addLayout(button_layout)
        self.splitter_code.addWidget(self.code_widget)

        # -----Message/Errors-----
        self.traceback_widget.setLayout(self.traceback_layout)
        self.traceback_layout.addWidget(self.traceback_label)
        self.traceback_layout.addWidget(self.traceback_display)
        self.splitter_code.addWidget(self.traceback_widget)

        # -----Results-----
        self.results_widget.setLayout(self.results_layout)
        self.results_layout.addWidget(self.results_label)
        self.results_layout.addWidget(self.results_table)
        self.splitter_results.addWidget(self.results_widget)
        self.splitter_results.addWidget(self.splitter_code)

        self.splitter_code.setSizes([300, 50])

        # -----Main-----
        self.setCentralWidget(self.widget_main)
        self.widget_main.setLayout(self.layout_main)
        self.layout_main.addWidget(self.splitter_results)

    def _create_connections(self) -> None:
        self.btn_execute_query.clicked.connect(self.btn_execute_query_connection)

    def btn_execute_query_connection(self) -> None:
        self.traceback_display.clear()
        self.results_table.clear()
        self.results_table.setRowCount(0)
        self.results_table.setColumnCount(0)

        code = self.code_editor.toPlainText()

        if not code.strip():
            self.traceback_display.setPlainText('Error: No code to execute.')
            return

        try:
            namespace = {'sg': self.sg, 'result': None}
            exec(code, namespace)
            result = namespace.get('result')
            if result is None:
                self.traceback_display.setPlainText(
                    'Query executed successfully, but no "result" variable found.\n'
                    'Make sure to assign your query result to a variable named "result".'
                )
                return

            if isinstance(result, list):
                self.traceback_display.setPlainText(
                    f'Query executed successfully!\n'
                    f'Retrieved {len(result)} record(s).'
                )
                self.display_results(result)
            elif isinstance(result, dict):
                self.traceback_display.setPlainText(
                    'Query executed successfully!\n'
                    'Retrieved 1 record.'
                )
                self.display_results([result])
            else:
                self.traceback_display.setPlainText(
                    'Query executed successfully!\n'
                    f'Result type: {type(result).__name__}\n'
                    f'Result: {result}'
                )

        except Exception as e:
            self.traceback_display.setPlainText(
                f'Error executing query:\n\n{e}'
            )

    def display_results(self, results: list = None) -> None:
        if not results:
            self.results_table.setRowCount(0)
            self.results_table.setColumnCount(0)
            return

        all_keys = set()
        for i in results:
            if isinstance(i, dict):
                all_keys.update(i.keys())

        all_keys = sorted(list(all_keys))

        self.results_table.setRowCount(len(results))
        self.results_table.setColumnCount(len(all_keys))
        self.results_table.setHorizontalHeaderLabels(all_keys)

        for row, item in enumerate(results):
            if isinstance(item, dict):
                for col, key in enumerate(all_keys):
                    value = item.get(key, '')
                    display_value = str(value) if value is not None else ''
                    table_item = QtWidgets.QTableWidgetItem(display_value)
                    self.results_table.setItem(row, col, table_item)

        self.results_table.resizeColumnsToContents()


def main() -> None:
    QtWrappers.exec_app(DictionaryViewer, 'DictionaryViewer')


if __name__ == '__main__':
    main()
