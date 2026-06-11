from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING

from PySide6 import QtCore

from PySide6TK.Nodes.graph_data import Graph
from PySide6TK.Nodes.graph_data import NodeData
from PySide6TK.Nodes.comment import CommentBox

if TYPE_CHECKING:
    from PySide6TK.Nodes.graph import GraphView


class Command(ABC):
    """Base class for undoable graph commands."""

    @abstractmethod
    def execute(self) -> None:
        """Execute the command."""

    @abstractmethod
    def undo(self) -> None:
        """Undo the command."""


class AddNodeCommand(Command):
    """
    Adds a node to the data graph.

    Args:
        graph (Graph): The data graph to operate on.
        node_type (str): The node type name.
        title (str): Display title.
        x (float): Scene x position.
        y (float): Scene y position.
        width (float | None): Optional width override.
        height (float | None): Optional height override.
    """

    def __init__(
        self,
        graph: Graph,
        node_type: str,
        title: str,
        x: float,
        y: float,
        width: float | None = None,
        height: float | None = None,
    ) -> None:
        self._graph = graph
        self._node_type = node_type
        self._title = title
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self._node: NodeData | None = None

    def execute(self) -> None:
        self._node = self._graph.add_node(
            node_type=self._node_type,
            title=self._title,
            x=self._x,
            y=self._y,
            width=self._width,
            height=self._height,
        )

    def undo(self) -> None:
        if self._node is not None:
            self._graph.remove_node(self._node.node_id)


class RemoveNodeCommand(Command):
    """
    Removes a node and all its connections from the data graph.

    Args:
        graph (Graph): The data graph to operate on.
        node (NodeData): The node to remove.
    """

    def __init__(self, graph: Graph, node: NodeData) -> None:
        self._graph = graph
        self._node = node
        self._x = node.x
        self._y = node.y
        self._severed_connections: list[tuple[str, str]] = []

    def execute(self) -> None:
        for port in self._node.ports.values():
            for connected_id in list(port.connections):
                self._severed_connections.append((port.port_id, connected_id))
        self._graph.remove_node(self._node.node_id)

    def undo(self) -> None:
        self._graph.nodes[self._node.node_id] = self._node
        self._node.x = self._x
        self._node.y = self._y
        for port in self._node.ports.values():
            port.connections.clear()
        for port_id_a, port_id_b in self._severed_connections:
            self._graph.connect_ports(port_id_a, port_id_b)
        self._graph._fire(self._graph.on_node_added, self._node)


class ConnectPortsCommand(Command):
    """
    Connects two ports in the data graph.

    Args:
        graph (Graph): The data graph to operate on.
        source_port_id (str): The output port id.
        target_port_id (str): The input port id.
    """

    def __init__(self, graph: Graph, source_port_id: str, target_port_id: str) -> None:
        self._graph = graph
        self._source_port_id = source_port_id
        self._target_port_id = target_port_id

    def execute(self) -> None:
        self._graph.connect_ports(self._source_port_id, self._target_port_id)

    def undo(self) -> None:
        self._graph.disconnect_ports(self._source_port_id, self._target_port_id)


class DisconnectPortsCommand(Command):
    """
    Disconnects two ports in the data graph.

    Args:
        graph (Graph): The data graph to operate on.
        port_id_a (str): One end of the connection.
        port_id_b (str): The other end of the connection.
    """

    def __init__(self, graph: Graph, port_id_a: str, port_id_b: str) -> None:
        self._graph = graph
        self._port_id_a = port_id_a
        self._port_id_b = port_id_b

    def execute(self) -> None:
        self._graph.disconnect_ports(self._port_id_a, self._port_id_b)

    def undo(self) -> None:
        self._graph.connect_ports(self._port_id_a, self._port_id_b)


class AddCommentCommand(Command):
    """
    Adds a comment box to the view.

    Args:
        view (GraphView): The graph view to operate on.
        box (CommentBox): The comment box to add.
        x (float): Scene x position.
        y (float): Scene y position.
    """

    def __init__(self, view: GraphView, box: CommentBox, x: float, y: float) -> None:
        self._view = view
        self._box = box
        self._x = x
        self._y = y

    def execute(self) -> None:
        self._view._node_refs.append(self._box)
        self._view.scene.addItem(self._box)
        self._box.setPos(self._x, self._y)

    def undo(self) -> None:
        self._view.scene.removeItem(self._box)
        if self._box in self._view._node_refs:
            self._view._node_refs.remove(self._box)


class MoveNodeCommand(Command):
    """
    Records a node move for undo/redo.

    Args:
        graph (Graph): The data graph to operate on.
        node_id (str): The id of the node that was moved.
        old_x (float): The x position before the move.
        old_y (float): The y position before the move.
        new_x (float): The x position after the move.
        new_y (float): The y position after the move.
    """

    def __init__(
        self,
        graph: Graph,
        node_id: str,
        old_x: float,
        old_y: float,
        new_x: float,
        new_y: float,
    ) -> None:
        self._graph = graph
        self._node_id = node_id
        self._old_x = old_x
        self._old_y = old_y
        self._new_x = new_x
        self._new_y = new_y

    def execute(self) -> None:
        self._graph.move_node(self._node_id, self._new_x, self._new_y)

    def undo(self) -> None:
        self._graph.move_node(self._node_id, self._old_x, self._old_y)


class CommandStack(object):
    """
    Manages an undo/redo stack of commands.

    Args:
        max_size (int): Maximum number of commands to retain.
    """

    def __init__(self, max_size: int = 100) -> None:
        self._max_size = max_size
        self._undo_stack: list[Command] = []
        self._redo_stack: list[Command] = []

    def push(self, command: Command) -> None:
        """
        Execute a command and push it onto the undo stack.

        Args:
            command (Command): The command to execute.
        """
        command.execute()
        self._undo_stack.append(command)
        self._redo_stack.clear()
        if len(self._undo_stack) > self._max_size:
            self._undo_stack.pop(0)

    def undo(self) -> None:
        """Undo the last command."""
        if not self._undo_stack:
            return
        command = self._undo_stack.pop()
        command.undo()
        self._redo_stack.append(command)

    def redo(self) -> None:
        """Redo the last undone command."""
        if not self._redo_stack:
            return
        command = self._redo_stack.pop()
        command.execute()
        self._undo_stack.append(command)

    def can_undo(self) -> bool:
        """
        Return whether there is a command to undo.

        Returns:
            bool: True if undo is available.
        """
        return bool(self._undo_stack)

    def can_redo(self) -> bool:
        """
        Return whether there is a command to redo.

        Returns:
            bool: True if redo is available.
        """
        return bool(self._redo_stack)

    def clear(self) -> None:
        """Clear both stacks."""
        self._undo_stack.clear()
        self._redo_stack.clear()
