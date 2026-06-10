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

    Nodes are stored with their type name, position, field values, and a
    generated id. Wires are stored as pairs of port references in the form
    ``(node_id, port_type, port_index)``.

    Args:
        view (GraphView): The graph view to serialize.
    Returns:
        dict[str, Any]: The serialized graph.
    """
    nodes = [i for i in view.scene.items() if isinstance(i, BaseNode)]

    node_ids: dict[int, str] = {}
    nodes_data: list[dict[str, Any]] = []

    for i, node in enumerate(nodes):
        node_id = str(i)
        node_ids[id(node)] = node_id
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


def deserialize(
    view: GraphView,
    data: dict[str, Any],
    registry: dict[str, type[BaseNode]],
) -> None:
    """
    Reconstruct a graph from serialized data into a GraphView.

    Clears the existing scene before loading. Node types are resolved via
    ``registry``, which maps type name strings to node classes.

    Args:
        view (GraphView): The graph view to load into.
        data (dict[str, Any]): Serialized graph data from ``serialize``.
        registry (dict[str, type[BaseNode]]): Map of type name to node class.
    """
    view.scene.clear()

    nodes_by_id: dict[str, BaseNode] = {}

    for node_data in data["nodes"]:
        node_type = registry.get(node_data["type"])
        if node_type is None:
            continue
        node = node_type()
        for name, value in node_data["fields"].items():
            if name in node._fields:
                node.set_field_value(name, _deserialize_value(value))
        view.add_node(node, node_data["x"], node_data["y"])
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
        view.connect_ports(source_ports[si], target_ports[ti])


def save(view: GraphView, path: Path) -> None:
    """
    Serialize a GraphView and write it to a JSON file.

    Args:
        view (GraphView): The graph view to save.
        path (Path): Destination file path.
    """
    data = serialize(view)
    path.write_text(json.dumps(data, indent=2))


def load(
    view: GraphView,
    path: Path,
    registry: dict[str, type[BaseNode]],
) -> None:
    """
    Load a JSON file and reconstruct the graph into a GraphView.

    Args:
        view (GraphView): The graph view to load into.
        path (Path): Source file path.
        registry (dict[str, type[BaseNode]]): Map of type name to node class.
    """
    data = json.loads(path.read_text())
    deserialize(view, data, registry)


def _port_index(port: Port, node: BaseNode, port_type: str) -> int:
    ports = node.output_ports() if port_type == PortType.OUTPUT else node.input_ports()
    return ports.index(port)


def _serialize_value(value: Any) -> Any:
    if isinstance(value, tuple):
        return list(value)
    return value


def _deserialize_value(value: Any) -> Any:
    if isinstance(value, list):
        return tuple(value)
    return value
