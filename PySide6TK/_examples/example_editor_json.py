"""
Example editor for python code that creates a dict viewer from JSON code.

Also doubles as example showing help bar.
"""

import json

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

import PySide6TK.dict_viewer
import PySide6TK.main_window
from PySide6TK import QtWrappers

example_code = """{
    "parameters": {
        "address": "0.0.0.0",
        "port": 8080,
        "verbosity": 2,
        "log-output": 0,
        "print-tree": true,
        "xform-timeout": "45s",
        "consolidate": true,
        "security-tokens": [
            "lockheed",
            "martin"
        ]
    },
    "routes": [
        {
            "name": "default",
            "channels": [
                {
                    "name": "inmem",
                    "strategy": "pub-sub",
                    "transformers": [
                        { "address": "127.0.0.1:7010" },
                        { "address": "10.0.0.52:8008" }
                    ],
                    "subscribers": [
                        { "address": "127.0.0.1:1234" },
                        { "address": "16.70.18.1:9999" }
                    ]
                }
            ]
        }
    ]
}

"""


class JsonEditor(QtWrappers.MainWindow):
    def __init__(self) -> None:
        super().__init__('Json Editor', (450, 750))
        self.toolbar = QtWrappers.HelpToolbar(
            parent=self,
            description='Example code editor with dict viewer for viewing json',
            version='1.0.0',
            author='Nate Maxwell',
            repo_url='https://github.com/nate-maxwell/PySide6TK',
            documentation_url='https://github.com/nate-maxwell/PySide6TK',
            reload_modules=[
                PySide6TK.dict_viewer
            ]
        )

        self._create_widgets()
        self._create_layout()
        self._create_connections()

    def _create_widgets(self) -> None:
        self.widget_main = QtWidgets.QWidget()
        self.layout_main = QtWidgets.QVBoxLayout()

        font = QtGui.QFont('Courier')
        font.setPointSize(10)

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)

        self.sa_output = QtWrappers.ScrollArea()
        self.dict_viewer = QtWrappers.DictViewer('Output', {})

        self.vlayout_code = QtWidgets.QVBoxLayout()

        self.hlayout_editor = QtWidgets.QHBoxLayout()
        self.editor = QtWrappers.CodeEditor(QtWrappers.JsonHighlighter)
        self.editor.setFont(font)
        self.editor.setPlainText(example_code)
        self.minimap = QtWrappers.CodeMiniMapWidget(self.editor)

        self.btn_run = QtWidgets.QPushButton(
            text='Run',
            icon=self.style().standardIcon(
                QtWidgets.QStyle.StandardPixmap.SP_MediaPlay)
        )

    def _create_layout(self) -> None:
        self.sa_output.add_widget(self.dict_viewer)
        self.sa_output.add_stretch()
        self.splitter.addWidget(self.sa_output)

        self.hlayout_editor.addWidget(self.editor)
        self.hlayout_editor.addWidget(self.minimap)

        self.vlayout_code.addLayout(self.hlayout_editor)
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.btn_run)
        self.vlayout_code.addLayout(button_layout)
        wid = QtWidgets.QWidget()
        wid.setLayout(self.vlayout_code)
        self.splitter.addWidget(wid)

        self.setCentralWidget(self.widget_main)
        self.widget_main.setLayout(self.layout_main)
        self.layout_main.addWidget(self.splitter)

    def _create_connections(self) -> None:
        self.btn_run.clicked.connect(self.refresh)

    def refresh(self) -> None:
        self.dict_viewer.data = json.loads(self.editor.toPlainText())
        self.dict_viewer.refresh()


if __name__ == '__main__':
    QtWrappers.exec_app(JsonEditor, 'JsonEditor')
