from pathlib import Path

import PySide6.QtCore
import PySide6.QtGui
import PySide6.QtOpenGL
import PySide6.QtOpenGLWidgets
import PySide6.QtWidgets

QtCore = PySide6.QtCore
QtGui = PySide6.QtGui
QtWidgets = PySide6.QtWidgets
QtOpenGL = PySide6.QtOpenGL
QtOpenGLWidgets = PySide6.QtOpenGLWidgets


MODULE_NAME = Path(__file__).parent.name

RESOURCES_PATH = Path(Path(__file__).parent, "Resources")
