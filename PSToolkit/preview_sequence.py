"""
# Preview Sequence

* Descriptions

    A UI component class that holds an updatable preview image sequence and a
    label.
    Contains basic functionality for handling invalid paths.
"""


from PySide6 import QtWidgets

from PSToolkit.preview_image import PreviewImage


class PreviewSequence(PreviewImage):
    """Preview widget that can display a still image or animate an
        ImageSequence. Unlike PreviewImage, PreviewSequence contains a
        Play/Pause button and Stop button at the bottom.
        If label is not '', it will always be drawn at the top.

        Args:
            label: Optional caption shown above/below the image.
            size: Target display size (width, height) for the preview area.

        Notes:
            - Uses ImageSequence for both single-frame and multi-frame sources.
            - Connects to ImageSequence.frame_changed to update the pixmap live.
            - Make sure to call close() (or let Qt manage lifetime) so timers stop.
        """

    def __init__(self, label: str, size: tuple[int, int] | None = None) -> None:
        super().__init__(label, size, True)
        self._playing = False

        self.hlayout_buttons = QtWidgets.QHBoxLayout()
        self.btn_play = QtWidgets.QPushButton('Play')
        self.btn_play.clicked.connect(self.play)
        self.btn_stop = QtWidgets.QPushButton('Stop')
        self.btn_stop.clicked.connect(self.stop)

        self.hlayout_buttons.addWidget(self.btn_play)
        self.hlayout_buttons.addWidget(self.btn_stop)

    def play_seq(self) -> None:
        """Plays/Pauses the images sequence and flips the text on the play
        button.
        """
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
        self.reset()
