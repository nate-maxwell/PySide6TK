from PySide6 import QtGui
from PySide6 import QtWidgets

from PySide6TK import QtWrappers
from PySide6TK import Nodes


class StartNode(Nodes.BaseNode):

    _COLOR_HEADER = QtGui.QColor(40, 120, 60)

    def __init__(self) -> None:
        super().__init__(title="Start", width=160, body_height=40)

    def _build(self) -> None:
        self.port_out = self.add_port(Nodes.PortType.OUTPUT, "Exec")


class TransitionNode(Nodes.BaseNode):

    _COLOR_HEADER = QtGui.QColor(100, 60, 160)

    def __init__(self) -> None:
        super().__init__(title="Transition", width=240, body_height=40)

    def _build(self) -> None:
        self.port_in = self.add_port(Nodes.PortType.INPUT, "Pane")
        self.port_out = self.add_port(Nodes.PortType.OUTPUT, "Post Transition")

        self.add_field(
            Nodes.FieldDefinition(
                name="duration",
                label="Duration",
                field_type=Nodes.FieldType.FLOAT,
                default=0.5,
                min_value=0.0,
                max_value=10.0,
            )
        )
        self.add_field(
            Nodes.FieldDefinition(
                name="type",
                label="Type",
                field_type=Nodes.FieldType.CHOICE,
                default="fade",
                options=["fade", "wipe", "dissolve", "cut"],
            )
        )
        self.add_field(
            Nodes.FieldDefinition(
                name="easing",
                label="Easing",
                field_type=Nodes.FieldType.CHOICE,
                default="ease_in_out",
                options=["linear", "ease_in", "ease_out", "ease_in_out"],
            )
        )
        self.add_field(
            Nodes.FieldDefinition(
                name="color",
                label="Color",
                field_type=Nodes.FieldType.COLOR,
                default=(0, 0, 0, 255),
            )
        )


class OutroNode(Nodes.BaseNode):

    _COLOR_HEADER = QtGui.QColor(100, 160, 160)

    def __init__(self) -> None:
        super().__init__(title="Outro", width=160, body_height=40)

    def _build(self) -> None:
        self.port_in = self.add_port(Nodes.PortType.INPUT, "Pane")


class PanelNode(Nodes.BaseNode):

    _COLOR_HEADER = QtGui.QColor(160, 60, 60)

    def __init__(self) -> None:
        super().__init__(title="Panel", width=180, body_height=40)

    def _build(self) -> None:
        self.port_in = self.add_port(Nodes.PortType.INPUT, "Previous")
        self.port_out = self.add_port(Nodes.PortType.OUTPUT, "Output")

        self.add_field(
            Nodes.FieldDefinition(
                name="filepath",
                label="Filepath",
                field_type=Nodes.FieldType.STR,
                default="",
            )
        )
        self.add_field(
            Nodes.FieldDefinition(
                name="duration",
                label="Duration",
                field_type=Nodes.FieldType.FLOAT,
                default=3.0,
                min_value=0.0,
                max_value=60.0,
            )
        )
        self.add_field(
            Nodes.FieldDefinition(
                name="scale",
                label="Scale",
                field_type=Nodes.FieldType.FLOAT,
                default=1.0,
                min_value=0.1,
                max_value=10.0,
            )
        )
        self.add_field(
            Nodes.FieldDefinition(
                name="offset",
                label="Offset",
                field_type=Nodes.FieldType.VEC2,
                default=(0.0, 0.0),
            )
        )
        self.add_field(
            Nodes.FieldDefinition(
                name="fit_mode",
                label="Fit Mode",
                field_type=Nodes.FieldType.CHOICE,
                default="Fit",
                options=["Fit", "Fill", "Stretch", "None"],
            )
        )
        self.add_field(
            Nodes.FieldDefinition(
                name="visible",
                label="Visible",
                field_type=Nodes.FieldType.BOOL,
                default=True,
            )
        )


class NodeGraphWindow(QtWidgets.QMainWindow):

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Node Graph")
        self.resize(1024, 768)

        self.cur_pos = 0

        self.graph = Nodes.GraphView(self)
        self.setCentralWidget(self.graph)

        self._populate()

    def _populate(self) -> None:
        self.node_start = StartNode()
        self.node_pane_a = PanelNode()
        self.node_pane_a.set_field_value(
            "filepath", "T:/git/catena//Core/Resources/PIC_Example_Board.png"
        )
        self.node_pane_b = PanelNode()
        self.node_transition = TransitionNode()
        self.node_pane_c = PanelNode()
        self.node_outro = OutroNode()

        self.graph.add_node(self.node_start, 0, 0)
        self.graph.add_node(self.node_pane_a, 200, 0)
        self.graph.add_node(self.node_pane_b, 400, 0)
        self.graph.add_node(self.node_transition, 600, 0)
        self.graph.add_node(self.node_pane_c, 900, 0)
        self.graph.add_node(self.node_outro, 1100, 0)

        self.graph.connect_ports(self.node_start.port_out, self.node_pane_a.port_in)
        self.graph.connect_ports(self.node_pane_a.port_out, self.node_pane_b.port_in)
        self.graph.connect_ports(
            self.node_pane_b.port_out, self.node_transition.port_in
        )
        self.graph.connect_ports(
            self.node_transition.port_out, self.node_pane_c.port_in
        )
        self.graph.connect_ports(self.node_pane_c.port_out, self.node_outro.port_in)


class ExampleWindow(QtWrappers.MainWindow):
    def __init__(self) -> None:
        super().__init__("Example Buttons Window")

        self.wid = QtWidgets.QWidget()
        self.layout_main = QtWidgets.QHBoxLayout()
        self.wid.setLayout(self.layout_main)
        self.setCentralWidget(self.wid)

        self.graph = NodeGraphWindow()
        self.layout_main.addWidget(self.graph)


if __name__ == "__main__":
    QtWrappers.exec_app(ExampleWindow, "ExampleNodeGraph")
