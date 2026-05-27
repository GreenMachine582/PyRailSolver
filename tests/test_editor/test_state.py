from app.editor.state import EditorState
from app.parser.models import NodeType


class TestEditorState:
    def test_initial_nodes_empty(self) -> None:
        s = EditorState()
        assert s.map_data.nodes == []

    def test_initial_edges_empty(self) -> None:
        s = EditorState()
        assert s.map_data.edges == []

    def test_initial_meta(self) -> None:
        s = EditorState()
        assert s.map_data.meta.name == "Untitled Map"
        assert s.map_data.meta.width == 20
        assert s.map_data.meta.height == 15

    def test_add_node_returns_node(self) -> None:
        s = EditorState()
        node = s.add_node(NodeType.station, 3, 4, "Mine")
        assert node.type == NodeType.station
        assert node.x == 3
        assert node.y == 4
        assert node.name == "Mine"

    def test_add_node_assigns_id(self) -> None:
        s = EditorState()
        n1 = s.add_node(NodeType.station, 0, 0)
        n2 = s.add_node(NodeType.station, 1, 1)
        assert n1.id == 1
        assert n2.id == 2

    def test_add_node_stored_in_map_data(self) -> None:
        s = EditorState()
        s.add_node(NodeType.station, 5, 5, "A")
        assert len(s.map_data.nodes) == 1
        assert s.map_data.nodes[0].name == "A"

    def test_map_data_nodes_is_copy(self) -> None:
        s = EditorState()
        s.add_node(NodeType.station, 0, 0)
        nodes = s.map_data.nodes
        nodes.clear()
        assert len(s.map_data.nodes) == 1

    def test_node_at_found(self) -> None:
        s = EditorState()
        s.add_node(NodeType.station, 3, 7, "B")
        result = s.node_at(3, 7)
        assert result is not None
        assert result.name == "B"

    def test_node_at_not_found(self) -> None:
        s = EditorState()
        assert s.node_at(0, 0) is None

    def test_node_at_wrong_coords(self) -> None:
        s = EditorState()
        s.add_node(NodeType.station, 3, 7)
        assert s.node_at(3, 8) is None

    def test_reset_clears_nodes(self) -> None:
        s = EditorState()
        s.add_node(NodeType.station, 1, 1)
        s.reset()
        assert s.map_data.nodes == []

    def test_reset_resets_id_counter(self) -> None:
        s = EditorState()
        s.add_node(NodeType.station, 1, 1)
        s.reset()
        node = s.add_node(NodeType.station, 2, 2)
        assert node.id == 1

    def test_reset_with_custom_meta(self) -> None:
        s = EditorState()
        s.reset(name="Test Map", width=10, height=8)
        meta = s.map_data.meta
        assert meta.name == "Test Map"
        assert meta.width == 10
        assert meta.height == 8

    def test_add_node_default_name(self) -> None:
        s = EditorState()
        node = s.add_node(NodeType.junction, 0, 0)
        assert node.name == ""

    def test_add_platform_node(self) -> None:
        s = EditorState()
        node = s.add_node(NodeType.platform, 1, 2, "Mine Platform")
        assert node.type == NodeType.platform
        assert node.name == "Mine Platform"

    def test_add_depot_node(self) -> None:
        s = EditorState()
        node = s.add_node(NodeType.depot, 3, 4, "Yard")
        assert node.type == NodeType.depot

    def test_add_waypoint_node(self) -> None:
        s = EditorState()
        node = s.add_node(NodeType.waypoint, 5, 6)
        assert node.type == NodeType.waypoint
        assert node.name == ""

    def test_add_endpoint_node(self) -> None:
        s = EditorState()
        node = s.add_node(NodeType.endpoint, 7, 8, "North Siding")
        assert node.type == NodeType.endpoint

    def test_mixed_node_types_stored(self) -> None:
        s = EditorState()
        s.add_node(NodeType.station, 0, 0, "A")
        s.add_node(NodeType.junction, 5, 5)
        s.add_node(NodeType.depot, 10, 10, "Yard")
        nodes = s.map_data.nodes
        assert len(nodes) == 3
        assert nodes[0].type == NodeType.station
        assert nodes[1].type == NodeType.junction
        assert nodes[2].type == NodeType.depot
