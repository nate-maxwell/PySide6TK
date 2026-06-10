from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from PySide6TK.Nodes.node import BaseNode
from PySide6TK.Nodes.port import Port
from PySide6TK.Nodes.port import PortType
from PySide6TK.Nodes.graph import GraphView


def serialize(view: GraphView) -> dict[str, Any]:
    """
    Serialize a GraphView to a plain dict.

    All nodes are serialized in insertion order. Wires are stored as pairs
    of port references in the form ``(node_id, port_type, port_index)``.

    Args:
        view (GraphView): The graph view to serialize.
    Returns:
        dict[str, Any]: The serialized graph.
    """

    def _serialize_value(value: Any) -> Any:
        if isinstance(value, tuple):
            return list(value)
        return value

    def _port_index(port: Port, node_: BaseNode, port_type: str) -> int:
        ports = (
            node_.output_ports()
            if port_type == PortType.OUTPUT
            else node_.input_ports()
        )
        return ports.index(port)

    node_ids: dict[int, str] = {}
    nodes_data: list[dict[str, Any]] = []

    for i, node in enumerate(view.nodes_in_view):
        node_id = str(i)
        node_ids[id(node)] = node_id
        print(f"{i}: {type(node).__name__} - {node}")
        pos = node.pos()
        nodes_data.append(
            {
                "id": node_id,
                "type": type(node).__name__,
                "x": pos.x(),
                "y": pos.y(),
                "fields": {
                    name: _serialize_value(value)
                    for name, value in node._field_values.items()
                },
            }
        )

    wires_data: list[dict[str, Any]] = []
    for wire in view.get_wires():
        source_node = wire.source.parentItem()
        target_node = wire.target.parentItem()
        if not isinstance(source_node, BaseNode) or not isinstance(
            target_node, BaseNode
        ):
            continue
        wires_data.append(
            {
                "source_node": node_ids[id(source_node)],
                "source_port": _port_index(wire.source, source_node, PortType.OUTPUT),
                "target_node": node_ids[id(target_node)],
                "target_port": _port_index(wire.target, target_node, PortType.INPUT),
            }
        )

    return {"nodes": nodes_data, "wires": wires_data}


def save(graph: GraphView, path: Path) -> None:
    """
    Serialize a GraphView and write it to a JSON file.

    Args:
        graph (GraphView): The graph view to save.
        path (Path): Destination file path.
    """
    data = serialize(graph)
    path.write_text(json.dumps(data, indent=2))


def deserialize(graph: GraphView, data: dict[str, Any]) -> None:
    """
    Reconstruct a graph from serialized data into a GraphView.

    Clears the existing scene before loading. Node types are resolved via
    ``registry``, which maps type name strings to node classes.

    Args:
        graph (GraphView): The graph view to load into.
        data (dict[str, Any]): Serialized graph data from ``serialize``.
    """

    def _deserialize_value(value_: Any) -> Any:
        if isinstance(value_, list):
            return tuple(value_)
        return value_

    registry = {
        node_type.__name__: node_type
        for node_types in graph.node_registry.values()
        for node_type in node_types
    }

    graph.scene.clear()
    nodes_by_id: dict[str, BaseNode] = {}

    for node_data in data["nodes"]:
        node_type = registry.get(node_data["type"])
        if node_type is None:
            continue

        node = node_type()
        node.title = node_data.get("title", node.title)
        for name, value in node_data["fields"].items():
            if name in node._fields:
                node.set_field_value(name, _deserialize_value(value))

        graph.add_node(node, node_data["x"], node_data["y"])
        nodes_by_id[node_data["id"]] = node

    for wire_data in data["wires"]:
        source_node = nodes_by_id.get(wire_data["source_node"])
        target_node = nodes_by_id.get(wire_data["target_node"])
        if source_node is None or target_node is None:
            continue

        source_ports = source_node.output_ports()
        target_ports = target_node.input_ports()
        si = wire_data["source_port"]
        ti = wire_data["target_port"]
        if si >= len(source_ports) or ti >= len(target_ports):
            continue

        graph.connect_ports(source_ports[si], target_ports[ti])


def load(graph: GraphView, path: Path) -> None:
    """
    Load a JSON file and reconstruct the graph into a GraphView.

    Args:
        graph (GraphView): The graph view to load into.
        path (Path): Source file path.
    """
    data = json.loads(path.read_text())
    deserialize(graph, data)
