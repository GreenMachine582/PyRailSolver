from app.graph.rail_graph import build_graph
from app.parser.models import Direction, EdgeRow, MapData, MapMeta, NodeRow, NodeType, TrainRow
from app.renderer.svg import render_map


def _make_map(
    nodes: list[NodeRow] | None = None,
    edges: list[EdgeRow] | None = None,
    trains: list[TrainRow] | None = None,
) -> MapData:
    default_nodes = [
        NodeRow(id=1, type=NodeType.station, x=2, y=3, name="A"),
        NodeRow(id=2, type=NodeType.station, x=8, y=7, name="B"),
    ]
    default_edges = [EdgeRow(from_id=1, to_id=2, direction=Direction.bidirectional)]
    return MapData(
        meta=MapMeta(name="Test", width=10, height=10),
        nodes=nodes if nodes is not None else default_nodes,
        edges=edges if edges is not None else default_edges,
        trains=trains if trains is not None else [],
    )


class TestRenderMap:
    def test_returns_svg_string(self) -> None:
        svg = render_map(_make_map(), build_graph(_make_map()))
        assert svg.startswith("<svg")
        assert svg.endswith("</svg>")

    def test_contains_node_circles(self) -> None:
        map_data = _make_map()
        svg = render_map(map_data, build_graph(map_data))
        assert svg.count("<circle") >= 2

    def test_contains_edge_line(self) -> None:
        map_data = _make_map()
        svg = render_map(map_data, build_graph(map_data))
        assert "<line" in svg

    def test_bidirectional_edge_drawn_once(self) -> None:
        map_data = _make_map()
        svg = render_map(map_data, build_graph(map_data))
        assert svg.count("<line") == 1

    def test_forward_edge_is_polyline(self) -> None:
        map_data = _make_map(edges=[EdgeRow(from_id=1, to_id=2, direction=Direction.forward)])
        svg = render_map(map_data, build_graph(map_data))
        assert svg.count("<polyline") == 1
        assert "<line" not in svg.split('<g class="edges">')[1].split("</g>")[0]

    def test_bidirectional_edge_is_line(self) -> None:
        map_data = _make_map()
        svg = render_map(map_data, build_graph(map_data))
        assert "<line" in svg
        assert "<polyline" not in svg

    def test_directed_edge_has_arrow_marker(self) -> None:
        map_data = _make_map(edges=[EdgeRow(from_id=1, to_id=2, direction=Direction.forward)])
        svg = render_map(map_data, build_graph(map_data))
        assert 'marker-mid="url(#arrow)"' in svg
        assert 'id="arrow"' in svg

    def test_bidirectional_edge_no_arrow_defs(self) -> None:
        map_data = _make_map()
        svg = render_map(map_data, build_graph(map_data))
        assert 'id="arrow"' not in svg

    def test_edge_title_has_cost(self) -> None:
        map_data = _make_map(
            edges=[EdgeRow(from_id=1, to_id=2, cost=50, direction=Direction.bidirectional)]
        )
        svg = render_map(map_data, build_graph(map_data))
        assert "Cost: 50" in svg

    def test_edge_title_has_distance(self) -> None:
        map_data = _make_map(
            edges=[EdgeRow(from_id=1, to_id=2, distance=3.5, direction=Direction.bidirectional)]
        )
        svg = render_map(map_data, build_graph(map_data))
        assert "Dist: 3.5" in svg

    def test_edge_title_has_speed(self) -> None:
        map_data = _make_map(
            edges=[EdgeRow(from_id=1, to_id=2, speed_limit=80, direction=Direction.bidirectional)]
        )
        svg = render_map(map_data, build_graph(map_data))
        assert "Speed: 80" in svg

    def test_no_edges(self) -> None:
        map_data = _make_map(edges=[])
        svg = render_map(map_data, build_graph(map_data))
        assert "<line" not in svg

    def test_node_label_escaped(self) -> None:
        map_data = _make_map(nodes=[
            NodeRow(id=1, type=NodeType.station, x=1, y=1, name="A&B"),
            NodeRow(id=2, type=NodeType.station, x=5, y=5, name="C"),
        ])
        svg = render_map(map_data, build_graph(map_data))
        assert "A&amp;B" in svg
        assert "A&B" not in svg

    def test_station_color(self) -> None:
        map_data = _make_map()
        svg = render_map(map_data, build_graph(map_data))
        assert "#0d6efd" in svg

    def test_junction_color(self) -> None:
        map_data = _make_map(
            nodes=[
                NodeRow(id=1, type=NodeType.station, x=0, y=0, name="A"),
                NodeRow(id=2, type=NodeType.junction, x=5, y=5),
                NodeRow(id=3, type=NodeType.station, x=9, y=9, name="B"),
            ],
            edges=[EdgeRow(from_id=1, to_id=2), EdgeRow(from_id=2, to_id=3)],
        )
        svg = render_map(map_data, build_graph(map_data))
        assert "#6c757d" in svg

    def test_depot_color(self) -> None:
        map_data = _make_map(
            nodes=[NodeRow(id=1, type=NodeType.depot, x=3, y=3, name="D")],
            edges=[],
        )
        svg = render_map(map_data, build_graph(map_data))
        assert "#fd7e14" in svg

    def test_waypoint_color(self) -> None:
        map_data = _make_map(
            nodes=[NodeRow(id=1, type=NodeType.waypoint, x=3, y=3, name="W")],
            edges=[],
        )
        svg = render_map(map_data, build_graph(map_data))
        assert "#198754" in svg

    def test_platform_color(self) -> None:
        map_data = _make_map(
            nodes=[NodeRow(id=1, type=NodeType.platform, x=3, y=3, name="P")],
            edges=[],
        )
        svg = render_map(map_data, build_graph(map_data))
        assert "#6ea8fe" in svg

    def test_endpoint_color(self) -> None:
        map_data = _make_map(
            nodes=[NodeRow(id=1, type=NodeType.endpoint, x=3, y=3, name="E")],
            edges=[],
        )
        svg = render_map(map_data, build_graph(map_data))
        assert "#dc3545" in svg

    def test_svg_dimensions(self) -> None:
        map_data = _make_map()
        svg = render_map(map_data, build_graph(map_data))
        assert 'width="460"' in svg
        assert 'height="460"' in svg

    def test_fallback_label_uses_node_type(self) -> None:
        map_data = _make_map(
            nodes=[NodeRow(id=1, type=NodeType.junction, x=3, y=3)],
            edges=[],
        )
        svg = render_map(map_data, build_graph(map_data))
        assert "junction" in svg

    def test_grid_dots_present(self) -> None:
        map_data = _make_map()
        svg = render_map(map_data, build_graph(map_data))
        assert 'class="grid"' in svg

    def test_svg_has_id(self) -> None:
        map_data = _make_map()
        svg = render_map(map_data, build_graph(map_data))
        assert 'id="map-svg"' in svg

    def test_node_has_popover_toggle(self) -> None:
        map_data = _make_map()
        svg = render_map(map_data, build_graph(map_data))
        assert 'data-bs-toggle="popover"' in svg

    def test_node_popover_title_is_name(self) -> None:
        map_data = _make_map()
        svg = render_map(map_data, build_graph(map_data))
        assert 'data-bs-title="A"' in svg

    def test_node_popover_content_has_type_and_pos(self) -> None:
        map_data = _make_map()
        svg = render_map(map_data, build_graph(map_data))
        assert "Type: station" in svg
        assert "(2, 3)" in svg

    def test_node_popover_title_escaped(self) -> None:
        map_data = _make_map(nodes=[
            NodeRow(id=1, type=NodeType.station, x=1, y=1, name='A"B'),
        ], edges=[])
        svg = render_map(map_data, build_graph(map_data))
        assert 'A&quot;B' in svg
        assert 'A"B' not in svg
