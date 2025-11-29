"""
Example editor for python code that creates a table from dictionaries.

Also doubles as example showing help bar.
"""

import time

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

from PySide6TK import QtWrappers
from PySide6TK import dict_viewer


example_code = """import os
from typing import Union


values: list[dict[str, str]] = []

for i, (k, v) in enumerate(os.environ.items()):
    values.append({'key': k, 'value': v})


# As long as 'results' is given a list of dicts or dict value,
# the table will generate!
result: Union[list, dict] = values
"""


class ExamplePythonEditor(QtWrappers.MainWindow):
    def __init__(self) -> None:
        super().__init__(
            'Example Python Editor',
            (1200, 800),
            icon_path=QtWrappers.BUTTON_BLACK_40X40
        )
        self.sg = None
        self.toolbar = QtWrappers.HelpToolbar(
            parent=self,
            description='Example code editor with dict viewer',
            version='1.0.0',
            author='Nate Maxwell',
            repo_url='https://github.com/nate-maxwell/PySide6TK',
            documentation_url='https://github.com/nate-maxwell/PySide6TK',
            reload_modules=[
                dict_viewer
            ]
        )
        QtWrappers.set_style(self, QtWrappers.QSS_COMBINEAR)

        self._create_widgets()
        self._create_layout()
        self._create_connections()
        self.code_editor.setPlainText(example_code)

    def _create_widgets(self) -> None:
        # -----Main-----
        self.widget_main = QtWidgets.QWidget()
        self.layout_main = QtWidgets.QVBoxLayout()
        self.splitter_code = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)
        self.splitter_results = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)

        font = QtGui.QFont('Courier')
        font.setPointSize(10)

        # -----Code Editor-----
        self.grp_code = QtWrappers.GroupBox('Query Code:')

        self.hlayout_code_editor = QtWidgets.QHBoxLayout()
        self.code_editor = QtWrappers.CodeEditor()
        self.code_editor.setFont(font)
        self.code_editor.setMinimumHeight(150)
        self.code_editor.setPlaceholderText(example_code)
        self.minimap = QtWrappers.CodeMiniMap(self.code_editor)

        self.hlayout_query_button = QtWidgets.QHBoxLayout()
        self.btn_execute_query = QtWidgets.QPushButton(
            text='Run',
            icon=self.style().standardIcon(
                QtWidgets.QStyle.StandardPixmap.SP_MediaPlay
            )
        )

        # -----Message/Errors-----
        self.grp_traceback = QtWrappers.GroupBox('Messages / Errors:')

        self.traceback_display = QtWidgets.QTextEdit()
        self.traceback_display.setReadOnly(True)
        self.traceback_display.setPlaceholderText(
            'Error messages and tracebacks will appear here...'
        )
        self.traceback_display.setFont(font)
        self.traceback_display.setMinimumHeight(50)

        self.resource_monitor = QtWrappers.ResourceMonitor()

        # -----Results-----
        self.grp_result = QtWrappers.GroupBox('Results:')

        self.results_table = QtWidgets.QTableWidget()
        self.results_table.setMinimumHeight(200)
        self.results_table.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.Interactive
        )
        self.results_table.horizontalHeader().setStretchLastSection(True)

    def _create_layout(self) -> None:
        # -----Code Editor-----
        self.hlayout_code_editor.addWidget(self.code_editor)
        self.hlayout_code_editor.addWidget(self.minimap)

        self.hlayout_query_button.addStretch()
        self.hlayout_query_button.addWidget(self.btn_execute_query)

        self.grp_code.add_layout(self.hlayout_code_editor)
        self.grp_code.add_layout(self.hlayout_query_button)
        self.splitter_code.addWidget(self.grp_code)

        # -----Message/Errors-----
        self.grp_traceback.add_widget(self.traceback_display)
        self.grp_traceback.add_widget(QtWrappers.HorizontalLine())
        self.grp_traceback.add_widget(self.resource_monitor)
        self.splitter_code.addWidget(self.grp_traceback)
        self.splitter_code.setSizes([300, 50])

        # -----Results-----
        self.grp_result.add_widget(self.results_table)
        self.splitter_results.addWidget(self.grp_result)
        self.splitter_results.addWidget(self.splitter_code)

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
            before = time.perf_counter()
            exec(code, namespace)
            after = time.perf_counter()
            elapsed = after - before
            elapsed_str = f'Executed in {elapsed:.3f} seconds.'

            result = namespace.get('result')
            if result is None:
                self.traceback_display.setPlainText(
                    'Query executed successfully, but no "result" variable found.\n'
                    'Make sure to assign your query result to a variable named "result".\n'
                    f'\n{elapsed_str}'
                )
                return

            if isinstance(result, list):
                self.traceback_display.setPlainText(
                    f'Query executed successfully!\n'
                    f'Retrieved {len(result)} record(s).\n'
                    f'\n{elapsed_str}'
                )
                self.display_results(result)
            elif isinstance(result, dict):
                self.traceback_display.setPlainText(
                    'Query executed successfully!\n'
                    'Retrieved 1 record.\n'
                    f'\n{elapsed_str}'
                )
                self.display_results([result])
            else:
                self.traceback_display.setPlainText(
                    'Query executed successfully!\n'
                    f'Result type: {type(result).__name__}\n'
                    f'Result: {result}\n'
                    f'\n{elapsed_str}'
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
    QtWrappers.exec_app(ExamplePythonEditor, 'ExamplePythonEditor')


if __name__ == '__main__':
    main()
