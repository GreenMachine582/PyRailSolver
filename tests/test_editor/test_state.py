from app.editor.state import EditorState
from app.parser.models import Direction, MapData, MapMeta, NodeRow, NodeType


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


class TestAddEdge:
    def test_add_edge_returns_edge(self) -> None:
        s = EditorState()
        s.add_node(NodeType.station, 0, 0, "A")
        s.add_node(NodeType.station, 5, 5, "B")
        edge = s.add_edge(1, 2)
        assert edge.from_id == 1
        assert edge.to_id == 2

    def test_add_edge_stored_in_map_data(self) -> None:
        s = EditorState()
        s.add_node(NodeType.station, 0, 0, "A")
        s.add_node(NodeType.station, 5, 5, "B")
        s.add_edge(1, 2)
        assert len(s.map_data.edges) == 1

    def test_add_edge_default_direction_bidirectional(self) -> None:
        s = EditorState()
        s.add_node(NodeType.station, 0, 0)
        s.add_node(NodeType.station, 5, 5)
        edge = s.add_edge(1, 2)
        assert edge.direction == Direction.bidirectional

    def test_add_edge_custom_direction_forward(self) -> None:
        s = EditorState()
        s.add_node(NodeType.station, 0, 0)
        s.add_node(NodeType.station, 5, 5)
        edge = s.add_edge(1, 2, direction=Direction.forward)
        assert edge.direction == Direction.forward

    def test_add_edge_custom_cost(self) -> None:
        s = EditorState()
        s.add_node(NodeType.station, 0, 0)
        s.add_node(NodeType.station, 5, 5)
        edge = s.add_edge(1, 2, cost=75)
        assert edge.cost == 75

    def test_add_edge_custom_distance(self) -> None:
        s = EditorState()
        s.add_node(NodeType.station, 0, 0)
        s.add_node(NodeType.station, 5, 5)
        edge = s.add_edge(1, 2, distance=3.5)
        assert edge.distance == 3.5

    def test_add_edge_custom_capacity(self) -> None:
        s = EditorState()
        s.add_node(NodeType.station, 0, 0)
        s.add_node(NodeType.station, 5, 5)
        edge = s.add_edge(1, 2, capacity=4)
        assert edge.capacity == 4

    def test_add_edge_custom_speed_limit(self) -> None:
        s = EditorState()
        s.add_node(NodeType.station, 0, 0)
        s.add_node(NodeType.station, 5, 5)
        edge = s.add_edge(1, 2, speed_limit=80)
        assert edge.speed_limit == 80

    def test_map_data_edges_is_copy(self) -> None:
        s = EditorState()
        s.add_node(NodeType.station, 0, 0)
        s.add_node(NodeType.station, 5, 5)
        s.add_edge(1, 2)
        edges = s.map_data.edges
        edges.clear()
        assert len(s.map_data.edges) == 1

    def test_reset_clears_edges(self) -> None:
        s = EditorState()
        s.add_node(NodeType.station, 0, 0)
        s.add_node(NodeType.station, 5, 5)
        s.add_edge(1, 2)
        s.reset()
        assert s.map_data.edges == []


class TestUpdateNode:
    def test_update_node_returns_true(self) -> None:
        s = EditorState()
        s.add_node(NodeType.station, 1, 1, "Old")
        assert s.update_node(1, "New", NodeType.station) is True

    def test_update_node_changes_name(self) -> None:
        s = EditorState()
        s.add_node(NodeType.station, 1, 1, "Old")
        s.update_node(1, "New Name", NodeType.station)
        assert s.map_data.nodes[0].name == "New Name"

    def test_update_node_changes_type(self) -> None:
        s = EditorState()
        s.add_node(NodeType.station, 1, 1, "A")
        s.update_node(1, "A", NodeType.depot)
        assert s.map_data.nodes[0].type == NodeType.depot

    def test_update_node_unknown_id_returns_false(self) -> None:
        s = EditorState()
        assert s.update_node(99, "X", NodeType.station) is False

    def test_update_node_preserves_position(self) -> None:
        s = EditorState()
        s.add_node(NodeType.station, 3, 7, "A")
        s.update_node(1, "B", NodeType.junction)
        node = s.map_data.nodes[0]
        assert node.x == 3
        assert node.y == 7

    def test_update_node_preserves_id(self) -> None:
        s = EditorState()
        s.add_node(NodeType.station, 3, 7, "A")
        s.update_node(1, "B", NodeType.junction)
        assert s.map_data.nodes[0].id == 1


class TestDeleteNode:
    def test_delete_node_returns_true(self) -> None:
        s = EditorState()
        s.add_node(NodeType.station, 0, 0, "A")
        assert s.delete_node(1) is True

    def test_delete_node_removes_from_map(self) -> None:
        s = EditorState()
        s.add_node(NodeType.station, 0, 0, "A")
        s.delete_node(1)
        assert s.map_data.nodes == []

    def test_delete_node_unknown_id_returns_false(self) -> None:
        s = EditorState()
        assert s.delete_node(99) is False

    def test_delete_node_cascades_edges(self) -> None:
        s = EditorState()
        s.add_node(NodeType.station, 0, 0, "A")
        s.add_node(NodeType.station, 5, 5, "B")
        s.add_edge(1, 2)
        s.delete_node(1)
        assert s.map_data.edges == []

    def test_delete_node_cascades_only_connected_edges(self) -> None:
        s = EditorState()
        s.add_node(NodeType.station, 0, 0, "A")
        s.add_node(NodeType.station, 5, 5, "B")
        s.add_node(NodeType.station, 10, 10, "C")
        s.add_edge(1, 2)
        s.add_edge(2, 3)
        s.delete_node(1)
        assert len(s.map_data.edges) == 1
        assert s.map_data.edges[0].from_id == 2

    def test_delete_node_preserves_other_nodes(self) -> None:
        s = EditorState()
        s.add_node(NodeType.station, 0, 0, "A")
        s.add_node(NodeType.station, 5, 5, "B")
        s.delete_node(1)
        assert len(s.map_data.nodes) == 1
        assert s.map_data.nodes[0].name == "B"


