"""
Integration tests for Milestone 1: load a map and display graph statistics.

Exercises the full pipeline: CSV parse → structural validation →
graph build → graph validation → statistics queries.
"""
from pathlib import Path

import pytest

from app.graph.rail_graph import build_graph
from app.graph.validation import validate_map_data, validate_rail_graph
from app.parser.csv_parser import parse_map
from app.parser.models import NodeType


class TestTutorial1Pipeline:
    """Full end-to-end pipeline using examples/tutorial_1.csv."""

    @pytest.fixture(scope="class")
    def pipeline(self):  # type: ignore[no-untyped-def]
        map_data = parse_map(Path("examples/tutorial_1.csv"))
        graph = build_graph(map_data)
        return map_data, graph

    def test_parse_succeeds(self, pipeline) -> None:  # type: ignore[no-untyped-def]
        map_data, _ = pipeline
        assert map_data is not None

    def test_map_data_is_valid(self, pipeline) -> None:  # type: ignore[no-untyped-def]
        map_data, _ = pipeline
        assert validate_map_data(map_data).is_valid

    def test_graph_is_valid(self, pipeline) -> None:  # type: ignore[no-untyped-def]
        map_data, graph = pipeline
        assert validate_rail_graph(graph, map_data).is_valid

    # --- graph statistics ---

    def test_node_count(self, pipeline) -> None:  # type: ignore[no-untyped-def]
        _, graph = pipeline
        assert graph.node_count == 7

    def test_directed_edge_count(self, pipeline) -> None:  # type: ignore[no-untyped-def]
        # 4 bidir CSV edges → 8 directed + 3 forward CSV edges = 11 directed total
        _, graph = pipeline
        assert graph.edge_count == 11

    def test_station_count(self, pipeline) -> None:  # type: ignore[no-untyped-def]
        _, graph = pipeline
        assert len(graph.nodes_of_type(NodeType.station)) == 2

    def test_junction_count(self, pipeline) -> None:  # type: ignore[no-untyped-def]
        _, graph = pipeline
        assert len(graph.nodes_of_type(NodeType.junction)) == 1

    def test_platform_count(self, pipeline) -> None:  # type: ignore[no-untyped-def]
        _, graph = pipeline
        assert len(graph.nodes_of_type(NodeType.platform)) == 1

    def test_depot_count(self, pipeline) -> None:  # type: ignore[no-untyped-def]
        _, graph = pipeline
        assert len(graph.nodes_of_type(NodeType.depot)) == 1

    def test_waypoint_count(self, pipeline) -> None:  # type: ignore[no-untyped-def]
        _, graph = pipeline
        assert len(graph.nodes_of_type(NodeType.waypoint)) == 1

    def test_endpoint_count(self, pipeline) -> None:  # type: ignore[no-untyped-def]
        _, graph = pipeline
        assert len(graph.nodes_of_type(NodeType.endpoint)) == 1

    def test_has_directed_edges(self, pipeline) -> None:  # type: ignore[no-untyped-def]
        _, graph = pipeline
        # forward-only edges exist (e.g. junction → depot has no reverse)
        assert not graph.has_reverse_edge(3, 5)
        assert not graph.has_reverse_edge(1, 6)
        assert not graph.has_reverse_edge(3, 7)

    def test_bidirectional_edges_present(self, pipeline) -> None:  # type: ignore[no-untyped-def]
        _, graph = pipeline
        assert graph.has_reverse_edge(1, 3)
        assert graph.has_reverse_edge(3, 2)
        assert graph.has_reverse_edge(6, 2)

    def test_return_train_routable(self, pipeline) -> None:  # type: ignore[no-untyped-def]
        map_data, graph = pipeline
        # train 2 is Power Plant → Coal Mine
        return_train = next(t for t in map_data.trains if t.id == 2)
        assert graph.has_path(return_train.origin_id, return_train.destination_id)

    def test_train_cargo(self, pipeline) -> None:  # type: ignore[no-untyped-def]
        map_data, _ = pipeline
        assert map_data.trains[0].cargo == "coal"
        assert map_data.trains[1].cargo == ""

    def test_train_spawn_ticks(self, pipeline) -> None:  # type: ignore[no-untyped-def]
        map_data, _ = pipeline
        assert map_data.trains[0].spawn_tick == 0
        assert map_data.trains[1].spawn_tick == 5

    def test_all_trains_routable(self, pipeline) -> None:  # type: ignore[no-untyped-def]
        map_data, graph = pipeline
        for train in map_data.trains:
            assert graph.has_path(train.origin_id, train.destination_id), (
                f"Train {train.id}: no path from {train.origin_id} to {train.destination_id}"
            )

    def test_route_is_bidirectional(self, pipeline) -> None:  # type: ignore[no-untyped-def]
        map_data, graph = pipeline
        for train in map_data.trains:
            assert graph.has_path(train.destination_id, train.origin_id)

    def test_map_name(self, pipeline) -> None:  # type: ignore[no-untyped-def]
        map_data, _ = pipeline
        assert map_data.meta.name == "Tutorial 1"

    def test_grid_dimensions(self, pipeline) -> None:  # type: ignore[no-untyped-def]
        map_data, _ = pipeline
        assert map_data.meta.width == 20
        assert map_data.meta.height == 15
