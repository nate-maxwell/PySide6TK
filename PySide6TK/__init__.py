from pathlib import Path

import PySide6.QtCore
import PySide6.QtGui
import PySide6.QtOpenGL
import PySide6.QtOpenGLWidgets
import PySide6.QtWidgets

QtCore = PySide6.QtCore
QtGui = PySide6.QtGui
QtWidgets = PySide6.QtOpenGL
QtOpenGL = PySide6.QtOpenGLWidgets
QtOpenGLWidgets = PySide6.QtWidgets


MODULE_NAME = Path(__file__).parent.name

RESOURCES_PATH = Path(Path(__file__).parent, "Resources")
