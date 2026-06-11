from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from typing import Any


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
    Describes a single editable field on a node type.

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


@dataclass
class PortDefinition(object):
    """
    Describes a port on a node type.

    Args:
        name (str): Display name.
        port_type (str): Either ``"input"`` or ``"output"``.
    """

    name: str
    port_type: str


class NodeDefinition(object):
    """
    A pure data descriptor for a node type.

    Subclass this to define a node type. The graph and view use this to
    know what ports and fields a node has, and what default values to use.
    No Qt dependency.

    Attributes:
        node_type (str): Unique type name. Defaults to the class name.
        title (str): Default display title.
        width (int): Default node width.
        body_height (int): Default body height.
        ports (list[PortDefinition]): Port descriptors in order.
        fields (list[FieldDefinition]): Field descriptors in order.

    Example::

        class BlurNode(NodeDefinition):
            node_type = "BlurNode"
            title = "Blur"
            width = 180
            body_height = 80
            ports = [
                PortDefinition("image", "input"),
                PortDefinition("image", "output"),
            ]
            fields = [
                FieldDefinition("radius", "Radius", FieldType.FLOAT, default=1.0),
                FieldDefinition("
                    quality", "Quality", FieldType.CHOICE,
                    default="medium", options=["low", "medium", "high"]
                ),
            ]
    """

    node_type: str = ""
    title: str = ""
    width: int = 180
    body_height: int = 80
    ports: list[PortDefinition] = []
    fields: list[FieldDefinition] = []

    @classmethod
    def default_fields(cls) -> dict[str, Any]:
        """
        Return a dict of field name to default value.

        Returns:
            dict[str, Any]: Default field values.
        """
        return {f.name: f.default for f in cls.fields}
