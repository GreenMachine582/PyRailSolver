from pathlib import Path

import pytest

from app.parser.csv_parser import MapParseError, parse_map
from app.parser.models import Direction, NodeType

VALID_MAP = """\
[map]
name,width,height
Tutorial 1,20,15

[nodes]
id,type,x,y,name,capacity
1,station,2,3,Coal Mine,2
2,station,18,12,Power Plant,2
3,junction,10,7,,1

[edges]
from_id,to_id,cost,distance,capacity,direction,speed_limit
1,3,100,8,1,bidirectional,50
3,2,150,10,1,bidirectional,50

[trains]
id,origin_id,destination_id,cargo,speed,spawn_tick,priority
1,1,2,coal,40,0,1
"""


@pytest.fixture
def valid_map_file(tmp_path: Path) -> Path:
    p = tmp_path / "tutorial_1.csv"
    p.write_text(VALID_MAP, encoding="utf-8")
    return p


class TestParseMeta:
    def test_name(self, valid_map_file: Path) -> None:
        assert parse_map(valid_map_file).meta.name == "Tutorial 1"

    def test_width(self, valid_map_file: Path) -> None:
        assert parse_map(valid_map_file).meta.width == 20

    def test_height(self, valid_map_file: Path) -> None:
        assert parse_map(valid_map_file).meta.height == 15


class TestParseNodes:
    def test_node_count(self, valid_map_file: Path) -> None:
        assert len(parse_map(valid_map_file).nodes) == 3

    def test_station_type(self, valid_map_file: Path) -> None:
        assert parse_map(valid_map_file).nodes[0].type == NodeType.station

    def test_junction_type(self, valid_map_file: Path) -> None:
        assert parse_map(valid_map_file).nodes[2].type == NodeType.junction

    def test_coordinates(self, valid_map_file: Path) -> None:
        node = parse_map(valid_map_file).nodes[0]
        assert node.x == 2
        assert node.y == 3

    def test_name_populated(self, valid_map_file: Path) -> None:
        assert parse_map(valid_map_file).nodes[0].name == "Coal Mine"

    def test_name_defaults_to_empty(self, valid_map_file: Path) -> None:
        assert parse_map(valid_map_file).nodes[2].name == ""

    def test_capacity(self, valid_map_file: Path) -> None:
        assert parse_map(valid_map_file).nodes[0].capacity == 2


class TestParseEdges:
    def test_edge_count(self, valid_map_file: Path) -> None:
        assert len(parse_map(valid_map_file).edges) == 2

    def test_from_to_ids(self, valid_map_file: Path) -> None:
        edge = parse_map(valid_map_file).edges[0]
        assert edge.from_id == 1
        assert edge.to_id == 3

    def test_direction(self, valid_map_file: Path) -> None:
        assert parse_map(valid_map_file).edges[0].direction == Direction.bidirectional

    def test_cost(self, valid_map_file: Path) -> None:
        assert parse_map(valid_map_file).edges[0].cost == 100

    def test_speed_limit(self, valid_map_file: Path) -> None:
        assert parse_map(valid_map_file).edges[0].speed_limit == 50


class TestParseTrains:
    def test_train_count(self, valid_map_file: Path) -> None:
        assert len(parse_map(valid_map_file).trains) == 1

    def test_origin_destination(self, valid_map_file: Path) -> None:
        train = parse_map(valid_map_file).trains[0]
        assert train.origin_id == 1
        assert train.destination_id == 2

    def test_cargo(self, valid_map_file: Path) -> None:
        assert parse_map(valid_map_file).trains[0].cargo == "coal"

    def test_speed(self, valid_map_file: Path) -> None:
        assert parse_map(valid_map_file).trains[0].speed == 40

    def test_spawn_tick(self, valid_map_file: Path) -> None:
        assert parse_map(valid_map_file).trains[0].spawn_tick == 0


class TestEdgeDefaults:
    def test_defaults_applied(self, tmp_path: Path) -> None:
        content = VALID_MAP.replace(
            "1,3,100,8,1,bidirectional,50\n3,2,150,10,1,bidirectional,50",
            "1,3,,,,,",
        )
        p = tmp_path / "defaults.csv"
        p.write_text(content, encoding="utf-8")
        edge = parse_map(p).edges[0]
        assert edge.cost == 0
        assert edge.distance == 1.0
        assert edge.capacity == 1
        assert edge.direction == Direction.bidirectional
        assert edge.speed_limit == 100


class TestEmptyTrains:
    def test_no_trains_is_valid(self, tmp_path: Path) -> None:
        content = """\
[map]
name,width,height
Empty Map,10,10

[nodes]
id,type,x,y,name,capacity
1,station,0,0,A,1
2,station,9,9,B,1

[edges]
from_id,to_id,cost,distance,capacity,direction,speed_limit
1,2,50,10,1,bidirectional,50

[trains]
id,origin_id,destination_id,cargo,speed,spawn_tick,priority
"""
        p = tmp_path / "no_trains.csv"
        p.write_text(content, encoding="utf-8")
        assert parse_map(p).trains == []


