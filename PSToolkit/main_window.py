"""
# Main Window

* Descriptions

    Small wrapper for a Qt main window to eliminate writing the layout
    setting, saving a few lines...
"""


import ctypes
import platform
from pathlib import Path
from typing import Any
from typing import Optional
from typing import Union

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6.QtCore import QStandardPaths
from PySide6 import QtWidgets

import PSToolkit.gui


_optional_window = Optional[QtWidgets.QMainWindow]
_appdata_path = Path(QStandardPaths.writableLocation(
    QStandardPaths.StandardLocation.AppDataLocation))


def get_main_window_parent(widget: QtWidgets.QWidget) -> _optional_window:
    """
    Returns the QtWidgets.QMainWindow that contains a given widget.

    Args:
        widget(QtWidgets.QWidget): The widget to get the parent QMainWindow
         from.

    Returns:
        QtWidgets.QMainWindow: The owning QMainWindow currently holding the
         widget.
    """
    parent_widget = widget.parent()
    while parent_widget is not None:
        if isinstance(parent_widget, QtWidgets.QMainWindow):
            return parent_widget

        parent_widget = parent_widget.parent

    return None


def set_window_icon(window: QtWidgets.QMainWindow,
                    icon: Union[str, Path]) -> None:
    """
    Sets the window icon to the selected icon name from the icon folder.
    If the platform is windows, the tray icon is also set.

    Notes:
        - Must be called on Windows. No-ops elsewhere.
        - Ideally call this *before* creating/showing top-level windows.

    Args:
        window(QtWidgets.QMainWindow): Which window to set the icon for. This should
        be called within the window's constructor and should pass self through, although
        it can be called through some icon manager/function.

        icon(str): The name to the icon if it lives in the mythos.resources folder,
            or the path to it.
    """
    if type(icon) is str:
        icon_path = Path(PSToolkit.gui.ICONS_PATH, icon)
    else:
        icon_path = icon
    window.setWindowIcon(QtGui.QIcon(icon_path.as_posix()))

    if platform.system() == 'Windows':
        my_app_id = f'QtToolkit.MainWindow.{type(window).__name__}'
        # noinspection PyUnresolvedReferences
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(my_app_id)


def restore_window(window: QtWidgets.QMainWindow, settings: QtCore.QSettings) -> None:
    """Restore window geometry and state from QSettings.

    Args:
        window: The main window to restore.
        settings: The settings store to read from.
    """
    settings.beginGroup('main_window')
    geom_any = settings.value('geometry', None)
    state_any = settings.value('windowState', None)
    settings.endGroup()

    geom: QtCore.QByteArray = _as_bytearray(geom_any)
    state: QtCore.QByteArray = _as_bytearray(state_any)

    if not geom.isEmpty():
        window.restoreGeometry(geom)
    if not state.isEmpty():
        window.restoreState(state)


def _as_bytearray(value: Any) -> QtCore.QByteArray:
    """Coerce a settings value to QByteArray safely."""
    if isinstance(value, QtCore.QByteArray):
        return value
    if isinstance(value, (bytes, bytearray, memoryview)):
        return QtCore.QByteArray(bytes(value))
    return QtCore.QByteArray()


def save_window(window: QtWidgets.QMainWindow,
                settings: QtCore.QSettings) -> None:
    """Save window geometry and state to QSettings.

    Args:
        window: The main window to persist.
        settings: The settings store to write to.
    """
    settings.beginGroup('main_window')
    settings.setValue('geometry', window.saveGeometry())
    settings.setValue('windowState', window.saveState())
    settings.endGroup()
    settings.sync()


def _ensure_on_screen(window: QtWidgets.QWidget) -> None:
    """If the saved position is off-screen (e.g., monitor removed), move the
    window onscreen.
    """
    screen = QtWidgets.QApplication.primaryScreen()
    if not screen:
        return

    available = screen.availableGeometry()
    frame = window.frameGeometry()
    if not available.intersects(frame):
        size = frame.size()
        window.move(available.topLeft())
        window.resize(size)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, window_name: str, min_size: tuple[int, int],
                 max_size: tuple[int, int],
                 parent: Optional[QtWidgets.QWidget] = None) -> None:
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle(window_name)

        ini_name = window_name.replace(' ', '_')
        _settings_path: Path = Path(_appdata_path, f'QtToolkit/{ini_name}.ini')
        if not _settings_path.parent.exists():
            _settings_path.parent.mkdir(parents=True, exist_ok=True)

        self._settings: QtCore.QSettings = QtCore.QSettings(
            _settings_path.as_posix(),
            QtCore.QSettings.Format.IniFormat
        )

        if not min_size == (0, 0):
            self.resize(min_size[0], min_size[1])
            self.setMinimumSize(min_size[0], min_size[1])
        if not max_size == (0, 0):
            self.setMaximumSize(max_size[0], max_size[1])

        restore_window(self, self._settings)

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        """Persist on close."""
        save_window(self, self._settings)
        super().closeEvent(event)
