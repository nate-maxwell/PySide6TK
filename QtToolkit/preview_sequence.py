"""
# Preview Sequence

* Descriptions

    A UI component class that holds an updatable preview image sequence and a
    label.
    Contains basic functionality for handling invalid paths.
"""


from PySide6 import QtWidgets

from QtToolkit.preview_image import PreviewImage


class PreviewSequence(PreviewImage):
    def __init__(self, label: str, size: tuple[int, int] | None = None,
                 label_top: bool = True) -> None:
        super().__init__(label, size, label_top)
        self._playing = False

        self.hlayout_buttons = QtWidgets.QHBoxLayout()
        self.btn_play = QtWidgets.QPushButton('Play')
        self.btn_play.clicked.connect(self.play)
        self.btn_stop = QtWidgets.QPushButton('Stop')
        self.btn_stop.clicked.connect(self.stop)

        self.hlayout_buttons.addWidget(self.btn_play)
        self.hlayout_buttons.addWidget(self.btn_stop)

    def play_seq(self) -> None:
        if self._playing:
            self.pause()
            self.btn_play.setText('Play')
        else:
            self.play()
            self.btn_play.setText('Pause')

        self._playing = not self._playing

    def stop_seq(self) -> None:
        self._playing = False
        self.stop()
