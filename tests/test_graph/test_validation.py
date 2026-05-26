import pytest

from app.graph.rail_graph import build_graph
from app.graph.validation import validate_map_data, validate_rail_graph
from app.parser.models import Direction, EdgeRow, MapData, MapMeta, NodeRow, NodeType, TrainRow


def _make_map(
    *,
    width: int = 20,
    height: int = 15,
    nodes: list[NodeRow] | None = None,
    edges: list[EdgeRow] | None = None,
    trains: list[TrainRow] | None = None,
) -> MapData:
    return MapData(
        meta=MapMeta(name="Test", width=width, height=height),
        nodes=nodes if nodes is not None else [
            NodeRow(id=1, type=NodeType.station, x=2, y=3, name="A", capacity=2),
            NodeRow(id=2, type=NodeType.station, x=18, y=12, name="B", capacity=2),
            NodeRow(id=3, type=NodeType.junction, x=10, y=7),
        ],
        edges=edges if edges is not None else [
            EdgeRow(from_id=1, to_id=3, cost=100, distance=8.0, direction=Direction.bidirectional),
            EdgeRow(from_id=3, to_id=2, cost=150, distance=10.0, direction=Direction.bidirectional),
        ],
        trains=trains if trains is not None else [
            TrainRow(id=1, origin_id=1, destination_id=2),
        ],
    )


@pytest.fixture
def valid_map() -> MapData:
    return _make_map()


class TestValidateMapDataValid:
    def test_valid_map_has_no_errors(self, valid_map: MapData) -> None:
        assert validate_map_data(valid_map).is_valid

    def test_valid_map_has_no_warnings(self, valid_map: MapData) -> None:
        assert validate_map_data(valid_map).warnings == []

    def test_no_trains_is_valid(self) -> None:
        assert validate_map_data(_make_map(trains=[])).is_valid


class TestValidateMapDataGridDimensions:
    def test_zero_width(self) -> None:
        result = validate_map_data(_make_map(width=0))
        codes = [e.code for e in result.errors]
        assert "INVALID_WIDTH" in codes

    def test_negative_width(self) -> None:
        result = validate_map_data(_make_map(width=-5))
        assert any(e.code == "INVALID_WIDTH" for e in result.errors)

    def test_zero_height(self) -> None:
        result = validate_map_data(_make_map(height=0))
        assert any(e.code == "INVALID_HEIGHT" for e in result.errors)


class TestValidateMapDataNodeIds:
    def test_duplicate_node_id(self) -> None:
        nodes = [
            NodeRow(id=1, type=NodeType.station, x=0, y=0, name="A"),
            NodeRow(id=1, type=NodeType.station, x=1, y=1, name="B"),
        ]
        result = validate_map_data(_make_map(nodes=nodes, edges=[], trains=[]))
        assert any(e.code == "DUPLICATE_NODE_ID" for e in result.errors)

    def test_unique_node_ids_no_error(self, valid_map: MapData) -> None:
        result = validate_map_data(valid_map)
        assert not any(e.code == "DUPLICATE_NODE_ID" for e in result.errors)


class TestValidateMapDataNodeBounds:
    def test_x_at_grid_width_is_out_of_bounds(self) -> None:
        nodes = [NodeRow(id=1, type=NodeType.station, x=20, y=0, name="A")]
        result = validate_map_data(_make_map(width=20, height=15, nodes=nodes, edges=[], trains=[]))
        assert any(e.code == "NODE_OUT_OF_BOUNDS" for e in result.errors)

    def test_x_equals_width_minus_one_is_valid(self) -> None:
        nodes = [NodeRow(id=1, type=NodeType.station, x=19, y=0, name="A")]
        result = validate_map_data(_make_map(width=20, height=15, nodes=nodes, edges=[], trains=[]))
        assert not any(e.code == "NODE_OUT_OF_BOUNDS" for e in result.errors)

    def test_y_at_grid_height_is_out_of_bounds(self) -> None:
        nodes = [NodeRow(id=1, type=NodeType.station, x=0, y=15, name="A")]
        result = validate_map_data(_make_map(width=20, height=15, nodes=nodes, edges=[], trains=[]))
        assert any(e.code == "NODE_OUT_OF_BOUNDS" for e in result.errors)

    def test_negative_x(self) -> None:
        nodes = [NodeRow(id=1, type=NodeType.station, x=-1, y=0, name="A")]
        result = validate_map_data(_make_map(nodes=nodes, edges=[], trains=[]))
        assert any(e.code == "NODE_OUT_OF_BOUNDS" for e in result.errors)


