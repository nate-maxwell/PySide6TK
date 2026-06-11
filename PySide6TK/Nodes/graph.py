from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Callable

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

from PySide6TK.Nodes.commands import CommandStack
from PySide6TK.Nodes.comment import CommentBox
from PySide6TK.Nodes.graph_data import Graph
from PySide6TK.Nodes.graph_data import NodeData
from PySide6TK.Nodes.graph_data import PortData
from PySide6TK.Nodes.port import Port
from PySide6TK.Nodes.port import PortType
from PySide6TK.Nodes.wire import Wire


@dataclass
class NodeRegistryEntry(object):
    """
    An entry in the node registry mapping a type name to a widget class.

    Args:
        widget_class (type[NodeWidget]): The widget class to instantiate.
        category (str): Context menu category.
        label (str): Display name in the context menu.
        factory (Callable[[Graph, str], None] | None): Optional function called
            after the node is added to set up its ports and default fields.
            Receives the graph and the new node_id.
    """

    widget_class: type[NodeWidget]
    category: str
    label: str


class NodeWidget(QtWidgets.QGraphicsItem):
    """
    A QGraphicsItem that renders a node from a NodeData instance.

    Args:
        node_data (NodeData): The data node this widget represents.
        graph (Graph): The data graph, used to write back changes.
        grid_size (int): Grid snap size.
        width (int): Node width in pixels.
        body_height (int): Body region height in pixels.
        parent (QtWidgets.QGraphicsItem | None): Optional parent item.

    Attributes:
        node_data (NodeData): The backing data node.
        ports (dict[str, Port]): Port widgets keyed by port id.
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
        node_data: NodeData,
        graph: Graph,
        grid_size: int = 20,
        width: int = 180,
        body_height: int = 80,
        parent: QtWidgets.QGraphicsItem | None = None,
    ) -> None:
        super().__init__(parent)
        self.node_data = node_data
        self._graph = graph
        self._grid_size = grid_size
        self._width = int(node_data.width) if node_data.width is not None else width
        self._body_height = (
            int(node_data.height) - self._HEADER_HEIGHT
            if node_data.height is not None
            else body_height
        )
        self.ports: dict[str, Port] = {}
        self.on_double_click: list[Callable[[NodeData], None]] = []

        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setCacheMode(QtWidgets.QGraphicsItem.CacheMode.NoCache)

    @property
    def width(self) -> int:
        """
        Node width in pixels.

        Returns:
            int: Width.
        """
        return self._width

    @property
    def body_height(self) -> int:
        """
        Body region height in pixels.

        Returns:
            int: Body height.
        """
        return self._body_height

    @property
    def total_height(self) -> int:
        """
        Total height including header and body.

        Returns:
            int: Total height.
        """
        return self._HEADER_HEIGHT + self._body_height

    def _build_ports(self) -> None:
        input_count = 0
        output_count = 0
        for port_id, port_data in self.node_data.ports.items():
            is_input = port_data.port_type == PortType.INPUT
            count = input_count if is_input else output_count
            y = self._HEADER_HEIGHT + self._PORT_MARGIN + count * self._PORT_SPACING
            x = 0 if is_input else self._width
            port = Port(port_data.port_type, port_data.name, self)
            port.setPos(x, y)
            port.port_id = port_id
            self.ports[port_id] = port
            if is_input:
                input_count += 1
            else:
                output_count += 1

    def _update_wires(self) -> None:
        for port in self.ports.values():
            for wire in port.wires:
                wire.update_path()

    def boundingRect(self) -> QtCore.QRectF:
        """
        Return the bounding rectangle of the node.

        Returns:
            QtCore.QRectF: The node's bounding rect.
        """
        return QtCore.QRectF(0, 0, self._width, self.total_height)

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
        rect = QtCore.QRectF(0, 0, self._width, self.total_height)

        body_path = QtGui.QPainterPath()
        body_path.addRoundedRect(rect, self._CORNER_RADIUS, self._CORNER_RADIUS)
        painter.fillPath(body_path, QtGui.QBrush(self._COLOR_BODY))

        header_rect = QtCore.QRectF(0, 0, self._width, self._HEADER_HEIGHT)
        header_path = QtGui.QPainterPath()
        header_path.addRoundedRect(
            header_rect, self._CORNER_RADIUS, self._CORNER_RADIUS
        )
        square_patch = QtCore.QRectF(
            0,
            self._CORNER_RADIUS,
            self._width,
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
            QtCore.QRectF(8, 0, self._width - 16, self._HEADER_HEIGHT),
            QtCore.Qt.AlignmentFlag.AlignVCenter,
            self.node_data.title,
        )

        label_font = QtGui.QFont()
        label_font.setPointSize(8)
        painter.setFont(label_font)
        painter.setPen(self._COLOR_PORT_LABEL)

        for port_id, port in self.ports.items():
            port_data = self.node_data.ports[port_id]
            py = port.pos().y()
            if port_data.port_type == PortType.INPUT:
                painter.drawText(
                    QtCore.QRectF(10, py - 8, self._width * 0.5, 16),
                    QtCore.Qt.AlignmentFlag.AlignVCenter
                    | QtCore.Qt.AlignmentFlag.AlignLeft,
                    port_data.name,
                )
            else:
                painter.drawText(
                    QtCore.QRectF(
                        self._width * 0.5, py - 8, self._width * 0.5 - 10, 16
                    ),
                    QtCore.Qt.AlignmentFlag.AlignVCenter
                    | QtCore.Qt.AlignmentFlag.AlignRight,
                    port_data.name,
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
            pos = self.pos()
            self._graph.move_node(self.node_data.node_id, pos.x(), pos.y())
        return super().itemChange(change, value)

    def mouseDoubleClickEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:
        """
        Fire all registered double-click callbacks with this widget's node data.

        Args:
            event (QtWidgets.QGraphicsSceneMouseEvent): The mouse event.
        """
        for cb in self.on_double_click:
            cb(self.node_data)
        super().mouseDoubleClickEvent(event)


class GraphView(QtWidgets.QGraphicsView):
    """
    A view over a Graph data instance.

    Reacts to callbacks from the graph and creates or destroys widgets
    accordingly. The graph is the source of truth; this class only renders it.

    Args:
        graph (Graph): The data graph to render.
        parent (QtWidgets.QWidget | None): Optional parent widget.

    Attributes:
        graph (Graph): The backing data graph.
        node_registry (dict[str, NodeRegistryEntry]): Map of node type name
            to registry entry.
        comment_type (type[CommentBox]): Comment box class to instantiate.
        commands (CommandStack): The undo/redo command stack.
        on_node_double_click (list[Callable[[NodeData], None]]): Callbacks
            fired when a node widget is double-clicked.
    """

    _GRID_SMALL: int = 20
    _GRID_LARGE: int = 100
    _COLOR_BG: QtGui.QColor = QtGui.QColor(30, 30, 30)
    _COLOR_GRID_SMALL: QtGui.QColor = QtGui.QColor(45, 45, 45)
    _COLOR_GRID_LARGE: QtGui.QColor = QtGui.QColor(55, 55, 55)
    _ZOOM_MIN: float = 0.1
    _ZOOM_MAX: float = 4.0
    _ZOOM_STEP: float = 0.12

    def __init__(
        self,
        graph: Graph,
        parent: QtWidgets.QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.graph = graph
        self.scene = QtWidgets.QGraphicsScene(self)
        self.scene.setSceneRect(-10000, -10000, 20000, 20000)
        self.setScene(self.scene)

        self.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        self.setViewportUpdateMode(
            QtWidgets.QGraphicsView.ViewportUpdateMode.FullViewportUpdate
        )
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setTransformationAnchor(
            QtWidgets.QGraphicsView.ViewportAnchor.AnchorUnderMouse
        )
        self.setDragMode(QtWidgets.QGraphicsView.DragMode.NoDrag)
        self.setBackgroundBrush(QtGui.QBrush(self._COLOR_BG))
        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)

        self._zoom: float = 1.0
        self._pan_active: bool = False
        self._pan_origin: QtCore.QPoint = QtCore.QPoint()
        self._drag_wire: Wire | None = None
        self._move_origins: dict[str, QtCore.QPointF] = {}

        self._node_widgets: dict[str, NodeWidget] = {}
        self._wire_widgets: dict[frozenset[str], Wire] = {}
        self._node_refs: list[NodeWidget | CommentBox] = []

        self.node_registry: dict[str, NodeRegistryEntry] = {}
        self.comment_type: type[CommentBox] = CommentBox
        self.commands: CommandStack = CommandStack()
        self.on_node_double_click: list[Callable[[NodeData], None]] = []

        self.customContextMenuRequested.connect(self._on_context_menu)

        graph.on_node_added.append(self._on_node_added)
        graph.on_node_removed.append(self._on_node_removed)
        graph.on_port_added.append(self._on_port_added)
        graph.on_ports_connected.append(self._on_ports_connected)
        graph.on_ports_disconnected.append(self._on_ports_disconnected)

    def register_node(
        self,
        node_type: str,
        widget_class: type[NodeWidget],
        category: str = "Nodes",
        label: str | None = None,
    ) -> None:
        """
        Register a node type for use in the context menu and view.

        Args:
            node_type (str): The type name string matching NodeData.node_type.
            widget_class (type[NodeWidget]): The widget class to instantiate.
            category (str): Context menu category.
            label (str | None): Display name in the menu. Defaults to node_type.
        """
        self.node_registry[node_type] = NodeRegistryEntry(
            widget_class=widget_class,
            category=category,
            label=label or node_type,
        )

    def view_center(self) -> tuple[float, float]:
        """
        Return the center of the current viewport in scene coordinates.

        Returns:
            tuple[float, float]: Scene-space x and y of the viewport center.
        """
        center = self.mapToScene(self.viewport().rect().center())
        return center.x(), center.y()

    def add_comment(self, x: float, y: float, label: str = "Comment") -> CommentBox:
        """
        Add a comment box to the scene at the given scene coordinates.

        Args:
            x (float): Scene x position.
            y (float): Scene y position.
            label (str): Initial comment label.
        Returns:
            CommentBox: The created comment box.
        """
        box = self.comment_type(label)
        self._node_refs.append(box)
        self.scene.addItem(box)
        box.setPos(x, y)
        return box

    def get_wires(self) -> list[Wire]:
        """
        Return all fully connected wires in the scene.

        Returns:
            list[Wire]: All connected wires.
        """
        return list(self._wire_widgets.values())

    def _on_node_added(self, node: NodeData) -> None:
        entry = self.node_registry.get(node.node_type)
        widget_class = entry.widget_class if entry is not None else NodeWidget
        widget = widget_class(node, self.graph, self._GRID_SMALL)
        for cb in self.on_node_double_click:
            widget.on_double_click.append(cb)
        self._node_widgets[node.node_id] = widget
        self._node_refs.append(widget)
        self.scene.addItem(widget)
        widget.setPos(node.x, node.y)

    def _on_node_removed(self, node_id: str) -> None:
        widget = self._node_widgets.pop(node_id, None)
        if widget is None:
            return
        self.scene.removeItem(widget)
        if widget in self._node_refs:
            self._node_refs.remove(widget)

    def _on_port_added(self, port_data: PortData) -> None:
        widget = self._node_widgets.get(port_data.node_id)
        if widget is None:
            return
        node_data = self.graph.nodes[port_data.node_id]
        is_input = port_data.port_type == PortType.INPUT
        count = sum(
            1
            for p in node_data.ports.values()
            if p.port_type == port_data.port_type and p.port_id != port_data.port_id
        )
        y = widget._HEADER_HEIGHT + widget._PORT_MARGIN + count * widget._PORT_SPACING
        x = 0 if is_input else widget._width

        port = Port(port_data.port_type, port_data.name, widget)
        port.setPos(x, y)
        port.port_id = port_data.port_id
        widget.ports[port_data.port_id] = port
        widget.prepareGeometryChange()
        widget.update()

    def _on_ports_connected(self, source_port_id: str, target_port_id: str) -> None:
        key = frozenset({source_port_id, target_port_id})
        if key in self._wire_widgets:
            return
        source_data = self.graph._find_port(source_port_id)
        target_data = self.graph._find_port(target_port_id)
        if source_data is None or target_data is None:
            return
        if source_data.port_type == "input":
            source_port_id, target_port_id = target_port_id, source_port_id
        source_port = self._find_port_widget(source_port_id)
        target_port = self._find_port_widget(target_port_id)
        if source_port is None or target_port is None:
            return
        wire = Wire(source_port, target_port)
        wire.update_path()
        self.scene.addItem(wire)
        source_port.add_wire(wire)
        target_port.add_wire(wire)
        self._wire_widgets[key] = wire

    def _on_ports_disconnected(self, port_id_a: str, port_id_b: str) -> None:
        key = frozenset({port_id_a, port_id_b})
        wire = self._wire_widgets.pop(key, None)
        if wire is not None:
            wire.source.remove_wire(wire)
            if wire.target:
                wire.target.remove_wire(wire)
            self.scene.removeItem(wire)

    def _find_port_widget(self, port_id: str) -> Port | None:
        for widget in self._node_widgets.values():
            if port_id in widget.ports:
                return widget.ports[port_id]
        return None

    def _port_at(self, scene_pos: QtCore.QPointF) -> Port | None:
        for item in self.scene.items(scene_pos):
            if item is self._drag_wire:
                continue
            if isinstance(item, Port):
                return item
        return None

    def _port_data_for_widget(self, port_widget: Port) -> PortData | None:
        port_id = getattr(port_widget, "port_id", None)
        if port_id is None:
            return None
        return self.graph._find_port(port_id)

    def _delete_selected(self) -> None:
        for item in list(self.scene.selectedItems()):
            if isinstance(item, NodeWidget):
                self.graph.remove_node(item.node_data.node_id)
            elif isinstance(item, CommentBox):
                self.scene.removeItem(item)
                if item in self._node_refs:
                    self._node_refs.remove(item)

    def _on_context_menu(self, viewport_pos: QtCore.QPoint) -> None:
        item = self.itemAt(viewport_pos)
        if item is not None:
            return

        scene_pos = self.mapToScene(viewport_pos)
        menu = QtWidgets.QMenu(self)

        comment_action = menu.addAction("Add Comment")
        comment_action.setData(("comment", scene_pos))
        menu.addSeparator()

        by_category: dict[str, list[tuple[str, str]]] = defaultdict(list)
        for node_type, entry in self.node_registry.items():
            by_category[entry.category].append((node_type, entry.label))

        for category, entries in sorted(by_category.items()):
            submenu = menu.addMenu(category)
            for node_type, label in entries:
                action = submenu.addAction(label)
                action.setData(("node", node_type, scene_pos))

        chosen = menu.exec(self.viewport().mapToGlobal(viewport_pos))
        if chosen is None:
            return

        data = chosen.data()
        if data[0] == "comment":
            self.add_comment(data[1].x(), data[1].y())
        elif data[0] == "node":
            node_type = data[1]
            pos = data[2]
            self.graph.add_node_of_type(node_type, pos.x(), pos.y())

    def drawBackground(self, painter: QtGui.QPainter, rect: QtCore.QRectF) -> None:
        super().drawBackground(painter, rect)

        left = int(rect.left()) - (int(rect.left()) % self._GRID_SMALL)
        top = int(rect.top()) - (int(rect.top()) % self._GRID_SMALL)

        small_pen = QtGui.QPen(self._COLOR_GRID_SMALL)
        small_pen.setCosmetic(True)
        large_pen = QtGui.QPen(self._COLOR_GRID_LARGE)
        large_pen.setCosmetic(True)

        x = left
        while x < rect.right():
            pen = large_pen if x % self._GRID_LARGE == 0 else small_pen
            painter.setPen(pen)
            painter.drawLine(int(x), int(rect.top()), int(x), int(rect.bottom()))
            x += self._GRID_SMALL

        y = top
        while y < rect.bottom():
            pen = large_pen if y % self._GRID_LARGE == 0 else small_pen
            painter.setPen(pen)
            painter.drawLine(int(rect.left()), int(y), int(rect.right()), int(y))
            y += self._GRID_SMALL

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        delta = event.angleDelta().y()
        factor = 1 + self._ZOOM_STEP if delta > 0 else 1 - self._ZOOM_STEP
        new_zoom = self._zoom * factor
        if self._ZOOM_MIN <= new_zoom <= self._ZOOM_MAX:
            self._zoom = new_zoom
            self.scale(factor, factor)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        scene_pos = self.mapToScene(event.position().toPoint())

        if event.button() == QtCore.Qt.MouseButton.MiddleButton:
            self._pan_active = True
            self._pan_origin = event.position().toPoint()
            self.setCursor(QtCore.Qt.CursorShape.ClosedHandCursor)
            return

        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            port = self._port_at(scene_pos)
            if port is not None:
                if event.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier:
                    port_data = self._port_data_for_widget(port)
                    if port_data is not None:
                        for connected_id in list(port_data.connections):
                            self.graph.disconnect_ports(port_data.port_id, connected_id)
                    return
                self.setDragMode(QtWidgets.QGraphicsView.DragMode.NoDrag)
                self._drag_wire = Wire(port)
                self._drag_wire.reverse = port.port_type == PortType.INPUT
                self.scene.addItem(self._drag_wire)
                self._drag_wire.update_path()
                return

            item = self.itemAt(event.position().toPoint())
            if item is None:
                self.setDragMode(QtWidgets.QGraphicsView.DragMode.RubberBandDrag)
            else:
                self.setDragMode(QtWidgets.QGraphicsView.DragMode.NoDrag)
                node_widget = (
                    item if isinstance(item, NodeWidget) else item.parentItem()
                )
                if isinstance(node_widget, NodeWidget):
                    self._move_origins[node_widget.node_data.node_id] = (
                        node_widget.pos()
                    )

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        scene_pos = self.mapToScene(event.position().toPoint())

        if self._pan_active:
            delta = event.position().toPoint() - self._pan_origin
            self._pan_origin = event.position().toPoint()
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x()
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y()
            )
            return

        if self._drag_wire is not None:
            self._drag_wire.set_drag_end(scene_pos)
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        scene_pos = self.mapToScene(event.position().toPoint())

        if event.button() == QtCore.Qt.MouseButton.MiddleButton:
            self._pan_active = False
            self.setCursor(QtCore.Qt.CursorShape.ArrowCursor)
            return

        if (
            event.button() == QtCore.Qt.MouseButton.LeftButton
            and self._drag_wire is not None
        ):
            target_port = self._port_at(scene_pos)
            drag_port = self._drag_wire.source
            reverse = getattr(self._drag_wire, "reverse", False)

            self.scene.removeItem(self._drag_wire)
            self._drag_wire = None

            if target_port is not None and drag_port.can_connect_to(target_port):
                source_port, target_port_final = (
                    (target_port, drag_port) if reverse else (drag_port, target_port)
                )
                source_data = self._port_data_for_widget(source_port)
                target_data = self._port_data_for_widget(target_port_final)
                if source_data is not None and target_data is not None:
                    self.graph.connect_ports(source_data.port_id, target_data.port_id)

            self.setDragMode(QtWidgets.QGraphicsView.DragMode.NoDrag)
            return

        if event.button() == QtCore.Qt.MouseButton.LeftButton and self._move_origins:
            self._move_origins.clear()

        self.setDragMode(QtWidgets.QGraphicsView.DragMode.NoDrag)
        super().mouseReleaseEvent(event)
