"""
PySide6 File Tree Widget for Code IDE.
A comprehensive file browser with icons, context menus, and file filtering.
"""


import os
import platform
import subprocess
from pathlib import Path
from typing import Optional, List

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets


class FileTreeWidget(QtWidgets.QTreeView):
    """
    A file tree widget designed for code IDE integration.

    Signals:
        file_opened: Emitted when a file is double-clicked (str: file_path)
        file_selected: Emitted when a file is selected (str: file_path)
        directory_changed: Emitted when the root directory changes (str: dir_path)
    """

    file_opened = QtCore.Signal(str)
    file_selected = QtCore.Signal(str)
    directory_changed = QtCore.Signal(str)

    def __init__(
            self,
            root_path: Optional[Path] = None,
            parent: Optional[QtWidgets.QWidget] = None
    ) -> None:
        super().__init__(parent)

        self.model = QtWidgets.QFileSystemModel()
        self.model.setRootPath('')

        self.model.setNameFilters([
            '*.py', '*.pyw',  # Python
            '*.js', '*.jsx', '*.ts', '*.tsx',  # JavaScript/TypeScript
            '*.html', '*.css', '*.scss', '*.sass',  # Web
            '*.cpp', '*.c', '*.cs', '*.h', '*.hpp',  # C/C++
            '*.java',  # Java
            '*.go',  # Go
            '*.rs',  # Rust
            '*.json', '*.xml', '*.yaml', '*.yml', '*.toml',  # Config
            '*.md', '*.txt', '*.rst',  # Documentation
            '*.sh', '*.bat', '*.ps1',  # Scripts
            '*'  # Show all files by default
        ])
        self.model.setNameFilterDisables(False)
        self.setModel(self.model)

        if root_path and root_path.exists():
            self.set_root_path(root_path)
        else:
            self.set_root_path(Path(QtCore.QDir.homePath()))

        self.setAnimated(True)
        self.setIndentation(20)
        self.setSortingEnabled(True)
        self.sortByColumn(0, QtCore.Qt.SortOrder.AscendingOrder)

        self.setColumnHidden(1, True)  # Size
        self.setColumnHidden(2, True)  # Type
        self.setColumnHidden(3, True)  # Date Modified

        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        self.doubleClicked.connect(self.on_double_click)
        self.clicked.connect(self.on_click)

        self.expandToDepth(0)

    def set_root_path(self, path: Path) -> bool:
        """Set the root directory for the file tree."""
        if path.exists():
            index = self.model.setRootPath(str(path))
            self.setRootIndex(index)
            self.directory_changed.emit(str(path))
            return True
        return False

    def get_root_path(self) -> Path:
        """Get the current root directory."""
        return Path(self.model.rootPath())

    def on_double_click(self, index: QtCore.QModelIndex) -> None:
        """Handle double-click events.
        Emits file_opened signal if the double-clicked item is a file.
        """
        file_path = Path(self.model.filePath(index))

        if file_path.is_file():
            self.file_opened.emit(str(file_path))

    def on_click(self, index: QtCore.QModelIndex) -> None:
        """Handle single-click events.
        Emits a file_selected signal if the single-clicked item is a file.
        """
        file_path = Path(self.model.filePath(index))

        if file_path.is_file():
            self.file_selected.emit(str(file_path))

    def show_context_menu(self, position: QtCore.QPoint) -> None:
        """Show context menu for file operations."""
        index = self.indexAt(position)

        if not index.isValid():
            return

        file_path = Path(self.model.filePath(index))

        menu = QtWidgets.QMenu(self)

        # Actions based on whether it's a file or directory
        if file_path.is_file():
            open_action = QtGui.QAction('Open', self)
            open_action.triggered.connect(
                lambda: self.file_opened.emit(str(file_path)))
            menu.addAction(open_action)

            menu.addSeparator()

            rename_action = QtGui.QAction('Rename', self)
            rename_action.triggered.connect(
                lambda: self.rename_item(file_path))
            menu.addAction(rename_action)

            delete_action = QtGui.QAction('Delete', self)
            delete_action.triggered.connect(
                lambda: self.delete_item(file_path))
            menu.addAction(delete_action)

        elif file_path.is_dir():
            new_file_action = QtGui.QAction('New File', self)
            new_file_action.triggered.connect(
                lambda: self.create_new_file(file_path))
            menu.addAction(new_file_action)

            new_folder_action = QtGui.QAction('New Folder', self)
            new_folder_action.triggered.connect(
                lambda: self.create_new_folder(file_path))
            menu.addAction(new_folder_action)

            menu.addSeparator()

            rename_action = QtGui.QAction('Rename', self)
            rename_action.triggered.connect(
                lambda: self.rename_item(file_path))
            menu.addAction(rename_action)

            delete_action = QtGui.QAction('Delete', self)
            delete_action.triggered.connect(
                lambda: self.delete_item(file_path))
            menu.addAction(delete_action)

        menu.addSeparator()

        # Reveal in system file manager
        reveal_action = QtGui.QAction('Reveal in File Manager', self)
        reveal_action.triggered.connect(
            lambda: self.reveal_in_file_manager(file_path))
        menu.addAction(reveal_action)

        # Copy path
        copy_path_action = QtGui.QAction('Copy Path', self)
        copy_path_action.triggered.connect(
            lambda: self.copy_path_to_clipboard(file_path))
        menu.addAction(copy_path_action)

        menu.exec_(self.viewport().mapToGlobal(position))

    def create_new_file(self, parent_dir: Path) -> None:
        """Create a new file in the specified directory."""
        file_name, ok = QtWidgets.QInputDialog.getText(
            self, 'New File', 'Enter file name:'
        )

        if ok and file_name:
            new_file_path = parent_dir / file_name
            try:
                new_file_path.touch()

                # Open the newly created file
                self.file_opened.emit(str(new_file_path))

            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self, 'Error', f'Could not create file: {str(e)}'
                )

    def create_new_folder(self, parent_dir: Path) -> None:
        """Create a new folder in the specified directory."""
        folder_name, ok = QtWidgets.QInputDialog.getText(
            self, 'New Folder', 'Enter folder name:'
        )

        if ok and folder_name:
            new_folder_path = parent_dir / folder_name
            try:
                new_folder_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self, 'Error', f'Could not create folder: {str(e)}'
                )

    def rename_item(self, path: Path) -> None:
        """Rename a file or directory."""
        old_name = path.name
        new_name, ok = QtWidgets.QInputDialog.getText(
            self, 'Rename', 'Enter new name:', text=old_name
        )

        if ok and new_name and new_name != old_name:
            new_path = path.parent / new_name
            try:
                path.rename(new_path)
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self, 'Error', f'Could not rename: {str(e)}'
                )

    def delete_item(self, path: Path) -> None:
        """Delete a file or directory."""
        item_type = 'folder' if path.is_dir() else 'file'

        reply = QtWidgets.QMessageBox.question(
            self,
            'Confirm Delete',
            f'Are you sure you want to delete this {item_type}?\n\n{path}',
            QtWidgets.QMessageBox.StandardButton.Yes |
            QtWidgets.QMessageBox.StandardButton.No,
            QtWidgets.QMessageBox.StandardButton.No
        )

        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            try:
                if path.is_file():
                    path.unlink()
                elif path.is_dir():
                    import shutil
                    shutil.rmtree(path)
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self, 'Error',
                    f'Could not delete: {str(e)}'
                )

    def reveal_in_file_manager(self, path: Path) -> None:
        """Open the file's location in the system file manager."""
        directory = path if path.is_dir() else path.parent

        try:
            if platform.system() == 'Windows':
                os.startfile(str(directory))
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', str(directory)])
            else:  # Linux
                subprocess.run(['xdg-open', str(directory)])
        except Exception as e:
            QtWidgets.QMessageBox.warning(
                self, 'Warning',
                f'Could not open file manager: {str(e)}'
            )

    @staticmethod
    def copy_path_to_clipboard(path: Path) -> None:
        """Copy the file path to clipboard."""
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(str(path))

    def set_file_filters(self, filters: List[str]) -> None:
        """
        Set custom file filters.

        Args:
            filters: List of file patterns (e.g., ['*.py', '*.txt'])
        """
        self.model.setNameFilters(filters)

    def get_selected_path(self) -> Optional[Path]:
        """Get the currently selected file/directory path."""
        indexes = self.selectedIndexes()
        if indexes:
            return Path(self.model.filePath(indexes[0]))
        return None
