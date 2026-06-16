from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6TK.Nodes.wire import Wire

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets


class PortType:
    INPUT: str = "input"
    OUTPUT: str = "output"


class Port(QtWidgets.QGraphicsEllipseItem):
    """
    A connection point on a node that wires can attach to.

    Args:
        port_type (str): Either ``PortType.INPUT`` or ``PortType.OUTPUT``.
        name (str): Display name for this port.
        data_type (str): The data type this port carries. Defaults to ``"any"``,
            which connects to any other type.
        parent (QtWidgets.QGraphicsItem | None): The parent node item.

    Attributes:
        port_type (str): Whether this is an input or output port.
        name (str): The port's display name.
        data_type (str): The type of data carried by this port.
        color (QtGui.QColor): The display color for this port and its wires.
            Defaults to the standard input/output color. Set by the application
            after construction to reflect data type.
        wires (list[Wire]): All wires currently connected to this port.
    """

    _RADIUS: int = 6
    _COLOR_INPUT: QtGui.QColor = QtGui.QColor(80, 180, 255)
    _COLOR_OUTPUT: QtGui.QColor = QtGui.QColor(255, 160, 40)
    _COLOR_HOVER: QtGui.QColor = QtGui.QColor(255, 255, 255)
    _COLOR_BORDER: QtGui.QColor = QtGui.QColor(20, 20, 20)

    def __init__(
        self,
        port_type: str,
        name: str,
        data_type: str = "any",
        parent: QtWidgets.QGraphicsItem | None = None,
    ) -> None:
        r = self._RADIUS
        super().__init__(-r, -r, r * 2, r * 2, parent)
        self.port_type = port_type
        self.name = name
        self.data_type = data_type
        self.wires: list[Wire] = []

        self.color: QtGui.QColor = (
            self._COLOR_INPUT if port_type == PortType.INPUT else self._COLOR_OUTPUT
        )
        self.setBrush(QtGui.QBrush(self.color))
        self.setPen(QtGui.QPen(self._COLOR_BORDER, 1.5))
        self.setAcceptHoverEvents(True)
        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        self.setZValue(1)

    def set_color(self, color: QtGui.QColor) -> None:
        """
        Set the port's display color and update the brush immediately.

        Args:
            color (QtGui.QColor): The new color for this port and its wires.
        """
        self.color = color
        self.setBrush(QtGui.QBrush(color))
        self.update()

    def center_scene_pos(self) -> QtCore.QPointF:
        """
        Return the port's center position in scene coordinates.

        Returns:
            QtCore.QPointF: Scene-space center of the port.
        """
        return self.scenePos()

    def can_connect_to(self, other: "Port") -> bool:
        """
        Return whether this port can connect to another port.

        Ports must be of opposite types and carry compatible data types.
        A data type of ``"any"`` is compatible with all other types.

        Args:
            other (Port): The candidate port.
        Returns:
            bool: True if connection is valid.
        """
        if self.port_type == other.port_type:
            return False
        if self.data_type == "any" or other.data_type == "any":
            return True
        return self.data_type == other.data_type

    def add_wire(self, wire: Wire) -> None:
        """
        Register a wire as connected to this port.

        Args:
            wire (Wire): The wire to register.
        """
        self.wires.append(wire)

    def remove_wire(self, wire: Wire) -> None:
        """
        Unregister a wire from this port.

        Args:
            wire (Wire): The wire to remove.
        """
        if wire in self.wires:
            self.wires.remove(wire)

    def hoverEnterEvent(self, event: QtWidgets.QGraphicsSceneHoverEvent) -> None:
        self.setBrush(QtGui.QBrush(self._COLOR_HOVER))
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event: QtWidgets.QGraphicsSceneHoverEvent) -> None:
        self.setBrush(QtGui.QBrush(self.color))
        super().hoverLeaveEvent(event)
