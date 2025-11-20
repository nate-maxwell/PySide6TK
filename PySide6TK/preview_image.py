"""
# Preview Image

* Descriptions

    A UI component class that holds an updatable preview image and a label.
    Contains basic functionality for handling invalid paths.
"""

from pathlib import Path
from typing import Union

import PySide6.QtCore as QtCore
import PySide6.QtGui as QtGui
import PySide6.QtWidgets as QtWidgets

import PySide6TK.icons
from PySide6TK.image_sequence import ImageSequence


class PreviewImage(QtWidgets.QWidget):
    """Preview widget that can display a still image or animate an
    ImageSequence.

    Args:
        label: Optional caption shown above/below the image.
        size: Target display size (width, height) for the preview area.
        label_top: If True, label is placed above the image; otherwise below.

    Notes:
        - Uses ImageSequence for both single-frame and multi-frame sources.
        - Connects to ImageSequence.frame_changed to update the pixmap live.
        - Make sure to call close() (or let Qt manage lifetime) so timers stop.
    """

    def __init__(self, label: str, size: tuple[int, int] | None = None,
                 label_top: bool = True) -> None:
        super().__init__()

        self._size = (200, 200) if size is None else size
        self.sequence: Union[ImageSequence, None] = None
        self._default_image_path: Path = Path(PySide6TK.icons.ICON_NO_PREVIEW_384X384)

        self._layout = QtWidgets.QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self._label = QtWidgets.QLabel(label)
        self._label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self._image = QtWidgets.QLabel()
        self._image.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        if label_top:
            if label:
                self._layout.addWidget(self._label)
            self._layout.addWidget(self._image)
        else:
            self._layout.addWidget(self._image)
            if label:
                self._layout.addWidget(self._label)

        self._set_pixmap(self._pixmap_from_path(self._default_image_path))

    # ----------Public API-----------------------------------------------------

    def set_source(self, path: Path | str | None) -> None:
        """Set the preview source to a file or directory.

        If 'path' is a file -> treated as single-frame sequence.
        If 'path' is a directory -> treated as multi-frame sequence.
        If 'path' is None or invalid -> shows default image.
        """
        self._disconnect_sequence()

        p = Path(path) if path is not None else None
        if not p or not p.exists():
            self._set_pixmap(self._pixmap_from_path(self._default_image_path))
            return

        self.sequence = ImageSequence(p, self)
        self.sequence.frame_changed.connect(self._on_frame_changed)
        self._on_frame_changed(self.sequence.current_frame_number or 0)

    def play(self) -> None:
        """Begin playback."""
        if not self.sequence:
            return
        self.sequence.start()

    def pause(self) -> None:
        """Pause playback (frame remains)."""
        if self.sequence and getattr(self.sequence, '_timer', None):
            self.sequence.pause()

    def resume(self) -> None:
        """Resume playback if paused."""
        if self.sequence and getattr(self.sequence, '_timer', None):
            self.sequence.resume()

    def stop(self) -> None:
        """Stop playback (frame index preserved by ImageSequence unless reset)."""
        if self.sequence and getattr(self.sequence, '_timer', None):
            self.sequence.stop()

    def reset(self) -> None:
        """Stop (if running) and reset to frame 0; updates preview."""
        if not self.sequence:
            return
        self.sequence.reset()
        self._on_frame_changed(self.sequence.current_frame_number or 0)

    # ----------Overrides / Internals------------------------------------------

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        """Ensure background timers are stopped before the widget closes."""
        try:
            self.stop()
        finally:
            super().closeEvent(event)

    def _on_frame_changed(self, _frame_index: int) -> None:
        """Slot for ImageSequence.frame_changed: update pixmap with scaling."""
        if not self.sequence:
            return

        pix: QtGui.QPixmap = self.sequence.current_pixmap
        self._set_pixmap(pix)

    def _set_pixmap(self, pixmap: QtGui.QPixmap) -> None:
        """Scale and set pixmap into the label."""
        if pixmap.isNull():
            pixmap = self._pixmap_from_path(self._default_image_path)

        scaled = pixmap.scaled(
            self._size[0],
            self._size[1],
            QtCore.Qt.AspectRatioMode.KeepAspectRatio,
            QtCore.Qt.TransformationMode.SmoothTransformation,
        )
        self._image.setPixmap(scaled)

    @staticmethod
    def _pixmap_from_path(path: Path) -> QtGui.QPixmap:
        return QtGui.QPixmap(path.as_posix())

    def _disconnect_sequence(self) -> None:
        """Detach old sequence and stop any timers safely."""
        if self.sequence is None:
            return

        try:
            if getattr(self.sequence, '_timer', None):
                self.sequence.stop()
        except (RuntimeError, AttributeError) as err:
            print(f'[PreviewImage] Warning: failed to stop ImageSequence timer: {err!r}')

        try:
            self.sequence.frame_changed.disconnect(self._on_frame_changed)
        except (TypeError, RuntimeError) as err:
            print(f'[PreviewImage] Warning: failed to disconnect frame_changed: {err!r}')

        self.sequence = None
