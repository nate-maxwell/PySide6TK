"""
# Image sequence handler.

* Description:

    Loops through icons from a directory over a timer.
    Can create a QPixmap or QIcon from frames.

* Notes:

    You will need a closeEvent or equivalent to stop the image sequence,
    otherwise it will endlessly loop.
"""


import os
from pathlib import Path
from typing import Optional

from PySide6 import QtGui
from PySide6 import QtCore

import QtToolkit.regx


class ImageSequence(QtCore.QObject):
    """
    Loops through icons from a directory over a timer.
    Can create a QPixmap or QIcon from frames.

    Notes:
        You will need a closeEvent or equivalent to stop the image sequence,
        otherwise it will endlessly loop.
    """
    DEFAULT_FPS = 24
    frame_changed = QtCore.Signal(int)

    def __init__(self, path: Optional[Path], *args) -> None:
        QtCore.QObject.__init__(self, *args)

        self._fps = self.DEFAULT_FPS

        self._timer = QtCore.QTimer(self.parent())
        self._timer.setSingleShot(False)
        self._timer.timeout.connect(self._frame_changed)\

        self._frame = 0
        self._frames = []
        self._directory = None
        self._paused = False

        if path:
            self.set_path(path)

    @property
    def first_frame(self) -> Path:
        """
        Get the path to the first frame.

        Returns:
            Path: The path to the first frame.
        """
        if self._frames:
            return self._frames[0]
        return Path('/does/not/exist')

    def set_path(self, path: Path):
        """
        Set a single frame or a directory to an image sequence.

        Args:
            path(Path): The path to a single frame.
        """
        if path.is_file():
            self._frame = 0
            self._frames = [path]
        elif path.is_dir():
            self.set_dirname(path)

    def set_dirname(self, directory: Path):
        """
        Set the location to the image sequence.

        Args:
            directory(Path): The directory to grab frames from.
        """
        self._directory = directory
        if directory.is_dir():
            self._frames = [Path(directory, filename).as_posix() for filename in os.listdir(directory)]
            QtToolkit.regx.natural_sort_strings(self._frames)

    @property
    def dirname(self) -> Path:
        """
        Return the location to the image sequence.

        Returns:
            Path: The current tracked directory.
        """
        return self._directory

    def reset(self):
        """Stop and reset the current frame to 0."""
        if not self._paused:
            self._frame = 0
        self._timer.stop()

    def pause(self):
        """ImageSequence will enter Paused state."""
        self._paused = True
        self._timer.stop()

    def resume(self):
        """ImageSequence will enter Playing state."""
        if self._paused:
            self._paused = False
            self._timer.start()

    def stop(self):
        """Stops the movie. ImageSequence enters NotRunning state."""
        self._timer.stop()

    def start(self):
        """Starts the movie. ImageSequence will enter Running state."""
        self.reset()
        self._timer.start(int(1000.0 / self._fps))

    @property
    def frames(self):
        """Return all the filenames in the image sequence."""
        return self._frames

    def _frame_changed(self):
        """Triggered when the current frame changes."""
        if not self._frames:
            return

        frame = self._frame
        frame += 1
        self.jump_to_frame(frame)

    @property
    def percent(self):
        """Return the current frame position as a percentage."""
        if len(self._frames) == self._frame + 1:
            _percent = 1
        else:
            _percent = float((len(self._frames) + self._frame)) / len(self._frames) - 1
        return _percent

    @property
    def frame_count(self) -> int:
        """
        Return the number of frames.

        Returns:
            int: the number of current tracked frames
        """
        return len(self._frames)

    @property
    def current_icon(self) -> QtGui.QIcon:
        """
        Returns the current frame as a QIcon.

        Return:
            QtGui.QIcon: The created QIcon of the current frame.
        """
        return QtGui.QIcon(self.current_filename.as_posix())

    @property
    def current_pixmap(self) -> QtGui.QPixmap:
        """
        Return the current frame as a QPixmap.

        Return:
            QtGui.QPixmap: The created QPixmap of the current frame.
        """
        return QtGui.QPixmap(self.current_filename)

    @property
    def current_filename(self) -> Path:
        """
        Return the current file name.

        Returns:
            Path: The current frame's path.
        """
        try:
            return self._frames[self.current_frame_number]
        except IndexError:
            return Path('does/not/exist')

    @property
    def current_frame_number(self) -> Optional[int]:
        """
        Return the current frame.

        Returns:
            Optional[int]: The current frame number.
        """
        return self._frame

    def jump_to_frame(self, frame_num: int):
        """Set the current frame."""
        if frame_num >= self.frame_count:
            frame_num = 0
        self._frame = frame_num
        self.frame_changed.emit(frame_num)
