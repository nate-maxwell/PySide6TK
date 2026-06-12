from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from typing import Any

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

from PySide6TK.Nodes.port import Port
from PySide6TK.Nodes.port import PortType


class FieldType(str, Enum):
    FLOAT = "float"
    INT = "int"
    STR = "str"
    BOOL = "bool"
    COLOR = "color"
    VEC2 = "vec2"
    VEC3 = "vec3"
    CHOICE = "choice"


@dataclass
class FieldDefinition(object):
    """
    Describes a single editable field on a node.

    Args:
        name (str): The field's identifier key.
        label (str): Human-readable display name.
        field_type (FieldType): The input type.
        default (Any): The default value for this field.
        options (list[str]): Valid choices when ``field_type`` is ``FieldType.CHOICE``.
        min_value (float | None): Minimum value for numeric fields.
        max_value (float | None): Maximum value for numeric fields.
    """

    name: str
    label: str
    field_type: FieldType
    default: Any = None
    options: list[str] = field(default_factory=list)
    min_value: float | None = None
    max_value: float | None = None


class BaseNode(QtWidgets.QGraphicsItem):
    """
    Base class for Nodes placed on a GraphView.

    Subclass this and implement ``_build`` to add ports using ``add_port`` and
    fields using ``add_field``. Fields can be queried via ``get_fields`` to
    build a properties panel, and their values read and written via
    ``get_field_value`` and ``set_field_value``.

    Args:
        title (str): Text displayed in the node header.
        width (int): Node width in pixels.
        body_height (int): Height of the body region below the header.
        parent (QtWidgets.QGraphicsItem | None): Optional parent item.

    Attributes:
        title (str): The node's display title.
        width (int): Node width.
        body_height (int): Body region height.

    Example:

        class BlurNode(BaseNode):
            def _build(self) -> None:
                self.port_in = self.add_port(PortType.INPUT, "image")
                self.port_out = self.add_port(PortType.OUTPUT, "image")
                self.add_field(FieldDefinition(
                    name="radius",
                    label="Radius",
                    field_type=FieldType.STR,
                    default=1.0,
                    min_value=0.0,
                    max_value=100.0,
                ))
                self.add_field(FieldDefinition(
                    name="quality",
                    label="Quality",
                    field_type=FieldType.CHOICE,
                    default="medium",
                    options=["low", "medium", "high"],
                ))
    """

    _HEADER_HEIGHT: int = 28
    _PORT_SPACING: int = 22
    _PORT_MARGIN: int = 10
    _CORNER_RADIUS: float = 6.0
    _COLOR_HEADER: QtGui.QColor = QtGui.QColor(60, 60, 180)
    _COLOR_BODY: QtGui.QColor = QtGui.QColor(50, 50, 50)
    _COLOR_BORDER: QtGui.QColor = QtGui.QColor(20, 20, 20)
    _COLOR_BORDER_SELECTED: QtGui.QColor = QtGui.QColor(255, 200, 0)
    _COLOR_TITLE: QtGui.QColor = QtGui.QColor(240, 240, 240)
    _COLOR_PORT_LABEL: QtGui.QColor = QtGui.QColor(180, 180, 180)

    def __init__(
        self,
        title: str,
        width: int = 180,
        body_height: int = 80,
        grid_size: int = 20,
        parent: QtWidgets.QGraphicsItem | None = None,
    ) -> None:
        super().__init__(parent)
        self.title = title
        self.width = width
        self.body_height = body_height
        self._grid_size = grid_size
        self._ports: list[Port] = []
        self._fields: dict[str, FieldDefinition] = {}
        self._field_values: dict[str, Any] = {}

        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setCacheMode(QtWidgets.QGraphicsItem.CacheMode.DeviceCoordinateCache)

        self._build()
        self._update_wires()

    def _build(self) -> None:
        """
        Override to add ports and fields to the node.

        Called once during ``__init__``. Use ``add_port`` to create ports,
        ``add_field`` to register fields, and ``self._HEADER_HEIGHT`` as the
        y offset for body content.
        """

    @property
    def total_height(self) -> int:
        """
        Total height of the node including header and body.

        Returns:
            int: Total height in pixels.
        """
        return self._HEADER_HEIGHT + self.body_height

    def add_port(self, port_type: str, name: str) -> Port:
        """
        Create and position a port on this node.

        Input ports are placed on the left edge, output ports on the right.
        Ports are stacked top-to-bottom in the order they are added.

        Args:
            port_type (str): Either ``PortType.INPUT`` or ``PortType.OUTPUT``.
            name (str): Display name for the port.
        Returns:
            Port: The created port.
        """
        input_count = sum(1 for p in self._ports if p.port_type == PortType.INPUT)
        output_count = sum(1 for p in self._ports if p.port_type == PortType.OUTPUT)

        port = Port(port_type, name, self)
        y = (
            self._HEADER_HEIGHT
            + self._PORT_MARGIN
            + (input_count if port_type == PortType.INPUT else output_count)
            * self._PORT_SPACING
        )

        x = 0 if port_type == PortType.INPUT else self.width
        port.setPos(x, y)
        self._ports.append(port)
        return port

    def add_field(self, definition: FieldDefinition) -> None:
        """
        Register a field on this node.

        Args:
            definition (FieldDefinition): The field definition to register.
        """
        self._fields[definition.name] = definition
        self._field_values[definition.name] = definition.default

    def get_fields(self) -> list[FieldDefinition]:
        """
        Return all field definitions in order of registration.

        Returns:
            list[FieldDefinition]: All registered field definitions.
        """
        return list(self._fields.values())

    def get_field_value(self, name: str) -> Any:
        """
        Return the current value of a field.

        Args:
            name (str): The field's identifier key.
        Returns:
            Any: The current value.
        """
        return self._field_values[name]

    def set_field_value(self, name: str, value: Any) -> None:
        """
        Set the value of a field.

        Args:
            name (str): The field's identifier key.
            value (Any): The new value.
        """
        if name not in self._fields:
            raise KeyError(f"No field '{name}' on node '{self.title}'.")
        self._field_values[name] = value

    def contains_field(self, field_name: str) -> bool:
        """
        Returns whether the node contains a field by the given field_name.

        Args:
            field_name (str): The name to look up.
        Returns:
            bool: Whether it exists in the node's fields.
        """
        return field_name in self._fields

    def input_ports(self) -> list[Port]:
        """
        Return all input ports on this node.

        Returns:
            list[Port]: Input ports in order of addition.
        """
        return [p for p in self._ports if p.port_type == PortType.INPUT]

    def output_ports(self) -> list[Port]:
        """
        Return all output ports on this node.

        Returns:
            list[Port]: Output ports in order of addition.
        """
        return [p for p in self._ports if p.port_type == PortType.OUTPUT]

    def connected_inputs(self) -> list[BaseNode]:
        """
        Return all Nodes feeding into this node's input ports.

        Returns:
            list[BaseNode]: Upstream connected Nodes.
        """
        nodes: list[BaseNode] = []
        for port in self.input_ports():
            for wire in port.wires:
                parent = wire.source.parentItem()
                if isinstance(parent, BaseNode):
                    nodes.append(parent)
        return nodes

    def connected_outputs(self) -> list[BaseNode]:
        """
        Return all Nodes this node's output ports feed into.

        Returns:
            list[BaseNode]: Downstream connected Nodes.
        """
        nodes: list[BaseNode] = []
        for port in self.output_ports():
            for wire in port.wires:
                if wire.target is not None:
                    parent = wire.target.parentItem()
                    if isinstance(parent, BaseNode):
                        nodes.append(parent)
        return nodes

    def _update_wires(self) -> None:
        for port in self._ports:
            for wire in port.wires:
                wire.update_path()

    def boundingRect(self) -> QtCore.QRectF:
        """
        Return the bounding rectangle of the node.

        Returns:
            QtCore.QRectF: The node's bounding rect.
        """
        return QtCore.QRectF(0, 0, self.width, self.total_height)

    def paint(
        self,
        painter: QtGui.QPainter,
        option: QtWidgets.QStyleOptionGraphicsItem,
        widget: QtWidgets.QWidget | None = None,
    ) -> None:
        """
        Paint the node header, body, border, and port labels.

        Args:
            painter (QtGui.QPainter): The painter.
            option (QtWidgets.QStyleOptionGraphicsItem): Style options.
            widget (QtWidgets.QWidget | None): Optional widget.
        """
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        rect = QtCore.QRectF(0, 0, self.width, self.total_height)

        body_path = QtGui.QPainterPath()
        body_path.addRoundedRect(rect, self._CORNER_RADIUS, self._CORNER_RADIUS)
        painter.fillPath(body_path, QtGui.QBrush(self._COLOR_BODY))

        header_rect = QtCore.QRectF(0, 0, self.width, self._HEADER_HEIGHT)
        header_path = QtGui.QPainterPath()
        header_path.addRoundedRect(
            header_rect, self._CORNER_RADIUS, self._CORNER_RADIUS
        )
        square_patch = QtCore.QRectF(
            0,
            self._CORNER_RADIUS,
            self.width,
            self._HEADER_HEIGHT - self._CORNER_RADIUS,
        )
        header_path.addRect(square_patch)
        painter.fillPath(header_path, QtGui.QBrush(self._COLOR_HEADER))

        painter.setPen(self._COLOR_TITLE)
        font = painter.font()
        font.setPointSize(9)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(
            QtCore.QRectF(8, 0, self.width - 16, self._HEADER_HEIGHT),
            QtCore.Qt.AlignmentFlag.AlignVCenter,
            self.title,
        )

        label_font = QtGui.QFont()
        label_font.setPointSize(8)
        painter.setFont(label_font)
        painter.setPen(self._COLOR_PORT_LABEL)

        for port in self._ports:
            py = port.pos().y()
            if port.port_type == PortType.INPUT:
                painter.drawText(
                    QtCore.QRectF(10, py - 8, self.width * 0.5, 16),
                    QtCore.Qt.AlignmentFlag.AlignVCenter
                    | QtCore.Qt.AlignmentFlag.AlignLeft,
                    port.name,
                )
            else:
                painter.drawText(
                    QtCore.QRectF(self.width * 0.5, py - 8, self.width * 0.5 - 10, 16),
                    QtCore.Qt.AlignmentFlag.AlignVCenter
                    | QtCore.Qt.AlignmentFlag.AlignRight,
                    port.name,
                )

        border_pen = QtGui.QPen(
            self._COLOR_BORDER_SELECTED if self.isSelected() else self._COLOR_BORDER
        )
        border_pen.setWidth(2)
        painter.setPen(border_pen)
        painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(rect, self._CORNER_RADIUS, self._CORNER_RADIUS)

    def itemChange(
        self,
        change: QtWidgets.QGraphicsItem.GraphicsItemChange,
        value: object,
    ) -> object:
        if change == QtWidgets.QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            point = value
            x = round(point.x() / self._grid_size) * self._grid_size
            y = round(point.y() / self._grid_size) * self._grid_size
            value = QtCore.QPointF(x, y)
        if change == QtWidgets.QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            self._update_wires()
        return super().itemChange(change, value)
