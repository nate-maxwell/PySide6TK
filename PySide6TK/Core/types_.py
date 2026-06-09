from typing import Optional
from typing import Union

from PySide6 import QtWidgets


QT_COMMON_TYPE = Union[QtWidgets.QWidget, QtWidgets.QLayout]
OPTIONAL_COMMON_TYPE = Optional[QT_COMMON_TYPE]
