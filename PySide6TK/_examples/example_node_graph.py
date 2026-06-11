from PySide6 import QtGui
from PySide6 import QtWidgets

from PySide6TK import QtWrappers
from PySide6TK import Nodes


class StartNodeWidget(Nodes.NodeWidget):
    _COLOR_HEADER = QtGui.QColor(40, 120, 60)


class TransitionNodeWidget(Nodes.NodeWidget):
    _COLOR_HEADER = QtGui.QColor(100, 60, 160)


class OutroNodeWidget(Nodes.NodeWidget):
    _COLOR_HEADER = QtGui.QColor(100, 160, 160)


class PanelNodeWidget(Nodes.NodeWidget):
    _COLOR_HEADER = QtGui.QColor(160, 60, 60)


class NodeGraphWindow(QtWidgets.QMainWindow):

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Node Graph")
        self.resize(1024, 768)

        self.data_graph = Nodes.Graph()
        self.view = Nodes.GraphView(self.data_graph, self)
        self.setCentralWidget(self.view)

        self._register_types()
        self._register_widgets()
        self._populate()

    def _register_types(self) -> None:
        self.data_graph.register_type(
            Nodes.NodeTypeDefinition(
                node_type="Start",
                title="Start",
                width=160,
                height=68,
                ports=[("output", "Exec")],
            )
        )
        self.data_graph.register_type(
            Nodes.NodeTypeDefinition(
                node_type="Panel",
                title="Panel",
                width=180,
                height=68,
                ports=[("input", "Previous"), ("output", "Output")],
                fields={
                    "filepath": "",
                    "duration": 3.0,
                    "scale": 1.0,
                    "offset": (0.0, 0.0),
                    "fit_mode": "Fit",
                    "visible": True,
                },
            )
        )
        self.data_graph.register_type(
            Nodes.NodeTypeDefinition(
                node_type="Transition",
                title="Transition",
                width=240,
                height=68,
                ports=[("input", "Pane"), ("output", "Post Transition")],
                fields={
                    "duration": 0.5,
                    "type": "fade",
                    "easing": "ease_in_out",
                    "color": (0, 0, 0, 255),
                },
            )
        )
        self.data_graph.register_type(
            Nodes.NodeTypeDefinition(
                node_type="Outro",
                title="Outro",
                width=160,
                height=60,
                ports=[("input", "Pane")],
            )
        )

    def _register_widgets(self) -> None:
        self.view.register_node(
            "Start", StartNodeWidget, category="Main", label="Start"
        )
        self.view.register_node(
            "Panel", PanelNodeWidget, category="Main", label="Panel"
        )
        self.view.register_node(
            "Transition", TransitionNodeWidget, category="Main", label="Transition"
        )
        self.view.register_node(
            "Outro", OutroNodeWidget, category="Main", label="Outro"
        )

    def _populate(self) -> None:
        node_start = self.data_graph.add_node_of_type("Start", 0, 0)
        node_pane_a = self.data_graph.add_node_of_type("Panel", 200, 0)
        node_pane_b = self.data_graph.add_node_of_type("Panel", 400, 0)
        node_transition = self.data_graph.add_node_of_type("Transition", 600, 0)
        node_pane_c = self.data_graph.add_node_of_type("Panel", 900, 0)
        node_outro = self.data_graph.add_node_of_type("Outro", 1100, 0)

        self.data_graph.set_field_value(
            node_pane_a.node_id,
            "filepath",
            "T:/git/catena/Core/Resources/PIC_Example_Board.png",
        )

        start_out = list(node_start.ports.values())[0]
        pane_a_in, pane_a_out = list(node_pane_a.ports.values())
        pane_b_in, pane_b_out = list(node_pane_b.ports.values())
        trans_in, trans_out = list(node_transition.ports.values())
        pane_c_in, pane_c_out = list(node_pane_c.ports.values())
        outro_in = list(node_outro.ports.values())[0]

        self.data_graph.connect_ports(start_out.port_id, pane_a_in.port_id)
        self.data_graph.connect_ports(pane_a_out.port_id, pane_b_in.port_id)
        self.data_graph.connect_ports(pane_b_out.port_id, trans_in.port_id)
        self.data_graph.connect_ports(trans_out.port_id, pane_c_in.port_id)
        self.data_graph.connect_ports(pane_c_out.port_id, outro_in.port_id)


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
