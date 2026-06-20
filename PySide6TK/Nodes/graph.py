from __future__ import annotations

import json
from collections import defaultdict

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

from PySide6TK.Nodes.node import BaseNode
from PySide6TK.Nodes.port import Port
from PySide6TK.Nodes.port import PortType
from PySide6TK.Nodes.wire import Wire
from PySide6TK.Nodes.wire import WireStyle
from PySide6TK.Nodes.comment import CommentBox
from PySide6TK.Nodes.commands import AddNodeCommand
from PySide6TK.Nodes.commands import AddCommentCommand
from PySide6TK.Nodes.commands import RemoveNodeCommand
from PySide6TK.Nodes.commands import ConnectPortsCommand
from PySide6TK.Nodes.commands import MoveNodeCommand
from PySide6TK.Nodes.commands import CommandStack
from PySide6TK.Nodes.serialize import serialize_nodes
from PySide6TK.Nodes.serialize import deserialize_nodes


class GraphView(QtWidgets.QGraphicsView):
    """
    A zoomable, pannable grid backdrop for a node graph.

    Owns a ``QGraphicsScene`` that Nodes are added to. Supports middle-mouse
    pan, scroll-wheel zoom, and a multi-level grid that scales with zoom.
    Right-clicking the background opens a context menu populated from
    ``node_registry``, allowing nodes to be created at the click position.

    Undo and Redo shortcuts can be mapped to GraphView.commands.undo / redo.
    The tracked commands are node creation, deletion, movement, comment box
    creation and deletion, and wire adjustment.

    Args:
        parent (QtWidgets.QWidget | None): Optional parent widget.

    Attributes:
        graph_scene (QtWidgets.QGraphicsScene): The scene Nodes are added to.
        node_registry (dict[str, list[type[BaseNode]]]): Map of category
            name to node types registered under that category.
        commands (CommandStack): The undo/redo command stack.
    """

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.grid_small: int = 20
        self.grid_large: int = 100
        self.color_bg: QtGui.QColor = QtGui.QColor(30, 30, 30)
        self.color_grid_small: QtGui.QColor = QtGui.QColor(45, 45, 45)
        self.color_grid_large: QtGui.QColor = QtGui.QColor(55, 55, 55)
        self.zoom_min: float = 0.1
        self.zoom_max: float = 4.0
        self.zoom_step: float = 0.12

        self.graph_scene = QtWidgets.QGraphicsScene(self)
        self.graph_scene.setSceneRect(-10000, -10000, 20000, 20000)
        self.setScene(self.graph_scene)

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
        self.setBackgroundBrush(QtGui.QBrush(self.color_bg))
        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)

        self._zoom: float = 1.0
        self._pan_active: bool = False
        self._pan_origin: QtCore.QPoint = QtCore.QPoint()
        self._drag_wire: Wire | None = None
        self._move_origins: dict[int, QtCore.QPointF] = {}

        self._node_refs: list[BaseNode] = []
        self.node_registry: dict[str, list[type[BaseNode]]] = defaultdict(list)
        self.comment_type: type[CommentBox] = CommentBox
        self.commands: CommandStack = CommandStack()

        self.customContextMenuRequested.connect(self._on_context_menu)

        self.wire_style = WireStyle.BEZIER

    def view_center(self) -> QtCore.QPointF:
        """
        Return the center of the current viewport in scene coordinates.

        Returns:
            QtCore.QPointF: The scene-space center of the visible viewport.
        """
        return self.mapToScene(self.viewport().rect().center())

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
        self.commands.push(AddCommentCommand(self, box, x, y))
        return box

    def register_node(self, category: str, node_type: type[BaseNode]) -> None:
        """
        Register a node type under a category for the right-click context menu.

        Args:
            category (str): The category name to group the node under.
            node_type (type[BaseNode]): The node class to register.
        """
        self.node_registry[category].append(node_type)

    def add_node(self, node: BaseNode, x: float, y: float) -> None:
        """
        Add a node to the scene at the given scene coordinates.

        Args:
            node (BaseNode): The node graphics item to add.
            x (float): Scene x position.
            y (float): Scene y position.
        """
        self.commands.push(AddNodeCommand(self, node, x, y))

    def remove_node(self, node: BaseNode) -> None:
        """
        Remove a node and all its connected wires from the scene.

        Args:
            node (BaseNode): The node graphics item to remove.
        """
        self.commands.push(RemoveNodeCommand(self, node))

    def connect_ports(self, source: Port, target: Port) -> None:
        """
        Create a wire between two ports and register it with both.

        Args:
            source (Port): The output port to connect from.
            target (Port): The input port to connect to.
        """
        self.commands.push(ConnectPortsCommand(self, source, target))

    def get_wires(self) -> list[Wire]:
        """
        Return all fully connected wires in the scene.

        Returns:
            list[Wire]: All connected wires.
        """
        return [
            item
            for item in self.graph_scene.items()
            if isinstance(item, Wire) and item.is_connected()
        ]

    def clear(self) -> None:
        """Removes all nodes, comments, and wires from the scene and resets state."""
        for item in list(self.graph_scene.items()):
            self.graph_scene.removeItem(item)

        self._node_refs.clear()
        self.commands.clear()
        self._move_origins.clear()
        self._drag_wire = None

    def set_wire_style(self, style: WireStyle) -> None:
        """Update all wires to the selected style."""
        Wire.style = style
        for wire in self.get_wires():
            wire.update_path()

    # -----Command tracking for undo/redo--------------------------------------

    def add_node_internal(self, node: BaseNode, x: float, y: float) -> None:
        self._node_refs.append(node)
        self.graph_scene.addItem(node)
        node.setPos(x, y)
        node._grid_size = self.grid_small

    def remove_node_internal(self, node: BaseNode) -> None:
        self.graph_scene.removeItem(node)
        if node in self._node_refs:
            self._node_refs.remove(node)

    def connect_ports_internal(self, source: Port, target: Port) -> Wire:
        wire = Wire(source, target)
        source.add_wire(wire)
        target.add_wire(wire)
        wire.update_path()
        self.graph_scene.addItem(wire)
        return wire

    # -------------------------------------------------------------------------

    def _on_context_menu(self, viewport_pos: QtCore.QPoint) -> None:
        item = self.itemAt(viewport_pos)
        if item is not None:
            return

        scene_pos = self.mapToScene(viewport_pos)
        menu = QtWidgets.QMenu(self)

        comment_action = menu.addAction("Add Comment")
        comment_action.setData(("comment", scene_pos))
        menu.addSeparator()

        for category, node_types in sorted(self.node_registry.items()):
            submenu = menu.addMenu(category)
            for node_type in node_types:
                action = submenu.addAction(node_type.__name__)
                action.setData(("node", node_type, scene_pos))

        chosen = menu.exec(self.viewport().mapToGlobal(viewport_pos))
        if chosen is None:
            return

        data = chosen.data()
        if data[0] == "comment":
            self.add_comment(data[1].x(), data[1].y())
        elif data[0] == "node":
            node = data[1]()
            self.add_node(node, data[2].x(), data[2].y())

    def _port_at(self, scene_pos: QtCore.QPointF) -> Port | None:
        for item in self.graph_scene.items(scene_pos):
            if item is self._drag_wire:
                continue
            if isinstance(item, Port):
                return item
        return None

    def destroy_wire(self, wire: Wire) -> None:
        wire.source.remove_wire(wire)
        if wire.target:
            wire.target.remove_wire(wire)
        self.graph_scene.removeItem(wire)

    @staticmethod
    def _ports_of(node: object) -> list[Port]:
        return [c for c in node.childItems() if isinstance(c, Port)]

    def drawBackground(self, painter: QtGui.QPainter, rect: QtCore.QRectF) -> None:
        super().drawBackground(painter, rect)

        left = int(rect.left()) - (int(rect.left()) % self.grid_small)
        top = int(rect.top()) - (int(rect.top()) % self.grid_small)

        small_pen = QtGui.QPen(self.color_grid_small)
        small_pen.setCosmetic(True)
        large_pen = QtGui.QPen(self.color_grid_large)
        large_pen.setCosmetic(True)

        x = left
        while x < rect.right():
            pen = large_pen if x % self.grid_large == 0 else small_pen
            painter.setPen(pen)
            painter.drawLine(int(x), int(rect.top()), int(x), int(rect.bottom()))
            x += self.grid_small

        y = top
        while y < rect.bottom():
            pen = large_pen if y % self.grid_large == 0 else small_pen
            painter.setPen(pen)
            painter.drawLine(int(rect.left()), int(y), int(rect.right()), int(y))
            y += self.grid_small

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        delta = event.angleDelta().y()
        factor = 1 + self.zoom_step if delta > 0 else 1 - self.zoom_step
        new_zoom = self._zoom * factor
        if self.zoom_min <= new_zoom <= self.zoom_max:
            self._zoom = new_zoom
            self.scale(factor, factor)

    def delete_selected(self) -> None:
        for item in list(self.graph_scene.selectedItems()):
            if isinstance(item, BaseNode):
                self.remove_node(item)

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
                    for wire in list(port.wires):
                        self.destroy_wire(wire)
                    return
                self.setDragMode(QtWidgets.QGraphicsView.DragMode.NoDrag)
                self._drag_wire = Wire(port)
                self._drag_wire.reverse = port.port_type == PortType.INPUT
                self.graph_scene.addItem(self._drag_wire)
                self._drag_wire.update_path()
                return

            item = self.itemAt(event.position().toPoint())
            if item is None:
                self.setDragMode(QtWidgets.QGraphicsView.DragMode.RubberBandDrag)
            else:
                self.setDragMode(QtWidgets.QGraphicsView.DragMode.NoDrag)
                node = item if isinstance(item, BaseNode) else item.parentItem()
                if isinstance(node, BaseNode):
                    if event.modifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier:
                        node.setSelected(not node.isSelected())
                        return
                    if not node.isSelected():
                        self.graph_scene.clearSelection()
                        node.setSelected(True)
                    for selected in self.graph_scene.selectedItems():
                        n = (
                            selected
                            if isinstance(selected, BaseNode)
                            else selected.parentItem()
                        )
                        if isinstance(n, BaseNode):
                            self._move_origins[id(n)] = n.pos()

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

            self.graph_scene.removeItem(self._drag_wire)
            self._drag_wire = None

            if target_port is not None and drag_port.can_connect_to(target_port):
                source, target = (
                    (target_port, drag_port) if reverse else (drag_port, target_port)
                )

                if target.port_type == PortType.INPUT:
                    for wire in list(target.wires):
                        self.destroy_wire(wire)

                self.connect_ports(source, target)

            elif target_port is None:
                self._open_drop_menu(
                    event.position().toPoint(), scene_pos, drag_port, reverse
                )

            self.setDragMode(QtWidgets.QGraphicsView.DragMode.NoDrag)
            return

        if event.button() == QtCore.Qt.MouseButton.LeftButton and self._move_origins:
            for item in self.graph_scene.selectedItems():
                node = item if isinstance(item, BaseNode) else item.parentItem()
                if isinstance(node, BaseNode) and id(node) in self._move_origins:
                    old_pos = self._move_origins[id(node)]
                    new_pos = node.pos()
                    if old_pos != new_pos:
                        self.commands._undo_stack.append(
                            MoveNodeCommand(node, old_pos, new_pos)
                        )
            self._move_origins.clear()

        self.setDragMode(QtWidgets.QGraphicsView.DragMode.NoDrag)
        super().mouseReleaseEvent(event)

    def _open_drop_menu(
        self,
        viewport_pos: QtCore.QPoint,
        scene_pos: QtCore.QPointF,
        drag_port: Port,
        reverse: bool,
    ) -> None:
        menu = QtWidgets.QMenu(self)

        for category, node_types in sorted(self.node_registry.items()):
            submenu = menu.addMenu(category)
            for node_type in node_types:
                action = submenu.addAction(node_type.__name__)
                action.setData(node_type)

        chosen = menu.exec(self.viewport().mapToGlobal(viewport_pos))
        if chosen is None:
            return

        node_type = chosen.data()
        node = node_type()
        self.add_node(node, scene_pos.x(), scene_pos.y())

        candidate_ports = (
            node.input_ports()
            if drag_port.port_type == PortType.OUTPUT
            else node.output_ports()
        )
        if not candidate_ports:
            return

        target = candidate_ports[0]

        if reverse:
            source, target_final = target, drag_port
        else:
            source, target_final = drag_port, target

        if target_final.port_type == PortType.INPUT:
            for wire in list(target_final.wires):
                self.destroy_wire(wire)

        self.connect_ports(source, target_final)

    def copy_selected(self) -> None:
        """Copy selected nodes and the wires between them to the clipboard as JSON."""
        selected_nodes = [
            item
            for item in self.graph_scene.selectedItems()
            if isinstance(item, BaseNode)
        ]
        if not selected_nodes:
            return

        data = serialize_nodes(self, selected_nodes)
        QtGui.QGuiApplication.clipboard().setText(json.dumps(data))

    def paste_clipboard(self, x: float, y: float) -> None:
        """
        Paste nodes from the clipboard, offset so the first node lands at (x, y).

        Args:
            x (float): Scene x position for the first pasted node.
            y (float): Scene y position for the first pasted node.
        """
        text = QtGui.QGuiApplication.clipboard().text()
        if not text:
            return

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return

        if "nodes" not in data or not data["nodes"]:
            return

        deserialize_nodes(self, data, offset=(x, y))

    def cursor_scene_pos(self) -> tuple[float, float]:
        """
        Return the current cursor position in scene coordinates.

        Returns:
            tuple[float, float]: Scene-space x and y of the cursor.
        """
        viewport_pos = self.viewport().mapFromGlobal(QtGui.QCursor.pos())
        scene_pos = self.mapToScene(viewport_pos)
        return scene_pos.x(), scene_pos.y()