class TestDeleteEdge:
    def test_delete_edge_returns_true(self) -> None:
        s = EditorState()
        s.add_node(NodeType.station, 0, 0)
        s.add_node(NodeType.station, 5, 5)
        s.add_edge(1, 2)
        assert s.delete_edge(0) is True

    def test_delete_edge_removes_from_map(self) -> None:
        s = EditorState()
        s.add_node(NodeType.station, 0, 0)
        s.add_node(NodeType.station, 5, 5)
        s.add_edge(1, 2)
        s.delete_edge(0)
        assert s.map_data.edges == []

    def test_delete_edge_out_of_bounds_returns_false(self) -> None:
        s = EditorState()
        assert s.delete_edge(0) is False

    def test_delete_edge_negative_index_returns_false(self) -> None:
        s = EditorState()
        assert s.delete_edge(-1) is False

    def test_delete_edge_by_index_correct_edge_removed(self) -> None:
        s = EditorState()
        s.add_node(NodeType.station, 0, 0, "A")
        s.add_node(NodeType.station, 5, 5, "B")
        s.add_node(NodeType.station, 10, 10, "C")
        s.add_edge(1, 2)
        s.add_edge(2, 3)
        s.delete_edge(0)
        assert len(s.map_data.edges) == 1
        assert s.map_data.edges[0].from_id == 2


class TestUpdateEdge:
    def _setup(self) -> EditorState:
        s = EditorState()
        s.add_node(NodeType.station, 0, 0, "A")
        s.add_node(NodeType.station, 5, 5, "B")
        s.add_edge(1, 2, cost=10, distance=2.0, capacity=2, speed_limit=80)
        return s

    def test_update_edge_returns_true(self) -> None:
        s = self._setup()
        assert s.update_edge(0, Direction.bidirectional, 20, 3.0, 3, 60) is True

    def test_update_edge_out_of_bounds_returns_false(self) -> None:
        s = self._setup()
        assert s.update_edge(5, Direction.bidirectional, 0, 1.0, 1, 100) is False

    def test_update_edge_negative_index_returns_false(self) -> None:
        s = self._setup()
        assert s.update_edge(-1, Direction.bidirectional, 0, 1.0, 1, 100) is False

    def test_update_edge_changes_cost(self) -> None:
        s = self._setup()
        s.update_edge(0, Direction.bidirectional, 99, 2.0, 2, 80)
        assert s.map_data.edges[0].cost == 99

    def test_update_edge_changes_distance(self) -> None:
        s = self._setup()
        s.update_edge(0, Direction.bidirectional, 10, 4.5, 2, 80)
        assert s.map_data.edges[0].distance == 4.5

    def test_update_edge_changes_capacity(self) -> None:
        s = self._setup()
        s.update_edge(0, Direction.bidirectional, 10, 2.0, 5, 80)
        assert s.map_data.edges[0].capacity == 5

    def test_update_edge_changes_speed_limit(self) -> None:
        s = self._setup()
        s.update_edge(0, Direction.bidirectional, 10, 2.0, 2, 120)
        assert s.map_data.edges[0].speed_limit == 120

    def test_update_edge_changes_direction(self) -> None:
        s = self._setup()
        s.update_edge(0, Direction.forward, 10, 2.0, 2, 80)
        assert s.map_data.edges[0].direction == Direction.forward

    def test_update_edge_preserves_from_to(self) -> None:
        s = self._setup()
        s.update_edge(0, Direction.bidirectional, 0, 1.0, 1, 100)
        edge = s.map_data.edges[0]
        assert edge.from_id == 1
        assert edge.to_id == 2


class TestLoadMap:
    def _make_map(self) -> MapData:
        return MapData(
            meta=MapMeta(name="Test", width=10, height=8),
            nodes=[NodeRow(id=5, type=NodeType.station, x=1, y=1, name="X")],
            edges=[],
            trains=[],
        )

    def test_load_sets_meta(self) -> None:
        s = EditorState()
        s.load(self._make_map())
        assert s.map_data.meta.name == "Test"
        assert s.map_data.meta.width == 10

    def test_load_sets_nodes(self) -> None:
        s = EditorState()
        s.load(self._make_map())
        assert len(s.map_data.nodes) == 1
        assert s.map_data.nodes[0].name == "X"

    def test_load_sets_next_id_after_max(self) -> None:
        s = EditorState()
        s.load(self._make_map())
        new_node = s.add_node(NodeType.junction, 3, 3)
        assert new_node.id == 6

    def test_load_empty_nodes_next_id_is_one(self) -> None:
        s = EditorState()
        data = MapData(
            meta=MapMeta(name="Empty", width=5, height=5),
            nodes=[],
            edges=[],
            trains=[],
        )
        s.load(data)
        new_node = s.add_node(NodeType.junction, 1, 1)
        assert new_node.id == 1

    def test_load_replaces_existing_state(self) -> None:
        s = EditorState()
        s.add_node(NodeType.station, 0, 0, "Old")
        s.load(self._make_map())
        assert len(s.map_data.nodes) == 1
        assert s.map_data.nodes[0].name == "X"
