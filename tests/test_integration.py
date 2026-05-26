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
        assert graph.node_count == 3

    def test_directed_edge_count(self, pipeline) -> None:  # type: ignore[no-untyped-def]
        # 2 bidirectional CSV edges → 4 directed edges
        _, graph = pipeline
        assert graph.edge_count == 4

    def test_station_count(self, pipeline) -> None:  # type: ignore[no-untyped-def]
        _, graph = pipeline
        assert len(graph.nodes_of_type(NodeType.station)) == 2

    def test_junction_count(self, pipeline) -> None:  # type: ignore[no-untyped-def]
        _, graph = pipeline
        assert len(graph.nodes_of_type(NodeType.junction)) == 1

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
