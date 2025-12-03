"""
# Help Bar

* Description:

    A toolbar to insert at the top of tools for developer and user
    convenience.
"""


import importlib
import os
import webbrowser
from functools import partial
from pathlib import Path
from types import ModuleType
from typing import Callable
from typing import Optional

from PySide6 import QtCore
from PySide6 import QtWidgets

from PySide6TK import styles
from PySide6TK import toolbar
from PySide6TK import shortcuts


class _AboutWidget(QtWidgets.QWidget):
    def __init__(
            self,
            description: Optional[str],
            version: Optional[str],
            author: Optional[str],
    ) -> None:
        super().__init__()
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        self.setWindowTitle('About')
        self.setMinimumSize(200, 200)

        text = ''
        if description:
            text += f'[Description]\n{description}\n\n'
        if version:
            text += f'[Version]\n{version}\n\n'
        if author:
            text += f'[Author]\n{author}\n\n'

        if not text:
            text = 'Nothing about ¯\\_(ツ)_/¯'

        self.label = QtWidgets.QLabel(text)
        self.layout.addWidget(self.label)


class HelpToolbar(toolbar.Toolbar):
    """
    A reusable top-of-window toolbar providing developer utilities, theme
    controls, and help/documentation actions.

    This toolbar attaches itself to the top of a parent QMainWindow-like
    widget and exposes a consistent set of convenience actions commonly
    needed in pipeline tools. It includes:

    **Developer tools**
        - Reloading the tool's Python module.
        - Rebuilding the UI by recreating the parent widget.
        - Opening the tool’s log directory.
        - Opening an embedded or external console.

    **Theme selection**
        - Dynamically applies any QSS theme defined in ``PySide6TK.styles``.
        - Uses ``functools.partial`` to avoid late-binding issues when building
          menu actions.

    **Help / About**
        - Opens a small "About" dialog displaying description, version, and
          author information.
        - Optional shortcuts to repository and documentation URLs.

    The toolbar is designed to be lightweight, self-contained, and safe to
    reuse across all GUI tools in the pipeline.

    Args:
        parent:
            The window or widget that will receive this toolbar. Must provide
            ``addToolBar`` and typically be a ``QMainWindow`` subclass.
        description:
            Short text displayed in the About dialog under [Description].
        version:
            Optional version string shown in the About dialog under [Version].
        author:
            Optional author string shown in the About dialog under [Author].
        repo_url:
            If provided, adds a "Repo" entry under the Help menu which opens the
            URL in the user's default browser.
        documentation_url:
            If provided, adds a "Documentation" entry under the Help menu.
        reload_modules:
            list of modules to reimport.
        logs_dir:
            Optional filesystem path to the tool’s log directory. When set,
            enables a "Show Logs" menu option.
        open_console_func:
            Callable used to open a developer console panel or window. Defaults
            to ``toolbar.null`` (disabled).

    Notes:
        - The toolbar sets its own button height using ``default_button_resolution``.
        - The parent UI will close and a new instance will be constructed when
          selecting "Reload UI".
        """

    def __init__(
            self,
            parent: QtWidgets.QMainWindow,
            description: Optional[str] = None,
            version: Optional[str] = None,
            author: Optional[str] = None,
            repo_url: Optional[str] = None,
            documentation_url: Optional[str] = None,
            reload_modules: list[ModuleType] = None,
            logs_dir: Optional[Path] = None,
            open_console_func: Callable = toolbar.null,
            shortcut_manager: Optional[shortcuts.KeyShortcutManager] = None
    ) -> None:
        self.parent = parent

        # developer section
        self.reload_modules: list[ModuleType] = reload_modules if reload_modules else []
        self.logs_dir: Optional[Path] = logs_dir
        self.open_console: Callable = open_console_func
        self.shortcut_manager = shortcut_manager

        # help section
        self.about_widget = _AboutWidget(description, version, author)
        self.repo_url: Optional[str] = repo_url
        self.documentation_url: Optional[str] = documentation_url

        super().__init__('Test Toolbar', default_button_resolution=[0, 20])
        self.setMovable(False)
        parent.addToolBar(QtCore.Qt.ToolBarArea.TopToolBarArea, self)

    def build(self) -> None:
        self._file_section()
        self._developer_section()
        self._theme_section()
        self._help_section()

    def _file_section(self) -> None:
        self.file_submenu = self.add_menu('File', image_path=None)

        if self.shortcut_manager is not None:
            self.add_menu_command(
                self.file_submenu, 'Shortcuts', self.shortcut_manager.show_editor
            )

    def _developer_section(self) -> None:
        self.developer_submenu = self.add_menu('Developer', image_path=None)

        if len(self.reload_modules) > 0:
            self.add_menu_command(
                self.developer_submenu, 'Reload Module', self._reload_modules
            )

        def reload_ui() -> None:
            cls = self.parent.__class__
            new_wid = cls()
            new_wid.show()
            self.parent.close()

        self.add_menu_command(self.developer_submenu, 'Reload UI', reload_ui)

        if self.logs_dir is not None:
            self.add_menu_command(
                self.developer_submenu, 'Show Logs', lambda: os.startfile(self.logs_dir.as_posix())
            )
        if self.open_console != toolbar.null:
            self.add_menu_command(
                self.developer_submenu, 'Open Console', self.open_console
            )

    def _theme_section(self) -> None:
        self.theme_submenu = self.add_menu('Theme', image_path=None)

        for k, v in styles.__dict__.items():
            if not k.startswith('QSS_'):
                continue
            name = k.replace('QSS_', '').title()
            self.add_menu_command(
                self.theme_submenu,
                name,
                # I cannot stand python's late-binding closures with lambdas...
                partial(styles.set_style, self.parent, v)
            )

    def _help_section(self) -> None:
        self.help_submenu = self.add_menu('Help', image_path=None)
        self.add_menu_command(
            self.help_submenu, 'About', lambda: self.about_widget.show()
        )

        if self.repo_url is not None:
            self.add_menu_command(
                self.help_submenu,
                'Repo',
                lambda: webbrowser.open_new_tab(self.repo_url)
            )
        if self.documentation_url is not None:
            self.add_menu_command(
                self.help_submenu,
                'Documentation',
                lambda: webbrowser.open_new_tab(self.documentation_url)
            )

    def _reload_modules(self) -> None:
        # Reload the modules twice because some modules may be dependent on others
        # that are going to be reimported, but are reimported in the wrong order,
        # thus referencing stale state.

        for i in self.reload_modules:
            importlib.reload(i)
        for i in self.reload_modules:
            importlib.reload(i)
