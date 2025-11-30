"""
# Code Mini Map

Description:

    A VSCode-like minimap widget for code editors that derive from
    QPlainTextEdit.
"""


from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets


class CodeMiniMap(QtWidgets.QWidget):
    """
    A VSCode-style minimap widget for QPlainTextEdit-based code editors.

    Displays a miniaturized, scrollable overview of the entire document
    with syntax highlighting colors. The minimap shows a viewport indicator
    rectangle representing the currently visible portion of the editor, and
    allows navigation by clicking or dragging within the minimap.

    The minimap automatically centers around the editor's current viewport
    and scrolls as you navigate through the document, similar to VSCode's
    behavior.

    Attributes:
        editor (QtWidgets.QPlainTextEdit): The text editor to create a
            minimap for.
        line_height (int): Height in pixels for each line in the minimap.
            Default: 2.
        char_width (int): Width in pixels for each character block.
            Default: 1.
        scroll_sensitivity (float): Multiplier for scroll speed when
            dragging. Values > 1.0 increase sensitivity, < 1.0 decrease it.
            Default: 1.0.
        color_brightness (float): Brightness multiplier for syntax colors.
            Range: 0.0 (black) to 1.0 (original brightness). Default: 0.6.

    Args:
        editor (QtWidgets.QPlainTextEdit): The code editor to attach the
            minimap to.
        parent (QtWidgets.QWidget | None): Optional parent widget.

    Example:
        >>> editor = CodeEditor()
        >>> minimap = CodeMiniMap(editor)
        >>> minimap.color_brightness = 0.4  # Darker colors
        >>> minimap.scroll_sensitivity = 1.5  # More sensitive scrolling
    """

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
        self.scroll_sensitivity = 1.0
        self.color_brightness = 0.6

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

        first_visible = self.editor.firstVisibleBlock().blockNumber()
        viewport_height = self.editor.viewport().height()
        block_height = self.editor.fontMetrics().height()
        visible_blocks = viewport_height // block_height + 1
        center_line = first_visible + visible_blocks // 2
        lines_in_minimap = minimap_height // self.line_height

        scroll_offset = center_line - lines_in_minimap // 2
        scroll_offset = max(
            0, min(scroll_offset, total_lines - lines_in_minimap)
        )

        start_line = max(0, int(scroll_offset))
        end_line = min(total_lines, start_line + lines_in_minimap + 1)
        char_position = sum(len(lines[i]) + 1 for i in range(start_line))

        y_offset = 0
        for i in range(start_line, end_line):
            if i >= len(lines):
                break

            line = lines[i]

            if y_offset >= minimap_height:
                break

            left_margin = 5  # default to 5 for slight padding
            for j, char in enumerate(line):
                if char != ' ' and char != '\t':
                    color = self._get_char_color(char_position)
                    painter.fillRect(
                        left_margin,
                        y_offset,
                        self.char_width,
                        self.line_height,
                        color
                    )
                left_margin += self.char_width
                char_position += 1
                if left_margin > self.width() - 5:
                    char_position += len(line) - j - 1
                    break

            char_position += 1  # Account for newline character
            y_offset += self.line_height

        self._draw_viewport_indicator(painter, total_lines, scroll_offset)

    def _get_char_color(self, position: int) -> QtGui.QColor:
        """Get color from editor's text format at position"""
        fallback_color = QtGui.QColor(212, 212, 212)
        doc = self.editor.document()

        if position >= doc.characterCount():
            return self._adjust_color_brightness(fallback_color)

        block = doc.findBlock(position)
        if not block.isValid():
            return self._adjust_color_brightness(fallback_color)

        block_position = position - block.position()

        # Get formats for this block
        layout = block.layout()
        if layout is None:
            return self._adjust_color_brightness(fallback_color)

        formats = layout.formats()

        # Find the format that applies to our position
        for fmt_range in formats:
            if fmt_range.start <= block_position < fmt_range.start + fmt_range.length:
                color = fmt_range.format.foreground().color()
                if color.isValid():
                    return self._adjust_color_brightness(color)

        return self._adjust_color_brightness(fallback_color)

    def _adjust_color_brightness(self, color: QtGui.QColor) -> QtGui.QColor:
        """Adjust color brightness for minimap display"""
        h, s, v, a = color.getHsv()
        v = int(v * self.color_brightness)
        adjusted = QtGui.QColor()
        adjusted.setHsv(h, s, v, a)
        return adjusted

    def _draw_viewport_indicator(
            self,
            painter: QtGui.QPainter,
            total_lines: int,
            scroll_offset: float = 0
    ) -> None:
        """Draw rectangle showing visible portion of editor"""
        if total_lines == 0:
            return

        first_visible = self.editor.firstVisibleBlock().blockNumber()
        viewport_height = self.editor.viewport().height()
        block_height = self.editor.fontMetrics().height()
        visible_blocks = viewport_height // block_height + 1

        # Calculate position in minimap coordinates
        rect_y = (first_visible - scroll_offset) * self.line_height
        rect_height = visible_blocks * self.line_height

        # Clamp to minimap bounds
        rect_y = max(0, int(min(rect_y, self.height() - rect_height)))
        rect_height = min(rect_height, self.height())

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

        # Calculate which line was clicked based on current scroll position
        first_visible = self.editor.firstVisibleBlock().blockNumber()
        viewport_height = self.editor.viewport().height()
        block_height = self.editor.fontMetrics().height()
        visible_blocks = viewport_height // block_height + 1

        center_line = first_visible + visible_blocks // 2
        lines_in_minimap = self.height() // self.line_height
        scroll_offset = center_line - lines_in_minimap // 2
        scroll_offset = max(
            0, min(scroll_offset, total_lines - lines_in_minimap)
        )

        # Calculate clicked line with sensitivity applied
        cur_pos = int((y / self.line_height) * self.scroll_sensitivity)
        clicked_line = cur_pos + scroll_offset
        clicked_line = max(0, min(clicked_line, total_lines - 1))

        # Center viewport
        centered_scroll_line = clicked_line - visible_blocks // 2

        # Scroll to that line without moving cursor
        scrollbar = self.editor.verticalScrollBar()
        # Compensate for last line
        centered_scroll_line = max(
            scrollbar.minimum(),
            min(centered_scroll_line, scrollbar.maximum())
        )
        scrollbar.setValue(int(centered_scroll_line))

        self.update()

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        """Forward scroll events to editor"""
        self.editor.wheelEvent(event)
