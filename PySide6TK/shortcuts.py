"""
# Shortcuts

* Description:

    Shortcut widgets and helper functions.
"""


from dataclasses import dataclass
from typing import Callable
from typing import Optional

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

import PySide6TK.layout
import PySide6TK.shapes
import PySide6TK.scroll_area


MODIFIER_KEYS = (
    QtCore.Qt.Key.Key_Control,
    QtCore.Qt.Key.Key_Shift,
    QtCore.Qt.Key.Key_Alt,
    QtCore.Qt.Key.Key_Meta
)


@dataclass
class _Shortcut(object):
    """
    Internal data structure for storing shortcut information.

    Attributes:
        shortcut (QtGui.QShortcut): The Qt shortcut object that handles key
            events.
        key_sequence (str): String representation of the key combination
            (e.g., "Ctrl+N").
        callback (Callable): Function to execute when the shortcut is activated.
        description (str): Human-readable description of what the shortcut does.
    """
    shortcut: QtGui.QShortcut
    key_sequence: str
    callback: Callable
    description: str = ""


class KeyShortcutManager(object):
    """
    Manager for keyboard shortcuts in a Qt application.

    This class provides a centralized way to add, remove, update, and list
    keyboard shortcuts. It also provides a GUI editor for users to view and
    modify shortcuts.

    Attributes:
        parent (QtWidgets.QWidget): The parent widget for the shortcuts.
        shortcuts (dict[str, _Shortcut]): Dictionary mapping action names to
            shortcut objects.

    Example:
        >>> manager = KeyShortcutManager(parent_widget)
        >>> manager.add_shortcut("new_file", "Ctrl+N", on_new_file, "Create new file")
        >>> manager.show_editor()  # Opens the shortcut editor dialog
    """

    def __init__(self, parent: QtWidgets.QWidget) -> None:
        self.parent = parent
        self.shortcuts: dict[str, _Shortcut] = {}

    def add_shortcut(
            self,
            action_name: str,
            key_sequence: str,
            callback: Callable,
            description: str = ''
    ) -> None:
        """
        Add a keyboard shortcut.

        Args:
            action_name (str): Unique identifier for this shortcut
            key_sequence (str): String like "Ctrl+N" or QKeySequence
            callback (Callable): Function to call when shortcut is activated
            description (str): Human-readable description
        """
        if action_name in self.shortcuts:
            self.remove_shortcut(action_name)

        new_shortcut = QtGui.QShortcut(
            QtGui.QKeySequence(key_sequence),
            self.parent
        )
        new_shortcut.activated.connect(callback)

        self.shortcuts[action_name] = _Shortcut(
            new_shortcut,
            key_sequence,
            callback,
            description
        )

    def remove_shortcut(self, action_name: str) -> None:
        """Remove a shortcut by action name."""
        entry = self.shortcuts.pop(action_name, None)
        if entry is None:
            return
        entry.shortcut.setEnabled(False)
        entry.shortcut.deleteLater()

    def update_shortcut(self, action_name: str, new_key_sequence: str) -> None:
        """Update an existing shortcut with a new key sequence."""
        if action_name not in self.shortcuts:
            raise KeyError(f'Shortcut action {action_name} not found.')

        entry = self.shortcuts[action_name]
        callback = entry.callback
        description = entry.description

        self.add_shortcut(action_name, new_key_sequence, callback, description)

    def get_shortcut_key(self, action_name: str) -> Optional[str]:
        if action_name in self.shortcuts:
            return self.shortcuts[action_name].key_sequence
        return None

    def list_shortcuts(self) -> list[tuple[str, str, str]]:
        """Returns a list of all shortcuts as
        list[tuple[action_name, key_sequence, description]].
        """
        return [
            (action_name, entry.key_sequence, entry.description)
            for action_name, entry in self.shortcuts.items()
        ]

    def show_editor(self) -> None:
        editor = _ShortcutEditorDialog(self, self.parent)
        editor.exec()


class _ShortcutEditorDialog(QtWidgets.QDialog):
    """
    Dialog for viewing and editing keyboard shortcuts.

    This modal dialog displays all registered shortcuts in a scrollable list,
    allowing users to view current key bindings and edit them interactively.
    Each shortcut is displayed as a row showing the action name, key sequence,
    and description.

    Attributes:
        manager (KeyShortcutManager): The shortcut manager this dialog edits.
        parent (QtWidgets.QWidget, optional): Parent widget for the dialog.
        sa_rows (PySide6TK.scroll_area.ScrollArea): Scrollable area containing
            shortcut rows.
        hlayout_buttons (QtWidgets.QHBoxLayout): Layout for dialog buttons.
        btn_close (QtWidgets.QPushButton): Button to close the dialog.
        layout_main (QtWidgets.QVBoxLayout): Main layout for the dialog.
    """

    def __init__(
            self,
            manager: KeyShortcutManager,
            parent: Optional[QtWidgets.QWidget] = None
    ) -> None:
        super().__init__(parent)
        self.manager = manager
        self.parent = parent
        self.setWindowTitle('Keyboard Shortcuts')
        self.setMinimumSize(800, 400)
        self._create_widgets()
        self._create_layout()
        self._create_connections()
        self.load_shortcuts()

    def _create_widgets(self) -> None:
        # Rows
        self.sa_rows = PySide6TK.scroll_area.ScrollArea()

        # Buttons
        self.hlayout_buttons = QtWidgets.QHBoxLayout()
        self.btn_close = QtWidgets.QPushButton('Close')

        # Main
        self.layout_main = QtWidgets.QVBoxLayout()

    def _create_layout(self) -> None:
        # Buttons
        self.hlayout_buttons.addStretch()
        self.hlayout_buttons.addWidget(self.btn_close)

        # Main
        self.setLayout(self.layout_main)
        self.layout_main.addWidget(self.sa_rows)
        self.layout_main.addLayout(self.hlayout_buttons)

    def _create_connections(self) -> None:
        self.btn_close.clicked.connect(self.accept)

    def load_shortcuts(self) -> None:
        shortcuts = self.manager.list_shortcuts()
        if len(shortcuts) == 0:
            msg = 'Application has no shortcuts!'
            self.sa_rows.add_widget(QtWidgets.QLabel(msg))

        for action, key, description in shortcuts:
            row_wid = _ShortcutRow(
                self.manager,
                action,
                key,
                description,
                self
            )
            self.sa_rows.add_widget(row_wid)

        self.sa_rows.add_stretch()


