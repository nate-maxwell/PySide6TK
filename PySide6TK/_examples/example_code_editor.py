from pathlib import Path

from PySide6TK import QtWrappers


class ExampleEditor(QtWrappers.MainWindow):
    def __init__(self) -> None:
        super().__init__('Example Editor')
        self.editor = QtWrappers.CodeEditor()
        self.setCentralWidget(self.editor)

        with Path(__file__).open('r') as f:
            text = f.read()
            self.editor.setPlainText(text)


if __name__ == '__main__':
    QtWrappers.exec_app(ExampleEditor, 'ExampleEditor')
