from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING

from PySide6 import QtCore

from PySide6TK.Nodes.node import BaseNode
from PySide6TK.Nodes.port import Port
from PySide6TK.Nodes.wire import Wire
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
    Adds a node to the graph.

    Args:
        graph (GraphView): The graph view to operate on.
        node (BaseNode): The node to add.
        x (float): Scene x position.
        y (float): Scene y position.
    """

    def __init__(self, graph: GraphView, node: BaseNode, x: float, y: float) -> None:
        self._graph = graph
        self._node = node
        self._x = x
        self._y = y

    def execute(self) -> None:
        self._graph.add_node_internal(self._node, self._x, self._y)

    def undo(self) -> None:
        self._graph.remove_node_internal(self._node)


class RemoveNodeCommand(Command):
    """
    Removes a node and all its connected wires from the graph.

    Args:
        graph (GraphView): The graph view to operate on.
        node (BaseNode): The node to remove.
    """

    def __init__(self, graph: GraphView, node: BaseNode) -> None:
        self._graph = graph
        self._node = node
        self._pos = node.pos()
        self._severed_wires: list[tuple[Port, Port]] = []

    def execute(self) -> None:
        for port in self._graph._ports_of(self._node):
            for wire in list(port.wires):
                self._severed_wires.append((wire.source, wire.target))
                self._graph._destroy_wire(wire)
        self._graph.remove_node_internal(self._node)

    def undo(self) -> None:
        self._graph.add_node_internal(self._node, self._pos.x(), self._pos.y())
        for source, target in self._severed_wires:
            self._graph.connect_ports_internal(source, target)


class AddCommentCommand(Command):
    """
    Adds a comment box to the graph.

    Args:
        graph (GraphView): The graph view to operate on.
        box (CommentBox): The comment box to add.
        x (float): Scene x position.
        y (float): Scene y position.
    """

    def __init__(self, graph: GraphView, box: CommentBox, x: float, y: float) -> None:
        self._graph = graph
        self._box = box
        self._x = x
        self._y = y

    def execute(self) -> None:
        self._graph.add_node_internal(self._box, self._x, self._y)

    def undo(self) -> None:
        self._graph.remove_node_internal(self._box)


class ConnectPortsCommand(Command):
    """
    Connects two ports with a wire.

    Args:
        graph (GraphView): The graph view to operate on.
        source (Port): The output port.
        target (Port): The input port.
    """

    def __init__(self, graph: GraphView, source: Port, target: Port) -> None:
        self._graph = graph
        self._source = source
        self._target = target
        self._wire: Wire | None = None

    def execute(self) -> None:
        self._wire = self._graph.connect_ports_internal(self._source, self._target)

    def undo(self) -> None:
        if self._wire is not None:
            self._graph._destroy_wire(self._wire)


class MoveNodeCommand(Command):
    """
    Records a node move for undo/redo.

    Args:
        node (BaseNode): The node that was moved.
        old_pos (QtCore.QPointF): The position before the move.
        new_pos (QtCore.QPointF): The position after the move.
    """

    def __init__(
        self,
        node: BaseNode,
        old_pos: QtCore.QPointF,
        new_pos: QtCore.QPointF,
    ) -> None:
        self._node = node
        self._old_pos = old_pos
        self._new_pos = new_pos

    def execute(self) -> None:
        self._node.setPos(self._new_pos)

    def undo(self) -> None:
        self._node.setPos(self._old_pos)


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
