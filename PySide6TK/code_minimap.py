"""
# Code Mini Map

Description:

    A VSCode minimap like widget for code editors that derive from
    QPlainTextEdit.
"""


from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets


class CodeMiniMap(QtWidgets.QWidget):
    def __init__(
        self,
        editor: QtWidgets.QPlainTextEdit,
        parent: QtWidgets.QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.editor = editor
        self.text_scale = 0.15
        self.visible_rect = QtCore.QRect()
        self.line_height = 2
        self.char_width = 1

        self.setFixedWidth(120)

        self.editor.textChanged.connect(self.update)
        self.editor.verticalScrollBar().valueChanged.connect(self.update)
        self.editor.cursorPositionChanged.connect(self.update)

        self.setMouseTracking(True)

        self.update_timer = QtCore.QTimer()
        self.update_timer.timeout.connect(self.update)
        self.update_timer.setInterval(100)

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        # Boy howdy do paint events in Qt always look ugly
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, False)
        painter.fillRect(self.rect(), QtGui.QColor(30, 30, 30))

        text = self.editor.toPlainText()
        lines = text.split('\n')
        total_lines = len(lines)
        minimap_height = self.height()

        if total_lines == 0:
            return

        y_offset = 0
        char_position = 0
        for i, line in enumerate(lines):
            if y_offset >= minimap_height:
                break

            x = 5
            for j, char in enumerate(line):
                if char != ' ' and char != '\t':
                    color = self._get_char_color(char_position)
                    painter.fillRect(
                        x,
                        y_offset,
                        self.char_width,
                        self.line_height,
                        color
                    )
                x += self.char_width
                char_position += 1
                if x > self.width() - 5:
                    char_position += len(line) - j - 1
                    break

            char_position += 1  # Account for newline character
            y_offset += self.line_height

        self._draw_viewport_indicator(painter, total_lines)

    def _get_char_color(self, position: int) -> QtGui.QColor:
        """Get color from editor's text format at position"""
        fallback_color = QtGui.QColor(212, 212, 212)
        doc = self.editor.document()

        if position >= doc.characterCount():
            return fallback_color

        block = doc.findBlock(position)
        if not block.isValid():
            return fallback_color

        block_position = position - block.position()

        # Get formats for this block
        layout = block.layout()
        if layout is None:
            return fallback_color

        formats = layout.formats()

        # Find the format that applies to our position
        for fmt_range in formats:
            if fmt_range.start <= block_position < fmt_range.start + fmt_range.length:
                color = fmt_range.format.foreground().color()
                if color.isValid():
                    return color

        return fallback_color

    def _draw_viewport_indicator(
        self,
        painter: QtGui.QPainter,
        total_lines: int
    ) -> None:
        """Draw rectangle showing visible portion of editor"""
        if total_lines == 0:
            return

        first_visible = self.editor.firstVisibleBlock().blockNumber()
        viewport_height = self.editor.viewport().height()
        block_height = self.editor.fontMetrics().height()
        visible_blocks = viewport_height // block_height + 1

        content_height = total_lines * self.line_height
        minimap_height = self.height()

        # Scale to fit minimap if content is larger, otherwise use actual size
        if content_height > minimap_height:
            scale = minimap_height / content_height
            rect_y = first_visible * self.line_height * scale
            rect_height = visible_blocks * self.line_height * scale
        else:
            rect_y = first_visible * self.line_height
            rect_height = visible_blocks * self.line_height

        # View rect overlay
        painter.setPen(QtGui.QPen(QtGui.QColor(100, 100, 100), 1))
        painter.setBrush(QtGui.QColor(255, 255, 255, 30))
        painter.drawRect(0, int(rect_y), self.width(), int(rect_height))

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        """Handle click to jump to position"""
        self._scroll_to_position(event.position().y())

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        """Handle drag to scroll"""
        if event.buttons() & QtCore.Qt.MouseButton.LeftButton:
            self._scroll_to_position(event.position().y())

    def _scroll_to_position(self, y: float) -> None:
        """Scroll editor to clicked position in minimap"""
        text = self.editor.toPlainText()
        total_lines = len(text.split('\n'))

        if total_lines == 0:
            return

        # Calculate content height and scaling
        content_height = total_lines * self.line_height
        minimap_height = self.height()

        # Adjust click position based on scaling
        if content_height > minimap_height:
            scale = minimap_height / content_height
            clicked_line = int((y / scale) / self.line_height)
        else:
            clicked_line = int(y / self.line_height)

        clicked_line = max(0, min(clicked_line, total_lines - 1))

        # Move cursor to that line
        cursor = self.editor.textCursor()
        cursor.movePosition(QtGui.QTextCursor.MoveOperation.Start)
        cursor.movePosition(
            QtGui.QTextCursor.MoveOperation.Down,
            QtGui.QTextCursor.MoveMode.MoveAnchor,
            int(clicked_line),
        )
        self.editor.setTextCursor(cursor)
        self.editor.centerCursor()

        self.update()

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        """Forward scroll events to editor"""
        self.editor.wheelEvent(event)
