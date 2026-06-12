from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from PySide6TK.Nodes.graph import GraphView
from PySide6TK.Nodes.node import BaseNode


def serialize_nodes(view: GraphView, nodes: list[BaseNode]) -> dict[str, Any]:
    """
    Serialize a subset of nodes and the wires between them to a plain dict.

    Args:
        view (GraphView): The graph view the nodes belong to.
        nodes (list[BaseNode]): The nodes to serialize.
    Returns:
        dict[str, Any]: The serialized nodes and wires.
    """

    def _serialize_value(value: Any) -> Any:
        if isinstance(value, tuple):
            return list(value)
        return value

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
                "title": node.title,
                "x": pos.x(),
                "y": pos.y(),
                "width": getattr(node, "_box_width", None),
                "height": getattr(node, "_box_height", None),
                "fields": {
                    name: _serialize_value(value)
                    for name, value in node._field_values.items()
                },
            }
        )

    node_set = set(node_ids.keys())
    wires_data: list[dict[str, Any]] = []
    for wire in view.get_wires():
        source_node = wire.source.parentItem()
        target_node = wire.target.parentItem()
        if id(source_node) not in node_set or id(target_node) not in node_set:
            continue
        wires_data.append(
            {
                "source_node": node_ids[id(source_node)],
                "source_port": source_node.output_ports().index(wire.source),
                "target_node": node_ids[id(target_node)],
                "target_port": target_node.input_ports().index(wire.target),
            }
        )

    return {"nodes": nodes_data, "wires": wires_data}


def serialize(view: GraphView) -> dict[str, Any]:
    """
    Serialize a GraphView to a plain dict.

    Args:
        view (GraphView): The graph view to serialize.
    Returns:
        dict[str, Any]: The serialized graph.
    """
    return serialize_nodes(view, view._node_refs)


def save(graph: GraphView, path: Path) -> None:
    """
    Serialize a GraphView and write it to a JSON file.

    Args:
        graph (GraphView): The graph view to save.
        path (Path): Destination file path.
    """
    data = serialize(graph)
    path.write_text(json.dumps(data, indent=2))


def deserialize_nodes(
    view: GraphView,
    data: dict[str, Any],
    offset: tuple[float, float] | None = None,
) -> list[BaseNode]:
    """
    Reconstruct nodes and wires from serialized data and add them to a GraphView.

    Args:
        view (GraphView): The graph view to add the nodes to.
        data (dict[str, Any]): Serialized data from ``serialize_nodes`` or ``serialize``.
        offset (tuple[float, float] | None): If provided, positions are
            translated so the first node lands at this (x, y), preserving
            relative offsets between nodes.
    Returns:
        list[BaseNode]: The newly created nodes, selected and added to the scene.
    """

    def _deserialize_value(value_: Any) -> Any:
        if isinstance(value_, list):
            return tuple(value_)
        return value_

    registry = {
        node_type.__name__: node_type
        for node_types in view.node_registry.values()
        for node_type in node_types
    }
    registry[view.comment_type.__name__] = view.comment_type

    nodes_by_id: dict[str, BaseNode] = {}
    created: list[BaseNode] = []

    origin_x = 0.0
    origin_y = 0.0
    if offset is not None and data["nodes"]:
        origin_x = data["nodes"][0]["x"]
        origin_y = data["nodes"][0]["y"]

    view.scene.clearSelection()

    for node_data in data["nodes"]:
        node_type = registry.get(node_data["type"])
        if node_type is None:
            continue

        node = node_type()
        if node_data.get("width") is not None:
            node._box_width = node_data["width"]
        if node_data.get("height") is not None:
            node._box_height = node_data["height"]
        node.title = node_data.get("title", node.title)
        for name, value in node_data["fields"].items():
            if name in node._fields:
                node.set_field_value(name, _deserialize_value(value))

        if offset is not None:
            new_x = offset[0] + (node_data["x"] - origin_x)
            new_y = offset[1] + (node_data["y"] - origin_y)
        else:
            new_x = node_data["x"]
            new_y = node_data["y"]

        view.add_node(node, new_x, new_y)
        nodes_by_id[node_data["id"]] = node
        created.append(node)

        if offset is not None:
            node.setSelected(True)

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

    return created


def deserialize(view: GraphView, data: dict[str, Any]) -> None:
    """
    Reconstruct a graph from serialized data into a GraphView.

    Clears the existing scene before loading.

    Args:
        view (GraphView): The graph view to load into.
        data (dict[str, Any]): Serialized graph data from ``serialize``.
    """
    view.scene.clear()
    deserialize_nodes(view, data, offset=None)


def load(graph: GraphView, path: Path) -> None:
    """
    Load a JSON file and reconstruct the graph into a GraphView.

    Args:
        graph (GraphView): The graph view to load into.
        path (Path): Source file path.
    """
    data = json.loads(path.read_text())
    deserialize(graph, data)
