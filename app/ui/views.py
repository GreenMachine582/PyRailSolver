from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, Response

from app.api.maps import MapStatsResponse, find_map_file, map_names
from app.graph.rail_graph import build_graph
from app.graph.validation import validate_map_data, validate_rail_graph
from app.parser.csv_parser import MapParseError, parse_map
from app.parser.models import NodeType
from app.ui import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def index(request: Request) -> Response:
    return templates.TemplateResponse(request, "index.html", {"maps": map_names()})


@router.get("/maps/{name}", response_class=HTMLResponse)
async def map_viewer(request: Request, name: str) -> Response:
    path = find_map_file(name)
    try:
        map_data = parse_map(path)
    except MapParseError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    graph = build_graph(map_data)
    data_result = validate_map_data(map_data)
    graph_result = validate_rail_graph(graph, map_data)

    return templates.TemplateResponse(
        request,
        "map.html",
        {
            "map_data": map_data,
            "stats": MapStatsResponse(
                node_count=graph.node_count,
                edge_count=graph.edge_count,
                train_count=len(map_data.trains),
                station_count=len(graph.nodes_of_type(NodeType.station)),
            ),
            "is_valid": data_result.is_valid and graph_result.is_valid,
            "errors": [e.message for e in data_result.errors + graph_result.errors],
            "warnings": [w.message for w in data_result.warnings + graph_result.warnings],
        },
    )
