import pytest

from app.graph.models import EdgeData, NodeData
from app.graph.rail_graph import RailGraph, build_graph
from app.parser.models import Direction, EdgeRow, MapData, MapMeta, NodeRow, NodeType, TrainRow


@pytest.fixture
def map_data() -> MapData:
    return MapData(
        meta=MapMeta(name="Tutorial 1", width=20, height=15),
        nodes=[
            NodeRow(id=1, type=NodeType.station, x=2, y=3, name="Coal Mine", capacity=2),
            NodeRow(id=2, type=NodeType.station, x=18, y=12, name="Power Plant", capacity=2),
            NodeRow(id=3, type=NodeType.junction, x=10, y=7, name="", capacity=1),
        ],
        edges=[
            EdgeRow(
                from_id=1, to_id=3, cost=100, distance=8.0,
                capacity=1, direction=Direction.bidirectional, speed_limit=50,
            ),
            EdgeRow(
                from_id=3, to_id=2, cost=150, distance=10.0,
                capacity=1, direction=Direction.bidirectional, speed_limit=50,
            ),
        ],
        trains=[
            TrainRow(
                id=1, origin_id=1, destination_id=2, cargo="coal",
                speed=40, spawn_tick=0, priority=1,
            ),
        ],
    )


@pytest.fixture
def rail_graph(map_data: MapData) -> RailGraph:
    return build_graph(map_data)


class TestBuildGraph:
    def test_node_count(self, rail_graph: RailGraph) -> None:
        assert rail_graph.node_count == 3

    def test_edge_count_bidirectional(self, rail_graph: RailGraph) -> None:
        # 2 bidirectional CSV edges → 4 directed edges
        assert rail_graph.edge_count == 4

    def test_forward_only_edge(self, map_data: MapData) -> None:
        map_data.edges[0] = EdgeRow(
            from_id=1, to_id=3, cost=100, distance=8.0,
            capacity=1, direction=Direction.forward, speed_limit=50,
        )
        g = build_graph(map_data)
        assert g._graph.has_edge(1, 3)
        assert not g._graph.has_edge(3, 1)

    def test_reverse_only_edge(self, map_data: MapData) -> None:
        map_data.edges[0] = EdgeRow(
            from_id=1, to_id=3, cost=100, distance=8.0,
            capacity=1, direction=Direction.reverse, speed_limit=50,
        )
        g = build_graph(map_data)
        assert not g._graph.has_edge(1, 3)
        assert g._graph.has_edge(3, 1)

    def test_empty_graph(self) -> None:
        empty = MapData(
            meta=MapMeta(name="Empty", width=5, height=5),
            nodes=[],
            edges=[],
            trains=[],
        )
        g = build_graph(empty)
        assert g.node_count == 0
        assert g.edge_count == 0


class TestNodeAccess:
    def test_node_lookup_by_id(self, rail_graph: RailGraph) -> None:
        node = rail_graph.node(1)
        assert isinstance(node, NodeData)
        assert node.id == 1

    def test_node_type(self, rail_graph: RailGraph) -> None:
        assert rail_graph.node(1).type == NodeType.station
        assert rail_graph.node(3).type == NodeType.junction

    def test_node_coordinates(self, rail_graph: RailGraph) -> None:
        node = rail_graph.node(1)
        assert node.x == 2
        assert node.y == 3

    def test_node_name(self, rail_graph: RailGraph) -> None:
        assert rail_graph.node(1).name == "Coal Mine"

    def test_node_name_empty(self, rail_graph: RailGraph) -> None:
        assert rail_graph.node(3).name == ""

    def test_node_capacity(self, rail_graph: RailGraph) -> None:
        assert rail_graph.node(1).capacity == 2

    def test_node_not_found_raises(self, rail_graph: RailGraph) -> None:
        with pytest.raises(KeyError, match="99"):
            rail_graph.node(99)

    def test_nodes_list_length(self, rail_graph: RailGraph) -> None:
        assert len(rail_graph.nodes) == 3

    def test_nodes_of_type_stations(self, rail_graph: RailGraph) -> None:
        stations = rail_graph.nodes_of_type(NodeType.station)
        assert len(stations) == 2
        assert all(n.type == NodeType.station for n in stations)

    def test_nodes_of_type_junction(self, rail_graph: RailGraph) -> None:
        junctions = rail_graph.nodes_of_type(NodeType.junction)
        assert len(junctions) == 1
        assert junctions[0].id == 3

    def test_nodes_of_type_missing_returns_empty(self, rail_graph: RailGraph) -> None:
        assert rail_graph.nodes_of_type(NodeType.depot) == []


class TestEdgeAccess:
    def test_edge_lookup(self, rail_graph: RailGraph) -> None:
        edge = rail_graph.edge(1, 3)
        assert isinstance(edge, EdgeData)
        assert edge.from_id == 1
        assert edge.to_id == 3

    def test_reverse_edge_exists(self, rail_graph: RailGraph) -> None:
        edge = rail_graph.edge(3, 1)
        assert edge.from_id == 3
        assert edge.to_id == 1

    def test_edge_cost(self, rail_graph: RailGraph) -> None:
        assert rail_graph.edge(1, 3).cost == 100

    def test_edge_distance(self, rail_graph: RailGraph) -> None:
        assert rail_graph.edge(1, 3).distance == 8.0

    def test_edge_speed_limit(self, rail_graph: RailGraph) -> None:
        assert rail_graph.edge(1, 3).speed_limit == 50

    def test_edge_not_found_raises(self, rail_graph: RailGraph) -> None:
        with pytest.raises(KeyError, match=r"\(1, 2\)"):
            rail_graph.edge(1, 2)

    def test_edges_list_length(self, rail_graph: RailGraph) -> None:
        assert len(rail_graph.edges) == 4


class TestPathfinding:
    def test_has_path_direct(self, rail_graph: RailGraph) -> None:
        assert rail_graph.has_path(1, 3)

    def test_has_path_via_junction(self, rail_graph: RailGraph) -> None:
        assert rail_graph.has_path(1, 2)

    def test_has_path_reverse(self, rail_graph: RailGraph) -> None:
        assert rail_graph.has_path(2, 1)

    def test_no_path_disconnected(self) -> None:
        data = MapData(
            meta=MapMeta(name="Split", width=10, height=10),
            nodes=[
                NodeRow(id=1, type=NodeType.station, x=0, y=0, name="A"),
                NodeRow(id=2, type=NodeType.station, x=9, y=9, name="B"),
            ],
            edges=[],
            trains=[],
        )
        g = build_graph(data)
        assert not g.has_path(1, 2)
