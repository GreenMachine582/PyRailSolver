from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core import settings
from app.graph.rail_graph import build_graph
from app.graph.validation import validate_map_data, validate_rail_graph
from app.parser.csv_parser import MapParseError, parse_map
from app.parser.models import EdgeRow, MapMeta, NodeRow, NodeType, TrainRow

router = APIRouter(prefix="/api/maps", tags=["maps"])

_PROJECT_ROOT = Path(__file__).parents[2]


def _map_files() -> list[Path]:
    dirs = [_PROJECT_ROOT / settings.examples_dir, _PROJECT_ROOT / settings.maps_dir]
    files: list[Path] = []
    for d in dirs:
        if d.is_dir():
            files.extend(sorted(d.glob("*.csv")))
    return files


def map_names() -> list[str]:
    return [f.stem for f in _map_files()]


def find_map_file(name: str) -> Path:
    for path in _map_files():
        if path.stem == name:
            return path
    raise HTTPException(status_code=404, detail=f"Map '{name}' not found")


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


@router.get("", response_model=list[str])
async def list_maps() -> list[str]:
    return map_names()


@router.get("/{name}", response_model=MapDataResponse)
async def get_map(name: str) -> MapDataResponse:
    path = find_map_file(name)
    try:
        map_data = parse_map(path)
    except MapParseError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

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
