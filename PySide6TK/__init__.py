from pathlib import Path
from typing import Optional
from typing import Union

from PySide6 import QtWidgets


MODULE_NAME = Path(__file__).parent.name

QT_COMMON_TYPE = Union[QtWidgets.QWidget, QtWidgets.QLayout]
OPTIONAL_COMMON_TYPE = Optional[QT_COMMON_TYPE]

MENU_TYPE = Union[QtWidgets.QMainWindow, QtWidgets.QWidget]

RESOURCES_PATH = Path(Path(__file__).parent, 'resources')
