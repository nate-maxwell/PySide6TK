"""
!! Remember to run PySide6TK._generate_namespace.py to create this regenerate
this file before pushing updates!!

# QtWrappers

* Description:

    A similar namespace to PySide6 allowing more natural usage along the
    PySide6 framework.

    Example:
        >>> from PySide6TK import QtWrappers
        >>>
        >>> class Foo(QtWrappers.MainWindow):
        >>>     ...
"""


from PySide6TK.app import exec_app
from PySide6TK.app import exec_single_instance_app
from PySide6TK.app import init_application
from PySide6TK.app import set_windows_app_user_model_id
from PySide6TK.app import single_instance_lock
from PySide6TK.code_editor import CodeEditor
from PySide6TK.code_minimap import CodeMiniMap
from PySide6TK.color import ColorPickerPanel
from PySide6TK.color import RectangularColorPicker
from PySide6TK.column_browser import ColumnBrowser
from PySide6TK.dialogs import MultiLineTextDialog
from PySide6TK.dialogs import SingleLineTextDialog
from PySide6TK.dict_viewer import DictViewer
from PySide6TK.enums import Orient
from PySide6TK.file_selector import FileSelector
from PySide6TK.grid_layout import GridLayout
from PySide6TK.groupbox import GroupBox
from PySide6TK.helpbar import HelpToolbar
from PySide6TK.icons import BUTTON_BLACK_40X40
from PySide6TK.icons import BUTTON_BLUE_40X40
from PySide6TK.icons import BUTTON_BLUE_80X40
from PySide6TK.icons import BUTTON_CYAN_40X40
from PySide6TK.icons import BUTTON_FLAT_BLACK_200X40
from PySide6TK.icons import BUTTON_GREEN_40X40
from PySide6TK.icons import BUTTON_ORANGE_40X40
from PySide6TK.icons import BUTTON_PURPLE_40X40
from PySide6TK.icons import BUTTON_RED_40X40
from PySide6TK.icons import BUTTON_YELLOW_40X40
from PySide6TK.icons import ICON_AFTER_EFFECTS_400X400
from PySide6TK.icons import ICON_BLENDER_400X400
from PySide6TK.icons import ICON_IMG_NOT_FOUND_400X400
from PySide6TK.icons import ICON_MAYA_400X400
from PySide6TK.icons import ICON_NO_PREVIEW_384X384
from PySide6TK.icons import ICON_NUKE_400X400
from PySide6TK.icons import ICON_PHOTOSHOP_400X400
from PySide6TK.icons import ICON_SUBSTANCE_PAINTER_400X400
from PySide6TK.icons import ICON_UNREAL_400X400
from PySide6TK.icons import ICONS_PATH
from PySide6TK.image_sequence import ImageSequence
from PySide6TK.labeled_combobox import LabeledComboBox
from PySide6TK.labeled_line_edit import LabeledLineEdit
from PySide6TK.labeled_spinbox import LabeledSpinBox
from PySide6TK.languages.json_syntax import JsonHighlighter
from PySide6TK.languages.json_syntax import JsonSyntaxColors
from PySide6TK.languages.python_syntax import PythonHighlighter
from PySide6TK.languages.python_syntax import PythonSyntaxColors
from PySide6TK.layout import clear_layout
from PySide6TK.layout import remove_layout
from PySide6TK.layout import set_layout_visibility
from PySide6TK.main_window import get_main_window_parent
from PySide6TK.main_window import MainWindow
from PySide6TK.main_window import restore_window
from PySide6TK.main_window import save_window
from PySide6TK.main_window import set_window_icon
from PySide6TK.preview_image import PreviewImage
from PySide6TK.preview_sequence import PreviewSequence
from PySide6TK.regx import natural_sort_strings
from PySide6TK.regx import validation_no_special_chars
from PySide6TK.resource_monitor import filetime_to_int
from PySide6TK.resource_monitor import get_memory_usage
from PySide6TK.resource_monitor import ResourceMonitor
from PySide6TK.scroll_area import ScrollArea
from PySide6TK.searchable_list import SearchableList
from PySide6TK.shapes import HorizontalLine
from PySide6TK.shapes import HorizontalSpacer
from PySide6TK.shapes import VerticalLine
from PySide6TK.shapes import VerticalSpacer
from PySide6TK.signal import emit_signal
from PySide6TK.signal import signal
from PySide6TK.styles import QSS_ADAPTIC
from PySide6TK.styles import QSS_CHATBEE
from PySide6TK.styles import QSS_CLIENTOR
from PySide6TK.styles import QSS_CLOCKER
from PySide6TK.styles import QSS_COMBINEAR
from PySide6TK.styles import QSS_CSTARTPAGE
from PySide6TK.styles import QSS_DARKEUM
from PySide6TK.styles import QSS_DARKORANGE
from PySide6TK.styles import QSS_DEEPBOX
from PySide6TK.styles import QSS_DEVSION
from PySide6TK.styles import QSS_DIFFNES
from PySide6TK.styles import QSS_DIPLAYTAP
from PySide6TK.styles import QSS_DTOR
from PySide6TK.styles import QSS_EASYCODE
from PySide6TK.styles import QSS_ECLIPPY
from PySide6TK.styles import QSS_EXCELOFFICE
from PySide6TK.styles import QSS_FIBERS
from PySide6TK.styles import QSS_FIBRARY
from PySide6TK.styles import QSS_FILMOVIO
from PySide6TK.styles import QSS_GENETIVE
from PySide6TK.styles import QSS_GEOO
from PySide6TK.styles import QSS_GRAVIRA
from PySide6TK.styles import QSS_HACKBOOK
from PySide6TK.styles import QSS_HOOKMARK
from PySide6TK.styles import QSS_INCRYPT
from PySide6TK.styles import QSS_INTEGRID
from PySide6TK.styles import QSS_IRRORATER
from PySide6TK.styles import QSS_LICENSE
from PySide6TK.styles import QSS_MAILSY
from PySide6TK.styles import QSS_MEDIZE
from PySide6TK.styles import QSS_MIXCHAT
from PySide6TK.styles import QSS_MYWATCH
from PySide6TK.styles import QSS_OBIT
from PySide6TK.styles import QSS_PERSTFIC
from PySide6TK.styles import QSS_PHOTOXO
from PySide6TK.styles import QSS_PICPAX
from PySide6TK.styles import QSS_REMOVER
from PySide6TK.styles import QSS_SCALCULA
from PySide6TK.styles import QSS_SPYBOT
from PySide6TK.styles import QSS_SYNET
from PySide6TK.styles import QSS_TAKEZO
from PySide6TK.styles import QSS_TCOBRA
from PySide6TK.styles import QSS_TOOLERY
from PySide6TK.styles import QSS_VISUALSCRIPT
from PySide6TK.styles import QSS_WEBMAS
from PySide6TK.styles import QSS_WORDOFFICE
from PySide6TK.styles import QSS_WSTARTPAGE
from PySide6TK.styles import set_style
from PySide6TK.styles import STYLE_PATH
from PySide6TK.text import color_format
from PySide6TK.text import HighlightRule
from PySide6TK.toolbar import DEFAULT_ICON
from PySide6TK.toolbar import null
from PySide6TK.toolbar import Toolbar