class _ShortcutRow(QtWidgets.QWidget):
    """
    Widget representing a single shortcut row in the editor dialog.

    Each row displays the action name, current key sequence, and description
    in read-only line edit fields. An "Edit" button allows the user to modify
    the key sequence through a key capture dialog.

    Attributes:
        manager (KeyShortcutManager): The shortcut manager to update when editing.
        parent (QtWidgets.QWidget, optional): Parent widget.
        layout_main (QtWidgets.QHBoxLayout): Main horizontal layout for the row.
        le_act (QtWidgets.QLineEdit): Line edit displaying the action name.
        le_key (QtWidgets.QLineEdit): Line edit displaying the key sequence.
        le_desc (QtWidgets.QLineEdit): Line edit displaying the description.
        btn_edit (QtWidgets.QPushButton): Button to open the key capture dialog.
    """
    def __init__(
            self,
            manager: KeyShortcutManager,
            action: str,
            key: str,
            description: str,
            parent: Optional[QtWidgets.QWidget] = None
    ) -> None:
        super().__init__(parent)
        self.manager = manager
        self.parent = parent

        self.layout_main = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout_main)

        self.le_act = self._make_line_edit(action)
        self.layout_main.addWidget(self.le_act)
        self.layout_main.addWidget(PySide6TK.shapes.VerticalLine())

        self.le_key = self._make_line_edit(key, 200)
        self.layout_main.addWidget(self.le_key)
        self.layout_main.addWidget(PySide6TK.shapes.VerticalLine())

        self.le_desc = self._make_line_edit(description, 0)
        self.layout_main.addWidget(self.le_desc)

        self.btn_edit = QtWidgets.QPushButton('Edit')
        self.btn_edit.clicked.connect(self._edit_shortcut)

        self.layout_main.addWidget(self.btn_edit)

    @staticmethod
    def _make_line_edit(text: str, width: int = 150) -> QtWidgets.QLineEdit:
        le = QtWidgets.QLineEdit()
        le.setText(text)
        if width > 0:
            le.setMinimumWidth(width)
            le.setMaximumWidth(width)
        le.setReadOnly(True)
        return le

    def _edit_shortcut(self) -> None:
        dialog = _KeyCaptureDialog(self.le_key.text(), self)
        if dialog.exec():
            new_key = dialog.get_key_sequence()
            try:
                self.manager.update_shortcut(self.le_act.text(), new_key)
                self.le_key.setText(new_key)
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self,
                    'Error',
                    f'Failed to update shortcut: {str(e)}'
                )


class _KeyCaptureDialog(QtWidgets.QDialog):
    """
    Modal dialog for capturing a new keyboard shortcut from user input.

    This dialog waits for the user to press a key combination and captures it
    as a new shortcut. Modifier-only keys (Ctrl, Shift, Alt, Meta) are ignored
    until combined with a regular key. The dialog accepts the input when a
    valid key combination is pressed.

    Attributes:
        current_key (str): The current key sequence being replaced.
        new_key (str, optional): The newly captured key sequence.
        layout_main (QtWidgets.QVBoxLayout): Main layout for the dialog.
        label (QtWidgets.QLabel): Label showing instructions and current key.
        hlayout_button (QtWidgets.QHBoxLayout): Layout for dialog buttons.
        btn_cancel (QtWidgets.QPushButton): Button to cancel key capture.
    """

    def __init__(
            self,
            current_key: str,
            parent: Optional[QtWidgets.QWidget] = None
    ) -> None:
        super().__init__(parent)
        self.current_key = current_key
        self.new_key: Optional[str] = None
        self.setWindowTitle('Press New Shortcut')
        self._create_widgets()
        self._create_layout()
        self._create_connections()

    def _create_widgets(self) -> None:
        self.layout_main = QtWidgets.QVBoxLayout()
        self.label = QtWidgets.QLabel(
            f'Current: {self.current_key}\n\nPress new key combination...'
        )
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label.setMinimumHeight(80)

        self.hlayout_button = QtWidgets.QHBoxLayout()
        self.btn_cancel = QtWidgets.QPushButton('Cancel')

    def _create_layout(self) -> None:
        self.setLayout(self.layout_main)
        self.layout_main.addWidget(self.label)
        self.layout_main.addLayout(self.hlayout_button)

    def _create_connections(self) -> None:
        self.btn_cancel.clicked.connect(self.reject)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        """Capture the key press..."""
        key = event.key()

        if key in MODIFIER_KEYS:
            return  # Ignore modifier-only presses

        key_sequence = QtGui.QKeySequence(event.keyCombination())
        self.new_key = key_sequence.toString()
        self.accept()

    def keyReleaseEvent(self, event: QtGui.QKeyEvent) -> None:
        """Accept on Enter key."""
        if event.key() == QtCore.Qt.Key.Key_Return and self.new_key:
            self.accept()

    def get_key_sequence(self) -> str:
        """Return captured key seq."""
        return self.new_key
