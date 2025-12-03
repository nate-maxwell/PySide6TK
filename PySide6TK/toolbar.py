"""
# Toolbar

* Description:

    This is a maya shelf-like toolbar for use in various applications.
"""


from pathlib import Path
from typing import Callable
from typing import Optional

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

import PySide6TK.icons
import PySide6TK.shapes


def null(*args) -> None:
    """Dummy func that does nothing. A placeholder for menu items not yet
    assigned a connected function.
    """
    pass


_SEP = '---------------'
"""Submenu separator via text insert."""


class Toolbar(QtWidgets.QToolBar):
    """A shelf-like toolbar providing buttons and nested sub-menus.

    This class serves as a customizable base for application toolbars that
    require button and submenu organization similar to a "shelf" layout.
    Developers should subclass and override the ``build`` method to
    populate toolbar items.

    Args:
        toolbar_name (str): The name of the toolbar.
        parent (Optoinal[QtWidget.QWidget]): What to parent the toolbar to.
        default_button_resolution (list[int]): The default resolution for
            buttons, e.g. [x, y]. If a value is 0, it is not used.
            Defaults to [40, 40].

    Example:
        >>> class MyToolbar(Toolbar):
        ...     def build(self) -> None:
        ...         self.add_toolbar_command('Save', library.save_command)
        ...
        >>> toolbar = MyToolbar('My Tools')

    Attributes:
        default_button_resolution (list[int]): The default width and height of
            toolbar buttons, in pixels. Defaults to ``[40, 40]``.
        icon_brightness (float): The brightness factor applied to icons to
            normalize their appearance. Defaults to ``0.2``.

    Notes:
        - The ``build`` method **must** be overridden in subclasses.
          Failure to do so will raise ``NotImplemented``.
        - Buttons can be added with or without icons.
        - Submenus can be nested indefinitely using
          ``add_submenu_submenu``.
    """
    def __init__(
            self,
            toolbar_name: str,
            parent: Optional[QtWidgets.QWidget] = None,
            default_button_resolution: list[int] = None
    ) -> None:
        super().__init__(parent=parent)
        if default_button_resolution is None:
            self.default_button_resolution = [40, 40]
        else:
            self.default_button_resolution = default_button_resolution

        self.icon_brightness: float = 0.2

        self.setObjectName(toolbar_name.replace(' ', '_'))
        self.setWindowTitle(toolbar_name)
        self.setMovable(False)
        self.build()

    def _make_toolbar_button(
            self,
            button_image: Optional[Path] = None
    ) -> QtWidgets.QToolButton:
        """
        Boilerplate for making a toolbar button with an icon. If button_image
        is set to None, a blank item is added.

        Button w/h are set based on self.default_button_resolution.
        """
        tool_button = QtWidgets.QToolButton()
        tool_button.setContentsMargins(0, 0, 0, 0)
        x = self.default_button_resolution[0]
        if x > 0:
            tool_button.setFixedWidth(x)
        y = self.default_button_resolution[1]
        if y > 0:
            tool_button.setFixedHeight(y)
        if button_image is None:
            tool_button.setToolButtonStyle(
                QtCore.Qt.ToolButtonStyle.ToolButtonTextOnly
            )
            return tool_button

        tool_button.setStyleSheet(f"""
            QToolButton {{
                background: url('{button_image.as_posix()}');
                background-position: center;                /* Center the image */
                background-repeat: no-repeat;               /* Prevent tiling */
                background-size: cover;                     /* Scale the image to fill the button */
                background-color: rgba(0, 0, 0, 0.1);       /* Add a semi-transparent black overlay */
                font-size: 10px;
            }}
        """)

        return tool_button

    def add_toolbar_command(
            self,
            label: str,
            command: Callable = null,
            image_path: Optional[Path] = None
    ) -> None:
        """Adds a toolbar button that is connected to the given command.

        Args:
            label (str): The button label.
            command (Callable): The function to connect to the button press,
              defaults to pass.
            image_path (Optional[Path]): The path to the button icon, if set to
              None: a blank item is added.
              Defaults to PySide6TK.gui.BUTTON_BLACK_40X40.
        """
        action = QtGui.QAction(label, self)
        action.triggered.connect(command)

        tool_button = self._make_toolbar_button(image_path)
        tool_button.setDefaultAction(action)
        self.addWidget(tool_button)

    def add_menu(
            self,
            label: str,
            image_path: Optional[Path] = None
    ) -> QtWidgets.QMenu:
        """Adds a menu, a collapsable list of options, to the toolbar.

        Args:
            label (str): The menu label.
            image_path (Optional[Path]): The path to the menu icon, if set to
              None: a blank item is added.
              Defaults to PySide6TK.gui.BUTTON_BLACK_40X40.

        Returns:
            QtWidgets.QMenu: The created menu, incase further submenus need
              to be added to the created menu.
        """
        submenu = QtWidgets.QMenu(f'{label}_submenu', self)

        action = QtGui.QAction(label, self)  # The actual label on the dropdown
        action.setMenu(submenu)

        tool_button = self._make_toolbar_button(image_path)
        tool_button.setDefaultAction(action)
        tool_button.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup)
        tool_button.setArrowType(QtCore.Qt.ArrowType.NoArrow)
        self.addWidget(tool_button)

        return submenu

    def add_submenu(
            self,
            label: str,
            parent: QtWidgets.QMenu
    ) -> QtWidgets.QMenu:
        """Adds a nested submenu to the given menu parent.

        Args:
            label (str): The submenu text label.
            parent (QtWidgets.QMenu): The menu to add the submenu to.

        Returns:
            QtWidgets.QMenu: The created submenu, incase further submenus need
                to be added to the created submenu.
        """
        submenu = QtWidgets.QMenu(f'{label}_submenu', self)
        action = QtGui.QAction(label, self)  # The actual label on the dropdown
        action.setMenu(submenu)
        parent.addMenu(submenu)

        return submenu

    @staticmethod
    def add_menu_command(
            submenu: QtWidgets.QMenu,
            cmd_name: str,
            cmd: Callable = null
    ) -> None:
        """Adds an item to the given submenu connected to the given command.

        Args:
            submenu (QtWidgets.QMenu): The submenu to add the item to.
            cmd_name (str): The text label for the added item.
            cmd (Callable): The function to connect the item selection to.
        """
        item = submenu.addAction(cmd_name)
        item.triggered.connect(cmd)

    def add_menu_separator(
            self,
            submenu: QtWidgets.QMenu,
            label: str = _SEP
    ) -> None:
        """Adds a dummy item to the given submenu, with the given label.
        Label defaults to '---------------'.
        """
        self.add_menu_command(submenu, label, null)

    def add_toolbar_separator(self, width: int = 10) -> None:
        """Adds a horizontal spacer to the toolbar of the given width.
        Width defaults to 10.
        """
        self.addWidget(PySide6TK.shapes.HorizontalSpacer(width))

    def build(self) -> None:
        """The derived class's constructor.
        This will build the toolbar widgets/layout.
        """
        raise NotImplemented
