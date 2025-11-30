from PySide6 import QtWidgets

from PySide6TK import QtWrappers


def new_file() -> None:
    print('New file created!')


def open_file() -> None:
    print('Open file dialog!')


def save_file() -> None:
    print('File saved!')


def show_help() -> None:
    print('Help documentation!')


class Example(QtWrappers.MainWindow):
    def __init__(self) -> None:
        super().__init__('Example Shortcut Window')
        self.resize(300, 200)

        self.shortcut_manager = QtWrappers.KeyShortcutManager(self)

        desc = 'Create a new file.'
        self.shortcut_manager.add_shortcut(
            'new_file', 'Ctrl+N', new_file, desc
        )

        desc = 'Open an existing file.'
        self.shortcut_manager.add_shortcut(
            'open_file', 'Ctrl+O', open_file, desc
        )

        desc = 'Save the current file.'
        self.shortcut_manager.add_shortcut(
            'save_file', 'Ctrl+S', save_file, desc
        )

        desc = 'Quit the application'
        self.shortcut_manager.add_shortcut(
            'quit_app', 'Ctrl+Q', self.close, desc
        )

        desc = 'Show help documentation.'
        self.shortcut_manager.add_shortcut(
            'show_help', 'F1', show_help, desc
        )

        self.btn_open_shortcuts = QtWidgets.QPushButton('Open Shortcuts')
        self.btn_open_shortcuts.clicked.connect(
            self.shortcut_manager.show_editor
        )

        self.setCentralWidget(self.btn_open_shortcuts)


if __name__ == '__main__':
    QtWrappers.exec_app(Example, 'ExampleShortcutWindow')
