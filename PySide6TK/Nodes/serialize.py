from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from PySide6TK.Nodes.graph_data import Graph
from PySide6TK.Nodes.graph_data import NodeData
from PySide6TK.Nodes.graph_data import PortData


def serialize(graph: Graph) -> dict[str, Any]:
    """
    Serialize a Graph to a plain dict.

    Args:
        graph (Graph): The data graph to serialize.
    Returns:
        dict[str, Any]: The serialized graph.
    """

    def _serialize_value(value: Any) -> Any:
        if isinstance(value, tuple):
            return list(value)
        return value

    nodes_data = []
    for node in graph.nodes.values():
        ports_data = []
        for port in node.ports.values():
            ports_data.append(
                {
                    "port_id": port.port_id,
                    "name": port.name,
                    "port_type": port.port_type,
                    "connections": port.connections,
                }
            )
        nodes_data.append(
            {
                "node_id": node.node_id,
                "node_type": node.node_type,
                "title": node.title,
                "x": node.x,
                "y": node.y,
                "width": node.width,
                "height": node.height,
                "fields": {k: _serialize_value(v) for k, v in node.fields.items()},
                "ports": ports_data,
            }
        )

    return {
        "id_counter": graph._id_counter,
        "nodes": nodes_data,
    }


def deserialize(graph: Graph, data: dict[str, Any]) -> None:
    """
    Reconstruct a Graph from serialized data.

    Clears the graph before loading. Fires ``on_node_added`` and
    ``on_port_added`` callbacks so any attached view rebuilds itself.

    Args:
        graph (Graph): The graph to load into.
        data (dict[str, Any]): Serialized graph data from ``serialize``.
    """

    def _deserialize_value(value: Any) -> Any:
        if isinstance(value, list):
            return tuple(value)
        return value

    graph.clear()
    graph._id_counter = data.get("id_counter", 0)

    for node_data in data["nodes"]:
        node = NodeData(
            node_id=node_data["node_id"],
            node_type=node_data["node_type"],
            title=node_data["title"],
            x=node_data["x"],
            y=node_data["y"],
            width=node_data.get("width"),
            height=node_data.get("height"),
            fields={k: _deserialize_value(v) for k, v in node_data["fields"].items()},
        )
        graph.nodes[node.node_id] = node
        graph._fire(graph.on_node_added, node)

        for port_data in node_data["ports"]:
            port = PortData(
                name=port_data["name"],
                port_type=port_data["port_type"],
                node_id=node_data["node_id"],
                port_id=port_data["port_id"],
                connections=[],
            )
            node.ports[port.port_id] = port
            graph._fire(graph.on_port_added, port)

    for node_data in data["nodes"]:
        for port_data in node_data["ports"]:
            for connected_id in port_data["connections"]:
                port_a = graph._find_port(port_data["port_id"])
                port_b = graph._find_port(connected_id)
                if port_a is None or port_b is None:
                    continue
                key = frozenset({port_data["port_id"], connected_id})
                already = connected_id in port_a.connections
                if not already:
                    port_a.connections.append(connected_id)
                    port_b.connections.append(port_data["port_id"])
                    graph._fire(
                        graph.on_ports_connected, port_data["port_id"], connected_id
                    )


def save(graph: Graph, path: Path) -> None:
    """
    Serialize a Graph and write it to a JSON file.

    Args:
        graph (Graph): The data graph to save.
        path (Path): Destination file path.
    """
    path.write_text(json.dumps(serialize(graph), indent=2))


def load(graph: Graph, path: Path) -> None:
    """
    Load a JSON file and reconstruct the graph.

    Args:
        graph (Graph): The graph to load into.
        path (Path): Source file path.
    """
    deserialize(graph, json.loads(path.read_text()))
