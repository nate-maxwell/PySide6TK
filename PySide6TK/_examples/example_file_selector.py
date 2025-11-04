from PySide6TK import QtWrappers


class Foo(QtWrappers.MainWindow):
    def __init__(self) -> None:
        super().__init__('file selector')
        self.wid = QtWrappers.FileSelector('file')
        self.setCentralWidget(self.wid)


if __name__ == '__main__':
    QtWrappers.exec_app(Foo, 'ExampleFileSelector')
