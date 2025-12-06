from PySide6TK import QtWrappers


class ExampleFileTreeWidget(QtWrappers.MainWindow):
    def __init__(self) -> None:
        super().__init__('Example File Tree Widget.')

        self.file_tree = QtWrappers.FileTreeWidget(parent=self)
        self.file_tree.file_opened.connect(lambda path: print(f'Opening file: {path}'))
        self.file_tree.file_selected.connect(lambda path: print(f'Selected: {path}'))
        self.file_tree.directory_changed.connect(lambda path: print(f'Root changed to: {path}'))

        self.setCentralWidget(self.file_tree)
        self.setMinimumHeight(700)


if __name__ == '__main__':
    QtWrappers.exec_app(ExampleFileTreeWidget, 'ExampleFileTreeWidget')