class TestExampleFile:
    def test_tutorial_1_loads(self) -> None:
        path = Path("examples/tutorial_1.csv")
        data = parse_map(path)
        assert data.meta.name == "Tutorial 1"
        assert len(data.nodes) == 3
        assert len(data.edges) == 2
        assert len(data.trains) == 1


class TestParseErrors:
    def test_missing_file(self, tmp_path: Path) -> None:
        with pytest.raises(MapParseError, match="Cannot read"):
            parse_map(tmp_path / "missing.csv")

    def test_missing_map_section(self, tmp_path: Path) -> None:
        p = tmp_path / "bad.csv"
        content = (
            "[nodes]\nid,type,x,y\n"
            "[edges]\nfrom_id,to_id\n"
            "[trains]\nid,origin_id,destination_id\n"
        )
        p.write_text(content, encoding="utf-8")
        with pytest.raises(MapParseError, match=r"\[map\]"):
            parse_map(p)

    def test_missing_nodes_section(self, tmp_path: Path) -> None:
        p = tmp_path / "bad.csv"
        content = (
            "[map]\nname,width,height\nTest,10,10\n"
            "[edges]\nfrom_id,to_id\n"
            "[trains]\nid,origin_id,destination_id\n"
        )
        p.write_text(content, encoding="utf-8")
        with pytest.raises(MapParseError, match=r"\[nodes\]"):
            parse_map(p)

    def test_map_section_multiple_rows(self, tmp_path: Path) -> None:
        content = (
            "[map]\nname,width,height\nMap1,10,10\nMap2,20,20\n"
            "[nodes]\nid,type,x,y\n"
            "[edges]\nfrom_id,to_id\n"
            "[trains]\nid,origin_id,destination_id\n"
        )
        p = tmp_path / "bad.csv"
        p.write_text(content, encoding="utf-8")
        with pytest.raises(MapParseError, match="exactly one"):
            parse_map(p)

    def test_invalid_node_type(self, tmp_path: Path) -> None:
        p = tmp_path / "bad.csv"
        p.write_text(VALID_MAP.replace("junction", "crossover"), encoding="utf-8")
        with pytest.raises(MapParseError, match="Invalid node"):
            parse_map(p)

    def test_edge_unknown_from_id(self, tmp_path: Path) -> None:
        p = tmp_path / "bad.csv"
        p.write_text(VALID_MAP.replace("1,3,100", "99,3,100"), encoding="utf-8")
        with pytest.raises(MapParseError, match="from_id 99"):
            parse_map(p)

    def test_edge_unknown_to_id(self, tmp_path: Path) -> None:
        p = tmp_path / "bad.csv"
        p.write_text(VALID_MAP.replace("1,3,100", "1,99,100"), encoding="utf-8")
        with pytest.raises(MapParseError, match="to_id 99"):
            parse_map(p)

    def test_train_unknown_origin(self, tmp_path: Path) -> None:
        p = tmp_path / "bad.csv"
        p.write_text(VALID_MAP.replace("1,1,2,coal", "1,99,2,coal"), encoding="utf-8")
        with pytest.raises(MapParseError, match="origin_id 99"):
            parse_map(p)

    def test_train_unknown_destination(self, tmp_path: Path) -> None:
        p = tmp_path / "bad.csv"
        p.write_text(VALID_MAP.replace("1,1,2,coal", "1,1,99,coal"), encoding="utf-8")
        with pytest.raises(MapParseError, match="destination_id 99"):
            parse_map(p)

    def test_invalid_meta_field_type(self, tmp_path: Path) -> None:
        p = tmp_path / "bad.csv"
        content = VALID_MAP.replace("Tutorial 1,20,15", "Tutorial 1,notanumber,15")
        p.write_text(content, encoding="utf-8")
        with pytest.raises(MapParseError, match=r"Invalid \[map\]"):
            parse_map(p)

    def test_invalid_edge_direction_value(self, tmp_path: Path) -> None:
        p = tmp_path / "bad.csv"
        content = VALID_MAP.replace("1,3,100,8,1,bidirectional,50", "1,3,100,8,1,sideways,50")
        p.write_text(content, encoding="utf-8")
        with pytest.raises(MapParseError, match="Invalid edge"):
            parse_map(p)

    def test_invalid_train_id_type(self, tmp_path: Path) -> None:
        p = tmp_path / "bad.csv"
        content = VALID_MAP.replace("1,1,2,coal,40,0,1", "notanint,1,2,coal,40,0,1")
        p.write_text(content, encoding="utf-8")
        with pytest.raises(MapParseError, match="Invalid train"):
            parse_map(p)