class TestValidateMapDataEdges:
    def test_self_loop_edge(self) -> None:
        nodes = [NodeRow(id=1, type=NodeType.station, x=0, y=0, name="A")]
        edges = [EdgeRow(from_id=1, to_id=1, distance=1.0)]
        result = validate_map_data(_make_map(nodes=nodes, edges=edges, trains=[]))
        assert any(e.code == "SELF_LOOP_EDGE" for e in result.errors)

    def test_negative_cost(self) -> None:
        edges = [
            EdgeRow(from_id=1, to_id=3, cost=-10, distance=8.0, direction=Direction.bidirectional),
            EdgeRow(from_id=3, to_id=2, cost=150, distance=10.0, direction=Direction.bidirectional),
        ]
        result = validate_map_data(_make_map(edges=edges))
        assert any(e.code == "NEGATIVE_EDGE_COST" for e in result.errors)

    def test_zero_cost_is_valid(self) -> None:
        edges = [
            EdgeRow(from_id=1, to_id=3, cost=0, distance=8.0, direction=Direction.bidirectional),
            EdgeRow(from_id=3, to_id=2, cost=150, distance=10.0, direction=Direction.bidirectional),
        ]
        result = validate_map_data(_make_map(edges=edges))
        assert not any(e.code == "NEGATIVE_EDGE_COST" for e in result.errors)

    def test_zero_distance(self) -> None:
        edges = [
            EdgeRow(from_id=1, to_id=3, cost=100, distance=0.0, direction=Direction.bidirectional),
            EdgeRow(from_id=3, to_id=2, cost=150, distance=10.0, direction=Direction.bidirectional),
        ]
        result = validate_map_data(_make_map(edges=edges))
        assert any(e.code == "NON_POSITIVE_DISTANCE" for e in result.errors)

    def test_negative_distance(self) -> None:
        edges = [
            EdgeRow(from_id=1, to_id=3, cost=100, distance=-5.0, direction=Direction.bidirectional),
            EdgeRow(from_id=3, to_id=2, cost=150, distance=10.0, direction=Direction.bidirectional),
        ]
        result = validate_map_data(_make_map(edges=edges))
        assert any(e.code == "NON_POSITIVE_DISTANCE" for e in result.errors)


class TestValidateMapDataTrains:
    def test_duplicate_train_id(self) -> None:
        trains = [
            TrainRow(id=1, origin_id=1, destination_id=2),
            TrainRow(id=1, origin_id=2, destination_id=1),
        ]
        result = validate_map_data(_make_map(trains=trains))
        assert any(e.code == "DUPLICATE_TRAIN_ID" for e in result.errors)


class TestValidateMapDataWarnings:
    def test_duplicate_position_is_warning_not_error(self) -> None:
        nodes = [
            NodeRow(id=1, type=NodeType.station, x=5, y=5, name="A"),
            NodeRow(id=2, type=NodeType.station, x=5, y=5, name="B"),
        ]
        result = validate_map_data(_make_map(nodes=nodes, edges=[], trains=[]))
        assert result.is_valid
        assert any(w.code == "DUPLICATE_NODE_POSITION" for w in result.warnings)


class TestValidateRailGraphValid:
    def test_valid_graph_has_no_errors(self, valid_map: MapData) -> None:
        graph = build_graph(valid_map)
        assert validate_rail_graph(graph, valid_map).is_valid

    def test_no_trains_is_valid(self) -> None:
        data = _make_map(trains=[])
        graph = build_graph(data)
        assert validate_rail_graph(graph, data).is_valid


class TestValidateRailGraphTrainEndpoints:
    def test_origin_not_station(self) -> None:
        trains = [TrainRow(id=1, origin_id=3, destination_id=2)]
        data = _make_map(trains=trains)
        graph = build_graph(data)
        result = validate_rail_graph(graph, data)
        assert any(e.code == "TRAIN_ORIGIN_NOT_STATION" for e in result.errors)

    def test_destination_not_station(self) -> None:
        trains = [TrainRow(id=1, origin_id=1, destination_id=3)]
        data = _make_map(trains=trains)
        graph = build_graph(data)
        result = validate_rail_graph(graph, data)
        assert any(e.code == "TRAIN_DESTINATION_NOT_STATION" for e in result.errors)


class TestValidateRailGraphConnectivity:
    def test_no_path_raises_error(self) -> None:
        nodes = [
            NodeRow(id=1, type=NodeType.station, x=0, y=0, name="A"),
            NodeRow(id=2, type=NodeType.station, x=9, y=9, name="B"),
        ]
        trains = [TrainRow(id=1, origin_id=1, destination_id=2)]
        data = _make_map(nodes=nodes, edges=[], trains=trains)
        graph = build_graph(data)
        result = validate_rail_graph(graph, data)
        assert any(e.code == "NO_PATH" for e in result.errors)

    def test_connected_graph_no_path_error(self, valid_map: MapData) -> None:
        graph = build_graph(valid_map)
        result = validate_rail_graph(graph, valid_map)
        assert not any(e.code == "NO_PATH" for e in result.errors)


class TestValidateRailGraphWarnings:
    def test_isolated_node_is_warning(self) -> None:
        nodes = [
            NodeRow(id=1, type=NodeType.station, x=0, y=0, name="A"),
            NodeRow(id=2, type=NodeType.station, x=9, y=9, name="B"),
            NodeRow(id=3, type=NodeType.junction, x=5, y=5, name="Orphan"),
        ]
        edges = [
            EdgeRow(from_id=1, to_id=2, cost=10, distance=5.0, direction=Direction.bidirectional),
        ]
        trains = [TrainRow(id=1, origin_id=1, destination_id=2)]
        data = _make_map(nodes=nodes, edges=edges, trains=trains)
        graph = build_graph(data)
        result = validate_rail_graph(graph, data)
        assert result.is_valid
        assert any(w.code == "ISOLATED_NODE" for w in result.warnings)

    def test_no_isolated_nodes_no_warning(self, valid_map: MapData) -> None:
        graph = build_graph(valid_map)
        result = validate_rail_graph(graph, valid_map)
        assert not any(w.code == "ISOLATED_NODE" for w in result.warnings)
