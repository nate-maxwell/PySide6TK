from __future__ import annotations

from typing import Any
from typing import Callable

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets


class CommentBox(QtWidgets.QGraphicsItem):
    """
    A resizable comment box that sits behind nodes in the graph.

    Label and color are plain attributes edited via ``on_double_click``
    callbacks. Drag any corner handle to resize.

    Args:
        label (str): The comment text displayed in the header.
        width (int): Initial width in pixels.
        height (int): Initial height in pixels.
        parent (QtWidgets.QGraphicsItem | None): Optional parent item.

    Attributes:
        label (str): The comment text.
        color (tuple[int, int, int, int]): RGBA header color.
        on_double_click (list[Callable[[CommentBox], None]]): Callbacks fired
            when the comment box is double-clicked.
    """

    _HEADER_HEIGHT: int = 24
    _HANDLE_SIZE: float = 12.0
    _CORNER_NONE: int = 0
    _CORNER_TOP_LEFT: int = 1
    _CORNER_TOP_RIGHT: int = 2
    _CORNER_BOTTOM_LEFT: int = 3
    _CORNER_BOTTOM_RIGHT: int = 4
    _CORNER_RADIUS: float = 6.0
    _MIN_WIDTH: float = 120.0
    _MIN_HEIGHT: float = 60.0
    _COLOR_BORDER_SELECTED: QtGui.QColor = QtGui.QColor(255, 220, 80)

    def __init__(
        self,
        label: str = "Comment",
        width: int = 240,
        height: int = 160,
        parent: QtWidgets.QGraphicsItem | None = None,
    ) -> None:
        super().__init__(parent)
        self.label: str = label
        self.color: tuple[int, int, int, int] = (80, 80, 40, 180)
        self.on_double_click: list[Callable[[CommentBox], None]] = []

        self._box_width: float = float(width)
        self._box_height: float = float(height)
        self._resizing: bool = False
        self._resize_corner: int = self._CORNER_NONE
        self._resize_origin: QtCore.QPointF = QtCore.QPointF()
        self._resize_start_size: tuple[float, float] = (float(width), float(height))
        self._resize_start_pos: QtCore.QPointF = QtCore.QPointF()

        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setZValue(-2)

    def _header_color(self) -> QtGui.QColor:
        r, g, b, a = self.color
        return QtGui.QColor(r, g, b, a)

    def _body_color(self) -> QtGui.QColor:
        r, g, b, a = self.color
        return QtGui.QColor(r, g, b, max(0, a - 100))

    def _border_color(self) -> QtGui.QColor:
        r, g, b, _ = self.color
        return QtGui.QColor(r, g, b, 200)

    def _corner_rects(self) -> dict[int, QtCore.QRectF]:
        h = self._HANDLE_SIZE
        return {
            self._CORNER_TOP_LEFT: QtCore.QRectF(0, 0, h, h),
            self._CORNER_TOP_RIGHT: QtCore.QRectF(self._box_width - h, 0, h, h),
            self._CORNER_BOTTOM_LEFT: QtCore.QRectF(0, self._box_height - h, h, h),
            self._CORNER_BOTTOM_RIGHT: QtCore.QRectF(
                self._box_width - h, self._box_height - h, h, h
            ),
        }

    def _corner_at(self, pos: QtCore.QPointF) -> int:
        for corner, rect in self._corner_rects().items():
            if rect.contains(pos):
                return corner
        return self._CORNER_NONE

    def boundingRect(self) -> QtCore.QRectF:
        """
        Return the bounding rectangle of the comment box.

        Returns:
            QtCore.QRectF: The bounding rect.
        """
        return QtCore.QRectF(0, 0, self._box_width, self._box_height)

    def paint(
        self,
        painter: QtGui.QPainter,
        option: QtWidgets.QStyleOptionGraphicsItem,
        widget: QtWidgets.QWidget | None = None,
    ) -> None:
        """
        Paint the comment box body, header, label, border, and resize handles.

        Args:
            painter (QtGui.QPainter): The painter.
            option (QtWidgets.QStyleOptionGraphicsItem): Style options.
            widget (QtWidgets.QWidget | None): Optional widget.
        """
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        rect = QtCore.QRectF(0, 0, self._box_width, self._box_height)

        body_path = QtGui.QPainterPath()
        body_path.addRoundedRect(rect, self._CORNER_RADIUS, self._CORNER_RADIUS)
        painter.fillPath(body_path, QtGui.QBrush(self._body_color()))

        header_rect = QtCore.QRectF(0, 0, self._box_width, self._HEADER_HEIGHT)
        header_path = QtGui.QPainterPath()
        header_path.addRoundedRect(
            header_rect, self._CORNER_RADIUS, self._CORNER_RADIUS
        )
        square_patch = QtCore.QRectF(
            0,
            self._CORNER_RADIUS,
            self._box_width,
            self._HEADER_HEIGHT - self._CORNER_RADIUS,
        )
        header_path.addRect(square_patch)
        painter.fillPath(header_path, QtGui.QBrush(self._header_color()))

        painter.setPen(QtGui.QColor(240, 240, 180))
        font = painter.font()
        font.setPointSize(9)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(
            QtCore.QRectF(8, 0, self._box_width - 16, self._HEADER_HEIGHT),
            QtCore.Qt.AlignmentFlag.AlignVCenter,
            self.label,
        )

        border_pen = QtGui.QPen(
            self._COLOR_BORDER_SELECTED if self.isSelected() else self._border_color(),
            1.5,
        )
        painter.setPen(border_pen)
        painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(rect, self._CORNER_RADIUS, self._CORNER_RADIUS)

        if self.isSelected():
            for corner_rect in self._corner_rects().values():
                painter.fillRect(corner_rect, QtGui.QBrush(self._border_color()))

    def mouseDoubleClickEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        """
        Fire all registered double-click callbacks.

        Args:
            event (QtWidgets.QGraphicsSceneMouseEvent): The mouse event.
        """
        for cb in self.on_double_click:
            cb(self)
        super().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        """
        Begin a resize drag if the press is on a corner handle, otherwise move.

        Args:
            event (QtWidgets.QGraphicsSceneMouseEvent): The mouse event.
        """
        corner = self._corner_at(event.pos())
        if corner != self._CORNER_NONE:
            self._resizing = True
            self._resize_corner = corner
            self._resize_origin = event.scenePos()
            self._resize_start_size = (self._box_width, self._box_height)
            self._resize_start_pos = self.pos()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        """
        Update the box size and position during a resize drag.

        Args:
            event (QtWidgets.QGraphicsSceneMouseEvent): The mouse event.
        """
        if self._resizing:
            delta = event.scenePos() - self._resize_origin
            start_w, start_h = self._resize_start_size
            start_pos = self._resize_start_pos
            self.prepareGeometryChange()

            if self._resize_corner == self._CORNER_BOTTOM_RIGHT:
                self._box_width = max(self._MIN_WIDTH, start_w + delta.x())
                self._box_height = max(self._MIN_HEIGHT, start_h + delta.y())

            elif self._resize_corner == self._CORNER_BOTTOM_LEFT:
                new_w = max(self._MIN_WIDTH, start_w - delta.x())
                self._box_height = max(self._MIN_HEIGHT, start_h + delta.y())
                self.setPos(start_pos.x() + (start_w - new_w), start_pos.y())
                self._box_width = new_w

            elif self._resize_corner == self._CORNER_TOP_RIGHT:
                self._box_width = max(self._MIN_WIDTH, start_w + delta.x())
                new_h = max(self._MIN_HEIGHT, start_h - delta.y())
                self.setPos(start_pos.x(), start_pos.y() + (start_h - new_h))
                self._box_height = new_h

            elif self._resize_corner == self._CORNER_TOP_LEFT:
                new_w = max(self._MIN_WIDTH, start_w - delta.x())
                new_h = max(self._MIN_HEIGHT, start_h - delta.y())
                self.setPos(
                    start_pos.x() + (start_w - new_w),
                    start_pos.y() + (start_h - new_h),
                )
                self._box_width = new_w
                self._box_height = new_h

            self.update()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        """
        End a resize drag.

        Args:
            event (QtWidgets.QGraphicsSceneMouseEvent): The mouse event.
        """
        if self._resizing:
            self._resizing = False
            self._resize_corner = self._CORNER_NONE
            event.accept()
        else:
            super().mouseReleaseEvent(event)
