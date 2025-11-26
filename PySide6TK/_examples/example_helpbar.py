"""
# Help Bar

* Description:

    An auto-generated toolbar to add to the top of tools.
"""


from PySide6 import QtWidgets

from PySide6TK import QtWrappers


class TestWindow(QtWrappers.MainWindow):
    def __init__(self) -> None:
        super().__init__('Style Library Viewer',
                         (0, 500), (0, 0))

        self.widget_main = QtWidgets.QWidget()
        self.layout_main = QtWidgets.QVBoxLayout()
        self.setCentralWidget(self.widget_main)
        self.widget_main.setLayout(self.layout_main)

        self.toolbar = QtWrappers.HelpToolbar(
            parent=self,
            description='An auto-generated toolbar to add to the top of tools.',
            version='1.0.0',
            author='Nate Maxwell',
            repo_url='https://github.com/nate-maxwell/PySide6TK',
            documentation_url='https://github.com/nate-maxwell/PySide6TK'
        )


if __name__ == '__main__':
    QtWrappers.exec_app(TestWindow, 'TestToolbar')
