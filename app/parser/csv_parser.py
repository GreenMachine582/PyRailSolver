import csv
import io
from collections.abc import Mapping
from pathlib import Path

from app.parser.models import EdgeRow, MapData, MapMeta, NodeRow, TrainRow


class MapParseError(ValueError):
    """Raised when a map CSV file is invalid or malformed."""


def _split_sections(text: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            current = stripped[1:-1].lower()
            sections[current] = []
        elif current is not None:
            sections[current].append(line)
    return {k: "\n".join(v) for k, v in sections.items()}


def _parse_csv_block(block: str) -> list[dict[str, str]]:
    reader = csv.DictReader(io.StringIO(block.strip()))
    return [dict(row) for row in reader]


def _clean(row: Mapping[str, str | None]) -> dict[str, str]:
    """Strip whitespace and drop empty values so Pydantic uses field defaults."""
    return {k.strip(): v.strip() for k, v in row.items() if v is not None and v.strip()}


def _parse_meta(block: str) -> MapMeta:
    rows = _parse_csv_block(block)
    if len(rows) != 1:
        raise MapParseError(f"[map] section must have exactly one data row, got {len(rows)}")
    try:
        return MapMeta.model_validate(_clean(rows[0]))
    except Exception as exc:
        raise MapParseError(f"Invalid [map] section: {exc}") from exc


def _parse_nodes(block: str) -> list[NodeRow]:
    nodes = []
    for i, row in enumerate(_parse_csv_block(block), start=1):
        try:
            nodes.append(NodeRow.model_validate(_clean(row)))
        except Exception as exc:
            raise MapParseError(f"Invalid node at row {i}: {exc}") from exc
    return nodes


def _parse_edges(block: str) -> list[EdgeRow]:
    edges = []
    for i, row in enumerate(_parse_csv_block(block), start=1):
        try:
            edges.append(EdgeRow.model_validate(_clean(row)))
        except Exception as exc:
            raise MapParseError(f"Invalid edge at row {i}: {exc}") from exc
    return edges


def _parse_trains(block: str) -> list[TrainRow]:
    trains = []
    for i, row in enumerate(_parse_csv_block(block), start=1):
        try:
            trains.append(TrainRow.model_validate(_clean(row)))
        except Exception as exc:
            raise MapParseError(f"Invalid train at row {i}: {exc}") from exc
    return trains


def _validate_references(data: MapData) -> None:
    node_ids = {n.id for n in data.nodes}
    for i, edge in enumerate(data.edges, start=1):
        if edge.from_id not in node_ids:
            raise MapParseError(f"Edge row {i}: unknown from_id {edge.from_id}")
        if edge.to_id not in node_ids:
            raise MapParseError(f"Edge row {i}: unknown to_id {edge.to_id}")
    for i, train in enumerate(data.trains, start=1):
        if train.origin_id not in node_ids:
            raise MapParseError(f"Train row {i}: unknown origin_id {train.origin_id}")
        if train.destination_id not in node_ids:
            raise MapParseError(f"Train row {i}: unknown destination_id {train.destination_id}")


def parse_map(path: Path) -> MapData:
    """Parse a multi-section CSV map file and return a validated MapData object."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise MapParseError(f"Cannot read map file '{path}': {exc}") from exc

    sections = _split_sections(text)

    for required in ("map", "nodes", "edges", "trains"):
        if required not in sections:
            raise MapParseError(f"Missing required section: [{required}]")

    data = MapData(
        meta=_parse_meta(sections["map"]),
        nodes=_parse_nodes(sections["nodes"]),
        edges=_parse_edges(sections["edges"]),
        trains=_parse_trains(sections["trains"]),
    )
    _validate_references(data)
    return data
