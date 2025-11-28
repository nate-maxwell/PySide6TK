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
        """Draw the colored lines for each code block in the editor."""
        # Boy howdy are painter functions in qt ugly...

        inner_w = max(1, self.width() - 2 * self.margin)
        max_lines = max(0, self.height() // self.line_height)
        block = self.editor.document().firstBlock()

        painted = 0
        for i in range(max_lines):
            if not block.isValid():
                break

            y = i * self.line_height
            text = block.text()
            text_len = len(text)

            if text_len == 0:
                painter.fillRect(
                    self.margin,
                    y,
                    inner_w,
                    self.line_height - 1,
                    QtGui.QColor('#2a2a2a')
                )
            else:
                layout = block.layout()
                runs = layout.formats()
                if runs:
                    denom = max(1, text_len)
                    for run in runs:
                        start = max(0, run.start)
                        length = max(0, run.length)
                        if length == 0:
                            continue
                        x0_ratio = start / denom
                        x1_ratio = min(1.0, (start + length) / denom)
                        x = self.margin + int(x0_ratio * inner_w)
                        w = max(1, int((x1_ratio - x0_ratio) * inner_w))
                        color = run.format.foreground().color()
                        if not color.isValid():
                            color = QtGui.QColor('#666')
                        painter.fillRect(x, y, w, self.line_height - 1, color)
                else:
                    painter.fillRect(
                        self.margin, y, inner_w,
                        self.line_height - 1,
                        QtGui.QColor('#666')
                    )

            painted += 1
            block = block.next()

        # Fill any remaining minimap rows with faint bars so bottom isn't blank
        for i in range(painted, max_lines):
            y = i * self.line_height
            painter.fillRect(
                self.margin,
                y,
                inner_w,
                self.line_height - 1,
                QtGui.QColor('#2a2a2a')
            )

    def _draw_view_area(self, painter: QtGui.QPainter) -> None:
        """Draws a green square on the minimap corresponding to the viewed
        lines of code.
        """
        vbar = self.editor.verticalScrollBar()
        page = max(1, vbar.pageStep())  # visible portion (scrollbar units)
        maximum = max(0, vbar.maximum())
        total = page + maximum

        top_ratio = (vbar.value() / total) if total else 0.0
        height_ratio = (page / total) if total else 1.0

        # IMPORTANT: scale to the actual painted area height, not full widget
        max_lines = max(0, self.height() // self.line_height)
        usable_h = max_lines * self.line_height
        inner_w = max(1, self.width() - 2 * self.margin)

        # Minimum height
        h = max(2, int(height_ratio * usable_h))
        y = int(top_ratio * usable_h)

        # Clamp to painted area to prevent overrun
        if y + h > usable_h:
            y = max(0, usable_h - h)

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
