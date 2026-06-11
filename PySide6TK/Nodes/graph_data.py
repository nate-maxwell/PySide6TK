from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Callable


@dataclass
class PortData(object):
    """
    A connection point on a node in the data graph.

    Args:
        name (str): Display name.
        port_type (str): Either ``"input"`` or ``"output"``.
        node_id (str): The id of the node this port belongs to.
        port_id (str): Unique id for this port within the graph.

    Attributes:
        connections (list[str]): Port ids this port is connected to.
    """

    name: str
    port_type: str
    node_id: str
    port_id: str
    connections: list[str] = field(default_factory=list)


@dataclass
class NodeData(object):
    """
    A node in the data graph.

    Args:
        node_id (str): Unique id for this node.
        node_type (str): The type name used to resolve the widget class.
        title (str): Display title.
        x (float): Scene x position.
        y (float): Scene y position.

    Attributes:
        fields (dict[str, Any]): Field values keyed by field name.
        ports (dict[str, PortData]): Ports keyed by port id.
        width (float | None): Optional width override.
        height (float | None): Optional height override.
    """

    node_id: str
    node_type: str
    title: str
    x: float
    y: float
    fields: dict[str, Any] = field(default_factory=dict)
    ports: dict[str, PortData] = field(default_factory=dict)
    width: float | None = None
    height: float | None = None


class Graph(object):
    """
    A pure data graph of nodes and connections.

    No Qt or broker dependency. Observers register callbacks directly on the
    graph instance to react to changes.

    Attributes:
        nodes (dict[str, NodeData]): All nodes keyed by node id.
        on_node_added (list[Callable[[NodeData], None]]): Callbacks fired when a node is added.
        on_node_removed (list[Callable[[str], None]]): Callbacks fired when a node is removed.
        on_ports_connected (list[Callable[[str, str], None]]): Callbacks fired when ports connect.
        on_ports_disconnected (list[Callable[[str, str], None]]): Callbacks fired when ports disconnect.
        on_field_changed (list[Callable[[str, str, Any], None]]): Callbacks fired when a field value changes.
        on_node_moved (list[Callable[[str, float, float], None]]): Callbacks fired when a node moves.
    """

    def __init__(self) -> None:
        self.nodes: dict[str, NodeData] = {}
        self._id_counter: int = 0

        self.on_node_added: list[Callable[[NodeData], None]] = []
        self.on_node_removed: list[Callable[[str], None]] = []
        self.on_ports_connected: list[Callable[[str, str], None]] = []
        self.on_ports_disconnected: list[Callable[[str, str], None]] = []
        self.on_field_changed: list[Callable[[str, str, Any], None]] = []
        self.on_node_moved: list[Callable[[str, float, float], None]] = []
        self.on_port_added: list[Callable[[PortData], None]] = []

    def _next_id(self) -> str:
        self._id_counter += 1
        return str(self._id_counter)

    def _fire(self, callbacks: list[Callable], *args: Any) -> None:
        for cb in callbacks:
            cb(*args)

    def add_node(
        self,
        node_type: str,
        title: str,
        x: float,
        y: float,
        width: float | None = None,
        height: float | None = None,
    ) -> NodeData:
        """
        Add a node to the graph and fire ``on_node_added`` callbacks.

        Args:
            node_type (str): The type name used to resolve the widget class.
            title (str): Display title.
            x (float): Scene x position.
            y (float): Scene y position.
            width (float | None): Optional width override.
            height (float | None): Optional height override.
        Returns:
            NodeData: The created node.
        """
        node = NodeData(
            node_id=self._next_id(),
            node_type=node_type,
            title=title,
            x=x,
            y=y,
            width=width,
            height=height,
        )
        self.nodes[node.node_id] = node
        self._fire(self.on_node_added, node)
        return node

    def remove_node(self, node_id: str) -> None:
        """
        Remove a node and all its connections and fire ``on_node_removed`` callbacks.

        Args:
            node_id (str): The id of the node to remove.
        """
        node = self.nodes.get(node_id)
        if node is None:
            return
        for port in list(node.ports.values()):
            for connected_port_id in list(port.connections):
                self.disconnect_ports(port.port_id, connected_port_id)
        del self.nodes[node_id]
        self._fire(self.on_node_removed, node_id)

    def add_port(self, node_id: str, port_type: str, name: str) -> PortData:
        """
        Add a port to a node and fire ``on_port_added`` callbacks.

        Args:
            node_id (str): The id of the node to add the port to.
            port_type (str): Either ``"input"`` or ``"output"``.
            name (str): Display name for the port.
        Returns:
            PortData: The created port.
        """
        node = self.nodes[node_id]
        port = PortData(
            name=name,
            port_type=port_type,
            node_id=node_id,
            port_id=self._next_id(),
        )
        node.ports[port.port_id] = port
        self._fire(self.on_port_added, port)
        return port

    def connect_ports(self, source_port_id: str, target_port_id: str) -> None:
        """
        Connect two ports and fire ``on_ports_connected`` callbacks.

        Args:
            source_port_id (str): The output port id.
            target_port_id (str): The input port id.
        """
        source = self._find_port(source_port_id)
        target = self._find_port(target_port_id)
        if source is None or target is None:
            return
        if target_port_id not in source.connections:
            source.connections.append(target_port_id)
        if source_port_id not in target.connections:
            target.connections.append(source_port_id)
        self._fire(self.on_ports_connected, source_port_id, target_port_id)

    def disconnect_ports(self, port_id_a: str, port_id_b: str) -> None:
        """
        Disconnect two ports and fire ``on_ports_disconnected`` callbacks.

        Args:
            port_id_a (str): One end of the connection.
            port_id_b (str): The other end of the connection.
        """
        port_a = self._find_port(port_id_a)
        port_b = self._find_port(port_id_b)
        if port_a is not None and port_id_b in port_a.connections:
            port_a.connections.remove(port_id_b)
        if port_b is not None and port_id_a in port_b.connections:
            port_b.connections.remove(port_id_a)
        self._fire(self.on_ports_disconnected, port_id_a, port_id_b)

    def set_field_value(self, node_id: str, name: str, value: Any) -> None:
        """
        Set a field value on a node and fire ``on_field_changed`` callbacks.

        Args:
            node_id (str): The id of the node.
            name (str): The field name.
            value (Any): The new value.
        """
        self.nodes[node_id].fields[name] = value
        self._fire(self.on_field_changed, node_id, name, value)

    def move_node(self, node_id: str, x: float, y: float) -> None:
        """
        Update a node's position and fire ``on_node_moved`` callbacks.

        Args:
            node_id (str): The id of the node.
            x (float): New scene x position.
            y (float): New scene y position.
        """
        node = self.nodes[node_id]
        node.x = x
        node.y = y
        self._fire(self.on_node_moved, node_id, x, y)

    def get_connections(self) -> list[tuple[str, str]]:
        """
        Return all connections as (source_port_id, target_port_id) pairs without duplicates.

        Returns:
            list[tuple[str, str]]: All connections.
        """
        seen: set[frozenset[str]] = set()
        result: list[tuple[str, str]] = []
        for node in self.nodes.values():
            for port in node.ports.values():
                for connected_id in port.connections:
                    key = frozenset({port.port_id, connected_id})
                    if key not in seen:
                        seen.add(key)
                        result.append((port.port_id, connected_id))
        return result

    def _find_port(self, port_id: str) -> PortData | None:
        for node in self.nodes.values():
            if port_id in node.ports:
                return node.ports[port_id]
        return None

    def clear(self) -> None:
        """Remove all nodes and connections without firing callbacks."""
        self.nodes.clear()
        self._id_counter = 0
