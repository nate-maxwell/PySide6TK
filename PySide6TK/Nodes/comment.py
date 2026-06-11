from __future__ import annotations

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

from PySide6TK.Nodes.node import BaseNode
from PySide6TK.Nodes.node import FieldDefinition
from PySide6TK.Nodes.node import FieldType


class CommentBox(BaseNode):
    """
    A resizable comment box that sits behind nodes in the graph.

    Title and color are editable via the properties panel on double-click.
    Drag the bottom-right corner handle to resize.

    Args:
        label (str): The comment text displayed in the header.
        width (float): Initial width in pixels.
        height (float): Initial height in pixels.
        parent (QtWidgets.QGraphicsItem | None): Optional parent item.
    """

    _HEADER_HEIGHT: int = 24
    _HANDLE_SIZE: float = 12.0
    _CORNER_NONE = 0
    _CORNER_TOP_LEFT = 1
    _CORNER_TOP_RIGHT = 2
    _CORNER_BOTTOM_LEFT = 3
    _CORNER_BOTTOM_RIGHT = 4
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
        self._box_width = width
        self._box_height = height
        self._resizing = False
        self._resize_origin: QtCore.QPointF = QtCore.QPointF()
        self._resize_start_size: tuple[float, float] = (width, height)
        super().__init__(
            title=label, width=width, body_height=height - 24, parent=parent
        )
        self.setZValue(-2)

    def _build(self) -> None:
        self.add_field(
            FieldDefinition(
                name="label",
                label="Label",
                field_type=FieldType.STR,
                default=self.title,
            )
        )
        self.add_field(
            FieldDefinition(
                name="color",
                label="Color",
                field_type=FieldType.COLOR,
                default=(80, 80, 40, 180),
            )
        )

    def _header_color(self) -> QtGui.QColor:
        r, g, b, a = self.get_field_value("color")
        return QtGui.QColor(r, g, b, a)

    def _body_color(self) -> QtGui.QColor:
        r, g, b, a = self.get_field_value("color")
        return QtGui.QColor(r, g, b, max(0, a - 100))

    def _border_color(self) -> QtGui.QColor:
        r, g, b, _ = self.get_field_value("color")
        return QtGui.QColor(r, g, b, 200)

    def _handle_rect(self) -> QtCore.QRectF:
        return QtCore.QRectF(
            self._box_width - self._HANDLE_SIZE,
            self._box_height - self._HANDLE_SIZE,
            self._HANDLE_SIZE,
            self._HANDLE_SIZE,
        )

    def boundingRect(self) -> QtCore.QRectF:
        return QtCore.QRectF(0, 0, self._box_width, self._box_height)

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
            self.get_field_value("label"),
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
