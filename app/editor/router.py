from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, Response

from app.editor.state import editor
from app.graph.rail_graph import build_graph
from app.parser.models import Direction, NodeType
from app.renderer import render_map
from app.ui import templates

router = APIRouter(prefix="/editor", tags=["editor"])


@router.get("", response_class=HTMLResponse)
async def editor_page(request: Request) -> Response:
    map_data = editor.map_data
    graph = build_graph(map_data)
    return templates.TemplateResponse(
        request,
        "editor.html",
        {"map_data": map_data, "svg": render_map(map_data, graph)},
    )


@router.post("/nodes", response_class=HTMLResponse)
async def add_node(
    request: Request,
    x: int = Form(...),
    y: int = Form(...),
    node_type: str = Form("station"),
    name: str = Form(""),
) -> Response:
    map_data = editor.map_data
    if not (0 <= x < map_data.meta.width and 0 <= y < map_data.meta.height):
        raise HTTPException(status_code=422, detail="Coordinates out of bounds")
    try:
        nt = NodeType(node_type)
    except ValueError:
        raise HTTPException(
            status_code=422, detail=f"Unknown node type: {node_type!r}"
        ) from None
    editor.add_node(nt, x, y, name.strip())
    map_data = editor.map_data
    graph = build_graph(map_data)
    return templates.TemplateResponse(
        request,
        "partials/editor_canvas.html",
        {"map_data": map_data, "svg": render_map(map_data, graph)},
    )


@router.post("/edges", response_class=HTMLResponse)
async def add_edge(
    request: Request,
    from_id: int = Form(...),
    to_id: int = Form(...),
    direction: str = Form("bidirectional"),
    cost: int = Form(0),
    distance: float = Form(1.0),
    capacity: int = Form(1),
    speed_limit: int = Form(100),
) -> Response:
    node_ids = {n.id for n in editor.map_data.nodes}
    if from_id not in node_ids:
        raise HTTPException(status_code=422, detail=f"from_id {from_id} not found")
    if to_id not in node_ids:
        raise HTTPException(status_code=422, detail=f"to_id {to_id} not found")
    if from_id == to_id:
        raise HTTPException(status_code=422, detail="from_id and to_id must differ")
    try:
        dir_val = Direction(direction)
    except ValueError:
        raise HTTPException(
            status_code=422, detail=f"Invalid direction: {direction!r}"
        ) from None
    editor.add_edge(from_id, to_id, dir_val, cost, distance, capacity, speed_limit)
    map_data = editor.map_data
    graph = build_graph(map_data)
    return templates.TemplateResponse(
        request,
        "partials/editor_canvas.html",
        {"map_data": map_data, "svg": render_map(map_data, graph)},
    )
