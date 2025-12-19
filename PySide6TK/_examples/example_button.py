from pathlib import Path

from PySide6 import QtWidgets
from PySide6TK import QtWrappers


_FRAMES_PATH = Path(Path(__file__).parent, 'frames')


class ExampleWindow(QtWrappers.MainWindow):
    def __init__(self) -> None:
        super().__init__('Example Buttons Window')

        self.wid = QtWidgets.QWidget()
        self.layout = QtWrappers.GridLayout()
        self.wid.setLayout(self.layout)
        self.setCentralWidget(self.wid)

        self.layout.add_to_new_row(
            self.make_button(Path(_FRAMES_PATH, 'frame_001.png'))
        )
        self.layout.add_to_last_row(
            self.make_button(Path(_FRAMES_PATH, 'frame_002.png'))
        )
        self.layout.add_to_last_row(
            self.make_button(Path(_FRAMES_PATH, 'frame_003.png'))
        )
        self.layout.add_to_new_row(
            self.make_button(Path(_FRAMES_PATH, 'frame_004.png'))
        )
        self.layout.add_to_last_row(
            self.make_button(Path(_FRAMES_PATH, 'frame_005.png'))
        )

    @staticmethod
    def make_button(image_path: Path) -> QtWidgets.QPushButton:
        button = QtWrappers.ImageButton(image_path)
        button.setFixedSize(100, 100)
        button.clicked.connect(lambda: print(image_path.as_posix()))
        return button


if __name__ == '__main__':
    QtWrappers.exec_app(ExampleWindow, 'ExampleWindow')
