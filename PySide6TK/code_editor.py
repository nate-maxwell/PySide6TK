"""
# Code Editor

* Description

    A QPlainTextEdit wrapper with numbered lines and python syntax
    highlighting.
"""


from typing import Type
from typing import TypeVar

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

from PySide6TK.languages.python_syntax import PythonHighlighter


class _LineNumberArea(QtWidgets.QWidget):
    def __init__(self, code_editor: 'CodeEditor') -> None:
        super().__init__(code_editor)
        self.editor = code_editor

    def sizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(self.editor.line_number_area_width, 0)

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        self.editor.line_number_area_paint_event(event)


T_Highlighter = TypeVar('T_Highlighter', bound=QtGui.QSyntaxHighlighter)


class CodeEditor(QtWidgets.QPlainTextEdit):
    """
    A custom code-editing widget built on top of ``QPlainTextEdit`` with
    line numbers, syntax highlighting, and indentation utilities.

    This editor provides an integrated gutter (``LineNumberArea``) that
    displays line numbers alongside the text viewport, updating
    automatically in response to scrolling, resizing, or block count
    changes. The editor also supports configurable syntax highlighting
    through a user-supplied ``QSyntaxHighlighter`` subclass
    (defaulting to ``PythonHighlighter``).

    Indentation and unindentation of multiple selected lines is supported
    through Tab and Shift+Tab. Two signals, ``indented`` and
    ``unindented``, emit a ``range`` of affected line numbers, allowing
    external tools to hook into indentation events if needed.

    Attributes:
        line_number_area (_LineNumberArea):
            The side widget responsible for drawing line numbers.
        highlighter (QSyntaxHighlighter):
            The active syntax highlighter instance applied to the
            document.
        indented (Signal(range)):
            Emitted when a block of lines should be indented.
        unindented (Signal(range)):
            Emitted when a block of lines should be unindented.

    Args:
        syntax_highlighter (Type[T_Highlighter], optional):
            A ``QSyntaxHighlighter`` subclass to use for syntax
            highlighting. Defaults to ``PythonHighlighter``.

    Notes:
        - Line numbers are recalculated dynamically based on the number
          of blocks in the document.
        - The currently active line is highlighted with a background
          marker for improved readability.
        - Prefix-based indentation functions are implemented to support
          both single-line and multi-line editing workflows.
    """

    indented = QtCore.Signal(range)
    unindented = QtCore.Signal(range)

    def __init__(
            self,
            syntax_highlighter: Type[T_Highlighter] = PythonHighlighter
    ) -> None:
        super(CodeEditor, self).__init__()

        self.setTabStopDistance(QtGui.QFontMetricsF(self.font()).horizontalAdvance(' ') * 4)

        self.line_number_area = _LineNumberArea(self)
        self._create_shortcut_signals()
        self._create_connections()
        self.update_line_number_area_width(0)

        self.highlighter = syntax_highlighter(self.document())

    def _create_shortcut_signals(self) -> None:
        self.indented.connect(self.indent)
        self.unindented.connect(self.unindent)

    def _create_connections(self) -> None:
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)

    @property
    def line_number_area_width(self) -> int:
        digits = 1
        count = max(1, self.blockCount())
        while count >= 10:
            count //= 10
            digits += 1
        space = 20 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def update_line_number_area_width(self, _) -> None:
        self.setViewportMargins(self.line_number_area_width, 0, 0, 0)

    def update_line_number_area(self, rect: QtCore.QRect, dy: int) -> None:
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, e: QtGui.QResizeEvent) -> None:
        super().resizeEvent(e)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QtCore.QRect(cr.left(), cr.top(), self.line_number_area_width, cr.height()))

    def line_number_area_paint_event(self, event) -> None:
        painter = QtGui.QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QtGui.QColor(21, 21, 21))  # Background color

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        height = self.fontMetrics().height()
        while block.isValid() and (top <= event.rect().bottom()):
            if block.isVisible() and (bottom >= event.rect().top()):
                number = str(blockNumber + 1)
                painter.setPen(QtGui.QColor('lightGray'))
                painter.drawText(
                    0,
                    top,
                    self.line_number_area.width(),
                    height,
                    QtCore.Qt.AlignmentFlag.AlignLeft,
                    number
                )

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber += 1

    def highlight_current_line(self) -> None:
        extraSelections = []
        if not self.isReadOnly():
            selection = QtWidgets.QTextEdit.ExtraSelection()
            line_color = QtGui.QColor('yellow').lighter(160)

            fmt = QtGui.QTextCharFormat()
            fmt.setBackground(line_color)
            selection.format = fmt

            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
        self.setExtraSelections(extraSelections)

    def add_line_prefix(self, prefix: str, line: int) -> None:
        """
        Adds the prefix substring to the start of a line.

        Args:
            prefix (str): The substring to append to the start of the line.
            line (int): The line number to append.
        """
        cursor = QtGui.QTextCursor(self.document().findBlockByLineNumber(line))
        self.setTextCursor(cursor)
        self.textCursor().insertText(prefix)

    def remove_line_prefix(self, prefix: str, line: int) -> None:
        """
        Removes the prefix substring from the start of a line.

        Args:
            prefix (str): The substring to remove from the start of the line.
            line (int): The line number to adjust.
        """
        cursor = QtGui.QTextCursor(self.document().findBlockByLineNumber(line))
        cursor.select(QtGui.QTextCursor.SelectionType.LineUnderCursor)
        text = cursor.selectedText()
        if text.startswith(prefix):
            cursor.removeSelectedText()
            cursor.insertText(text.split(prefix, 1)[-1])

    def _get_selection_range(self) -> tuple[int, int]:
        """
        Returns the first and last line of a continuous selection.

        Returns
            tuple[int, int]: First line number and last line number.
        """
        if not self.textCursor().hasSelection():
            return 0, 0

        cursor = self.textCursor()
        start_pos = cursor.selectionStart()
        end_pos = cursor.selectionEnd()

        cursor.setPosition(start_pos)
        first_line = cursor.blockNumber()
        cursor.setPosition(end_pos)
        last_line = cursor.blockNumber()

        return first_line, last_line

    def indent(self, lines: range) -> None:
        """Indent the lines within the given range."""
        for i in lines:
            self.add_line_prefix('\t', i)

    def unindent(self, lines: range) -> None:
        """Unindent the lines within the given range."""
        for i in lines:
            self.remove_line_prefix('\t', i)

    def keyPressEvent(self, e: QtGui.QKeyEvent) -> None:
        """Enable shortcuts in keypress event."""
        first_line, last_line = self._get_selection_range()

        if e.key() == QtCore.Qt.Key.Key_Tab and last_line - first_line:
            lines = range(first_line, last_line + 1)
            self.indented.emit(lines)
            return

        if e.key() == QtCore.Qt.Key.Key_Backtab:
            lines = range(first_line, last_line + 1)
            self.unindented.emit(lines)
            return

        super(CodeEditor, self).keyPressEvent(e)
