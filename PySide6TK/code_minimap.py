"""
# Code Mini Map

Description:

    A VSCode minimap like widget for code editors that derive from
    QPlainTextEdit.
"""


from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

import PySide6TK


class CodeMiniMapWidget(QtWidgets.QWidget):
    """
        A compact VSCode-style minimap widget that provides a visual overview of
        a ``QPlainTextEdit`` document and allows direct navigation by clicking
        and dragging.

        This minimap renders the document using thin horizontal bars—one per
        line—scaled to a fixed pixel height. Each bar is segmented horizontally
        according to the editor’s syntax-highlighting runs (via
        ``QTextLayout.formats()``), producing a miniature color-encoded preview
        of the document structure. Empty or whitespace lines are displayed as
        faint bars to provide visual continuity.

        The green viewport rectangle represents the currently visible portion of
        the editor. Its position and height are computed from the editor’s
        vertical scrollbar using a proportional mapping based on
        ``value``, ``maximum``, and ``pageStep``. This ensures correct behavior
        even with variable block heights, word-wrapped lines, or partial last
        pages.

        Navigation is supported via mouse interaction:
        - Left-clicking jumps the editor to the clicked region.
        - Clicking and dragging scrolls smoothly by continuously updating the
          scrollbar position.
        - Dragging clamps to the painted minimap area to prevent overshooting.

        The minimap can be attached to or detached from editors using
        ``set_editor()``, which updates its signal connections to track text
        changes and scrollbar movement.

        Attributes:
            editor (QtWidgets.QPlainTextEdit | None):
                The code editor that the minimap visualizes. May be set at
                construction time or later via ``set_editor()``.
            line_height (int):
                The height in pixels of each minimap line. Controls vertical
                compression.
            margin (int):
                Horizontal margin (left and right) for all drawn bars.
            _dragging (bool):
                True when the user is dragging the viewport on the minimap.

        Args:
            editor (QtWidgets.QPlainTextEdit, optional):
                The editor instance to visualize. If omitted, the minimap starts
                unattached and can be bound later.
            parent (QWidget, optional):
                The parent widget, if any.

        Notes:
            - The minimap paints only the number of lines that fit in its own
              vertical space. Remaining vertical area is filled with faint bars
              to avoid blank regions.
            - Syntax coloration is derived directly from each block’s
              ``QTextLayout`` using its ``formats()`` ranges.
            - Viewport mapping is pixel-accurate and independent of the editor’s
              block heights or text layout details.
            - The widget automatically updates when the editor’s text changes
              or when the vertical scrollbar moves.
        """

    def __init__(
            self,
            editor: QtWidgets.QPlainTextEdit = None,
            parent: PySide6TK.MENU_TYPE = None
    ) -> None:
        super().__init__(parent)
        self.editor = editor

        self.line_height = 3
        self.margin = 2

        self.setMinimumWidth(80)
        self.setMaximumWidth(120)
        self.setStyleSheet('background: #222;')

        if self.editor:
            self.editor.textChanged.connect(self.update)
            self.editor.verticalScrollBar().valueChanged.connect(self.update)

        self._dragging = False
        self.setMouseTracking(True)

    def set_editor(self, editor: QtWidgets.QPlainTextEdit) -> None:
        if self.editor:
            try:
                self.editor.textChanged.disconnect(self.update)
                self.editor.verticalScrollBar().valueChanged.disconnect(self.update)
            except Exception:
                pass

        self.editor = editor
        if self.editor:
            self.editor.updateRequest.connect(lambda *_: self.update())
            self.editor.textChanged.connect(self.update)
            self.editor.verticalScrollBar().valueChanged.connect(self.update)

        self.update()

    # -----Line drawing--------------------------------------------------------

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        """Paint a VSCode-style color-bar minimap.

        Draws one thin horizontal bar per document line. Each bar is segmented
        horizontally according to syntax highlight runs (from the editor's
        QSyntaxHighlighter), using each run's foreground color.
        Empty/whitespace lines are de-emphasized.

        Args:
            event (QtGui.QPaintEvent): The paint event.
        """
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QtGui.QColor('#222'))  # Background

        if not self.editor:
            painter.end()
            return

        self._draw_lines(painter)
        self._draw_view_area(painter)
        painter.end()

    def _draw_lines(self, painter: QtGui.QPainter) -> None:
        """Draw color bars by sampling blocks across the entire document height."""
        doc = self.editor.document()
        total_blocks = doc.blockCount()
        if total_blocks <= 0:
            return

        inner_w = max(1, self.width() - 2 * self.margin)
        max_lines = max(0, self.height() // self.line_height)
        if max_lines <= 0:
            return

        # Map each minimap row i -> a document block index
        # Use (total_blocks - 1) so the last block maps to the very bottom row.
        denom = max(1, total_blocks - 1)

        for i in range(max_lines):
            block_idx = min(total_blocks - 1, int(i * denom / max(1, max_lines - 1)))
            block = doc.findBlockByNumber(block_idx)
            y = i * self.line_height

            text = block.text()
            if not text:
                painter.fillRect(self.margin, y, inner_w, self.line_height - 1, QtGui.QColor('#2a2a2a'))
                continue

            layout = block.layout()
            runs = layout.formats()
            if runs:
                text_len = max(1, len(text))
                for run in runs:
                    if run.length <= 0:
                        continue
                    x0_ratio = max(0.0, run.start / text_len)
                    x1_ratio = min(1.0, (run.start + run.length) / text_len)
                    x = self.margin + int(x0_ratio * inner_w)
                    w = max(1, int((x1_ratio - x0_ratio) * inner_w))
                    color = run.format.foreground().color()
                    if not color.isValid():
                        color = QtGui.QColor('#666')
                    painter.fillRect(x, y, w, self.line_height - 1, color)
            else:
                painter.fillRect(self.margin, y, inner_w, self.line_height - 1, QtGui.QColor('#666'))

    def _draw_view_area(self, painter: QtGui.QPainter) -> None:
        """Draws a green square on the minimap corresponding to the viewed
        lines of code.
        """
        if not self.editor:
            return

        inner_w = max(1, self.width() - 2 * self.margin)
        max_lines = max(0, self.height() // self.line_height)
        usable_h = max_lines * self.line_height
        if usable_h <= 0:
            return

        first_idx, visible_count, total_blocks = self._visible_block_span()
        if total_blocks <= 0 or visible_count <= 0:
            return

        # Use the same denominator as _draw_lines so the scales match.
        denom = max(1, total_blocks - 1)

        # Map block indices → minimap Y with identical scaling to _draw_lines
        y_top = int((first_idx / denom) * (usable_h - self.line_height))
        # Show last visible block; +visible_count-1 to include the last block itself
        last_idx = min(total_blocks - 1, first_idx + max(1, visible_count) - 1)
        y_bottom = int((last_idx / denom) * (usable_h - self.line_height)) + self.line_height

        y = max(0, min(y_top, usable_h - 2))
        h = max(2, min(y_bottom - y_top, usable_h - y))

        painter.setPen(QtGui.QColor('#59ff00'))
        painter.drawRect(self.margin, y, inner_w - 1, h)

    # -----Mouse events--------------------------------------------------------

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if not self.editor:
            return
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._dragging = True
            self.setCursor(QtCore.Qt.CursorShape.ClosedHandCursor)
            # Map to scrollbar; y within the painted/usable area
            y = event.position().y()
            self._scroll_to_minimap_y(y, center=True)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if self._dragging and self.editor:
            y = event.position().y()
            self._scroll_to_minimap_y(y, center=True)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._dragging = False
            self.unsetCursor()
        super().mouseReleaseEvent(event)

    def leaveEvent(self, event: QtCore.QEvent) -> None:
        # If the mouse leaves while dragging, stop cleanly
        if self._dragging:
            self._dragging = False
            self.unsetCursor()
        super().leaveEvent(event)

    # -----CLick + dragging----------------------------------------------------

    def _usable_metrics(self) -> tuple[int, int, int]:
        """Return (inner_w, max_lines, usable_h) used everywhere."""
        inner_w = max(1, self.width() - 2 * self.margin)
        max_lines = max(0, self.height() // self.line_height)
        usable_h = max_lines * self.line_height
        return inner_w, max_lines, usable_h

    def _viewport_box_height(self) -> int:
        """Viewport height in minimap pixels (for centering during drag)."""
        vbar = self.editor.verticalScrollBar()
        page = max(1, vbar.pageStep())
        maximum = max(0, vbar.maximum())
        total = page + maximum if (page + maximum) else 1
        _, _, usable_h = self._usable_metrics()
        return max(2, int((page / total) * usable_h))

    def _scroll_to_minimap_y(self, y: float, center: bool = True) -> None:
        """Scroll the editor so the minimap viewport aligns with y."""
        if not self.editor:
            return

        vbar = self.editor.verticalScrollBar()
        page = max(1, vbar.pageStep())
        maximum = max(0, vbar.maximum())
        total = page + maximum
        if total <= 0:
            return

        _, _, usable_h = self._usable_metrics()
        if usable_h <= 0:
            return

        if center:
            y = y - self._viewport_box_height() / 2.0

        # Clamp to the painted area
        y = max(0.0, min(float(usable_h), y))

        top_ratio = y / float(usable_h) if usable_h else 0.0
        vbar.setValue(int(top_ratio * total))

    def _visible_block_span(self) -> tuple[int, int, int]:
        """Return (first_block_index, visible_block_count, total_block_count).

        Uses the editor's layout to count how many text blocks are currently
        visible inside the viewport, starting at firstVisibleBlock().
        """
        if not self.editor:
            return 0, 0, 0

        doc = self.editor.document()
        total_blocks = doc.blockCount()
        if total_blocks == 0:
            return 0, 0, 0

        layout: QtGui.QAbstractTextDocumentLayout = doc.documentLayout()
        viewport_h = self.editor.viewport().height()
        content_off_y = self.editor.contentOffset().y()

        block = self.editor.firstVisibleBlock()
        first_idx = block.blockNumber()

        # Position of this block's top inside the viewport coordinates
        # (translate by contentOffset).
        top_y = layout.blockBoundingRect(block).translated(0, content_off_y).top()

        visible = 0
        y = top_y
        cur = block
        while cur.isValid() and y < viewport_h:
            rect = layout.blockBoundingRect(cur)
            h = rect.height()
            # Guard against zero-height (can happen on empty docs/themes)
            if h <= 0:
                h = self.editor.fontMetrics().height()
            visible += 1
            y += h
            cur = cur.next()

        return first_idx, visible, total_blocks
