from pathlib import Path

from PySide6TK import QtWrappers


_FRAMES_PATH = Path(Path(__file__).parent, 'frames')

# Doubles as the example for preview_image.
# Minimal example - Probably should expand to have FPS combo box ¯\_(ツ)_/¯


class ExampleWindow(QtWrappers.MainWindow):
    def __init__(self) -> None:
        super().__init__('Example Preview Sequence')
        self.wid = QtWrappers.PreviewSequence('Example Frames')
        self.wid.set_source(Path(_FRAMES_PATH))
        self.setCentralWidget(self.wid)


if __name__ == '__main__':
    QtWrappers.exec_app(ExampleWindow, 'ExampleSeqViewer')
