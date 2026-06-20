from enum import Enum

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

from PySide6TK.Nodes.port import Port


class WireStyle(Enum):
    BEZIER = "bezier"
    RIGHT_ANGLE = "right_angle"


class Wire(QtWidgets.QGraphicsPathItem):
    """
    A Bézier curve connecting two ports.

    Can be fully connected (source + target) or dangling (source only),
    in which case ``set_drag_end`` drives the free end during drag.
    The wire's color is derived from the source port's ``color`` attribute,
    allowing the application to communicate data type visually.

    Args:
        source (Port): The output port the wire originates from.
        target (Port | None): The input port to connect to, or None if dangling.

    Attributes:
        source (Port): The originating port.
        target (Port | None): The destination port, or None if not yet connected.
    """

    _COLOR_FALLBACK: QtGui.QColor = QtGui.QColor(200, 200, 200)
    _COLOR_INVALID: QtGui.QColor = QtGui.QColor(220, 80, 80)
    _WIDTH: float = 2.0

    style = WireStyle.BEZIER

    def __init__(
        self,
        source: Port,
        target: Port | None = None,
    ) -> None:
        super().__init__()
        self.source = source
        self.target = target
        self._drag_end: QtCore.QPointF = source.center_scene_pos()

        pen = QtGui.QPen(self._wire_color(), self._WIDTH)
        pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
        self.setPen(pen)
        self.setZValue(-1)
        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)

    def _wire_color(self) -> QtGui.QColor:
        """
        Resolve the wire color from the source port.

        Returns:
            QtGui.QColor: The source port's color, or the fallback color if
                the source port has no color attribute set.
        """
        if self.source is not None and hasattr(self.source, "color"):
            return self.source.color
        return self._COLOR_FALLBACK

    def refresh_color(self) -> None:
        """
        Re-read the source port's color and update the wire's pen.

        Call this after the source port's color has been changed externally,
        e.g. after the application assigns a data-type color to the port.
        """
        pen = self.pen()
        pen.setColor(self._wire_color())
        self.setPen(pen)
        self.update()

    def set_drag_end(self, pos: QtCore.QPointF) -> None:
        """
        Update the free end of a dangling wire during drag.

        Args:
            pos (QtCore.QPointF): Scene position of the drag cursor.
        """
        self._drag_end = pos
        self.update_path()

    def update_path(self) -> None:
        """Recompute the bezier path between source and target (or drag end)."""
        if getattr(self, "reverse", False):
            start = self._drag_end
            end = self.source.center_scene_pos()
        else:
            start = self.source.center_scene_pos()
            end = self.target.center_scene_pos() if self.target else self._drag_end

        path = QtGui.QPainterPath(start)

        if Wire.style == WireStyle.RIGHT_ANGLE:
            mid_x = (start.x() + end.x()) / 2.0
            path.lineTo(QtCore.QPointF(mid_x, start.y()))
            path.lineTo(QtCore.QPointF(mid_x, end.y()))
            path.lineTo(end)
        elif Wire.style == WireStyle.BEZIER:
            dx = abs(end.x() - start.x()) * 0.5
            ctrl1 = QtCore.QPointF(start.x() + dx, start.y())
            ctrl2 = QtCore.QPointF(end.x() - dx, end.y())
            path.cubicTo(ctrl1, ctrl2, end)
        else:
            raise ValueError(f"Unsupported wire style {str(Wire.style)}")

        self.setPath(path)

    def is_connected(self) -> bool:
        """Return whether the wire has both a source and a target."""
        return self.target is not None
