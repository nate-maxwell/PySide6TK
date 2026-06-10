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

    def paint(
        self,
        painter: QtGui.QPainter,
        option: QtWidgets.QStyleOptionGraphicsItem,
        widget: QtWidgets.QWidget | None = None,
    ) -> None:
        """
        Paint the comment box body, header, label, border, and resize handle.

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

        painter.fillRect(self._handle_rect(), QtGui.QBrush(self._border_color()))

    def mousePressEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        """
        Begin a resize drag if the press is in the handle, otherwise move.

        Args:
            event (QtWidgets.QGraphicsSceneMouseEvent): The mouse event.
        """
        if self._handle_rect().contains(event.pos()):
            self._resizing = True
            self._resize_origin = event.scenePos()
            self._resize_start_size = (self._box_width, self._box_height)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        """
        Update the box size during a resize drag.

        Args:
            event (QtWidgets.QGraphicsSceneMouseEvent): The mouse event.
        """
        if self._resizing:
            delta = event.scenePos() - self._resize_origin
            self.prepareGeometryChange()
            self._box_width = max(
                self._MIN_WIDTH, self._resize_start_size[0] + delta.x()
            )
            self._box_height = max(
                self._MIN_HEIGHT, self._resize_start_size[1] + delta.y()
            )
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
            event.accept()
        else:
            super().mouseReleaseEvent(event)
