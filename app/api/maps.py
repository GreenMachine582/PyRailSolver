from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ValidationError

from app.core import settings
from app.graph.rail_graph import build_graph
from app.graph.validation import validate_map_data, validate_rail_graph
from app.parser.csv_parser import MapParseError, parse_map
from app.parser.models import EdgeRow, MapData, MapMeta, NodeRow, NodeType, TrainRow

router = APIRouter(prefix="/api/maps", tags=["maps"])

_PROJECT_ROOT = Path(__file__).parents[2]


def _maps_dir() -> Path:
    return _PROJECT_ROOT / settings.maps_dir


def _map_files() -> list[Path]:
    # Collect CSV maps from examples and maps dirs, then overlay JSON maps from
    # maps_dir — a saved JSON map takes precedence over a same-stem CSV.
    by_stem: dict[str, Path] = {}
    for d in [_PROJECT_ROOT / settings.examples_dir, _PROJECT_ROOT / settings.maps_dir]:
        if d.is_dir():
            for f in sorted(d.glob("*.csv")):
                by_stem.setdefault(f.stem, f)
    md = _maps_dir()
    if md.is_dir():
        for f in sorted(md.glob("*.json")):
            by_stem[f.stem] = f
    return sorted(by_stem.values(), key=lambda p: p.stem)


def _is_editable(path: Path) -> bool:
    try:
        path.relative_to(_maps_dir())
        return True
    except ValueError:
        return False


def map_names() -> list[str]:
    return [f.stem for f in _map_files()]


def find_map_file(name: str) -> Path:
    for path in _map_files():
        if path.stem == name:
            return path
    raise HTTPException(status_code=404, detail=f"Map '{name}' not found")


class MapListItem(BaseModel):
    name: str
    editable: bool


class MapStatsResponse(BaseModel):
    node_count: int
    edge_count: int
    train_count: int
    station_count: int


class MapDataResponse(BaseModel):
    meta: MapMeta
    nodes: list[NodeRow]
    edges: list[EdgeRow]
    trains: list[TrainRow]
    stats: MapStatsResponse
    is_valid: bool
    errors: list[str]
    warnings: list[str]


@router.get("", response_model=list[MapListItem])
async def list_maps() -> list[MapListItem]:
    return [MapListItem(name=f.stem, editable=_is_editable(f)) for f in _map_files()]


@router.delete("/{name}")
async def delete_map(name: str) -> dict[str, str]:
    path = find_map_file(name)
    if not _is_editable(path):
        raise HTTPException(status_code=403, detail="Example maps cannot be deleted")
    path.unlink()
    return {"deleted": name}


def load_map_file(path: Path) -> MapData:
    if path.suffix == ".json":
        try:
            return MapData.model_validate_json(path.read_text(encoding="utf-8"))
        except (ValidationError, ValueError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
    try:
        return parse_map(path)
    except MapParseError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/{name}", response_model=MapDataResponse)
async def get_map(name: str) -> MapDataResponse:
    path = find_map_file(name)
    map_data = load_map_file(path)

    graph = build_graph(map_data)
    data_result = validate_map_data(map_data)
    graph_result = validate_rail_graph(graph, map_data)

    return MapDataResponse(
        meta=map_data.meta,
        nodes=map_data.nodes,
        edges=map_data.edges,
        trains=map_data.trains,
        stats=MapStatsResponse(
            node_count=graph.node_count,
            edge_count=graph.edge_count,
            train_count=len(map_data.trains),
            station_count=len(graph.nodes_of_type(NodeType.station)),
        ),
        is_valid=data_result.is_valid and graph_result.is_valid,
        errors=[e.message for e in data_result.errors + graph_result.errors],
        warnings=[w.message for w in data_result.warnings + graph_result.warnings],
    )
