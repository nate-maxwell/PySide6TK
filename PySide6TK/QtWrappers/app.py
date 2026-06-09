"""
# Application

* Description

    PySide application helpers.
"""

import ctypes
import platform
import sys
from pathlib import Path
from typing import Callable
from typing import Optional
from typing import Type

from PySide6 import QtCore
from PySide6 import QtWidgets

AA_EnableHighDpiScaling = QtCore.Qt.ApplicationAttribute.AA_EnableHighDpiScaling
AA_UseHighDpiPixmaps = QtCore.Qt.ApplicationAttribute.AA_UseHighDpiPixmaps


def set_windows_app_user_model_id(app_id: str) -> None:
    """Set Windows AppUserModelID (improves taskbar grouping & jump list).
    No-op on non-Windows.

    Args:
        app_id (str): e.g. 'Vendor.Product.SubProduct.Version'
    """
    if platform.system() != 'Windows':
        return

    call_name = 'set_windows_app_user_model_id'
    fn_name = 'SetCurrentProcessExplicitAppUserModelID'

    try:
        shell32 = ctypes.windll.shell32
        fn = getattr(shell32, fn_name, None)
        if fn is None:
            return
        fn.argtypes = [ctypes.c_wchar_p]
        fn.restype = ctypes.HRESULT
        fn(app_id)

    except OSError as err:
        print(f'[{call_name}] OSError calling {fn_name}: {err!r}')

    except ValueError as err:
        print(f'[{call_name}] ValueError setting AppUserModelID: {err!r}')

    except Exception as err:
        print(f'[{call_name}] Unexpected error: {type(err).__name__}: {err!r}')


def single_instance_lock(name: str) -> QtCore.QLockFile:
    """Create a cross-platform single-instance lock based on QLockFile.

    Args:
        name: Stable app name used in the lock filename.

    Returns:
        A QLockFile that is already locked (raises RuntimeError if taken).
    """
    lock_dir = Path(QtCore.QStandardPaths.writableLocation(
        QtCore.QStandardPaths.StandardLocation.TempLocation
    ))
    lock_path = lock_dir / f'{name}.lock'
    lock = QtCore.QLockFile(lock_path.as_posix())
    lock.setStaleLockTime(0)
    if not lock.tryLock(0):
        raise RuntimeError(f'Another instance already running (lock: {lock_path}).')
    return lock


def init_application(org: str, app_name: str,
                     enable_highdpi: bool = True,
                     app_id_windows: Optional[str] = None,
                     ) -> QtWidgets.QApplication:
    """Create QApplication with sensible defaults.

    Args:
        org (str): Organization name (used by QSettings).
        app_name (str): Application name (used by QSettings, paths).
        enable_highdpi (bool): Enable Qt High-DPI attributes. Defaults to True.
        app_id_windows (Optional[str]): Optional Windows AppUserModelID.

    Returns:
        QtWidgets.QApplication: A constructed QApplication (not executed).
    """
    if enable_highdpi:
        QtCore.QCoreApplication.setAttribute(AA_EnableHighDpiScaling, True)
        QtCore.QCoreApplication.setAttribute(AA_UseHighDpiPixmaps, True)

    QtCore.QCoreApplication.setOrganizationName(org)
    QtCore.QCoreApplication.setApplicationName(app_name)

    if app_id_windows:
        set_windows_app_user_model_id(app_id_windows)

    app = QtWidgets.QApplication(sys.argv)
    return app


def exec_single_instance_app(
    window_factory: Callable[[], QtWidgets.QMainWindow],
    org: str = 'MyOrg',
    app_name: str = 'MyApp',
    app_id_windows: Optional[str] = None,
    lock_name: Optional[str] = None
) -> int:
    """Create, guard, and run a single-instance GUI with restore/save and style.

    Args:
        window_factory (Callable): Callable that returns a constructed
            QMainWindow.
        org (str): Organization name.
        app_name (str): Application name.
        app_id_windows (Optional[str]): Optional Windows AppUserModelID string.
        lock_name (Optional[str]): Name for single-instance lock (defaults to
            app_name).

    Returns:
        int: The process exit code.
    """
    app = init_application(org=org, app_name=app_name, app_id_windows=app_id_windows)

    # Single-instance lock
    try:
        lock = single_instance_lock(lock_name or app_name)
    except RuntimeError:
        info = 'Another instance already running.'
        QtWidgets.QMessageBox.information(None, app_name, info)
        return 0

    win = window_factory()
    win.show()

    code = app.exec()

    # Release lock
    if lock:
        lock.unlock()

    return code


def exec_app(window_cls: Type[QtWidgets.QMainWindow], app_name: str) -> int:
    """Run a QApplication for a given main window (basic).

    Args:
        window_cls (Type[QtWidgets.QMainWindow]): The main window class type to
            start an application with.
        app_name (str): The name of the application.
    """
    app = init_application('MyOrg', app_name)
    win = window_cls()
    win.show()
    return app.exec()
