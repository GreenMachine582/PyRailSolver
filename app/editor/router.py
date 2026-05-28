from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, Response

from app.editor.state import editor
from app.graph.rail_graph import build_graph
from app.parser.models import Direction, MapData, NodeType
from app.renderer import render_map
from app.ui import templates

router = APIRouter(prefix="/editor", tags=["editor"])


def _canvas_response(request: Request) -> Response:
    map_data = editor.map_data
    graph = build_graph(map_data)
    return templates.TemplateResponse(
        request,
        "partials/editor_canvas.html",
        {"map_data": map_data, "svg": render_map(map_data, graph)},
    )


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
    return _canvas_response(request)


@router.put("/nodes/{node_id}", response_class=HTMLResponse)
async def update_node(
    request: Request,
    node_id: int,
    node_type: str = Form("station"),
    name: str = Form(""),
) -> Response:
    try:
        nt = NodeType(node_type)
    except ValueError:
        raise HTTPException(
            status_code=422, detail=f"Unknown node type: {node_type!r}"
        ) from None
    if not editor.update_node(node_id, name.strip(), nt):
        raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
    return _canvas_response(request)


@router.delete("/nodes/{node_id}", response_class=HTMLResponse)
async def delete_node(request: Request, node_id: int) -> Response:
    if not editor.delete_node(node_id):
        raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
    return _canvas_response(request)


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
    return _canvas_response(request)


@router.put("/edges/{edge_index}", response_class=HTMLResponse)
async def update_edge(
    request: Request,
    edge_index: int,
    direction: str = Form("bidirectional"),
    cost: int = Form(0),
    distance: float = Form(1.0),
    capacity: int = Form(1),
    speed_limit: int = Form(100),
) -> Response:
    try:
        dir_val = Direction(direction)
    except ValueError:
        raise HTTPException(
            status_code=422, detail=f"Invalid direction: {direction!r}"
        ) from None
    if not editor.update_edge(edge_index, dir_val, cost, distance, capacity, speed_limit):
        raise HTTPException(status_code=404, detail=f"Edge index {edge_index} not found")
    return _canvas_response(request)


@router.delete("/edges/{edge_index}", response_class=HTMLResponse)
async def delete_edge(request: Request, edge_index: int) -> Response:
    if not editor.delete_edge(edge_index):
        raise HTTPException(status_code=404, detail=f"Edge index {edge_index} not found")
    return _canvas_response(request)


@router.get("/export")
async def export_map() -> Response:
    json_bytes = editor.map_data.model_dump_json(indent=2).encode()
    return Response(
        content=json_bytes,
        media_type="application/json",
        headers={"Content-Disposition": 'attachment; filename="map.json"'},
    )


@router.post("/load")
async def load_map(file: UploadFile = File(...)) -> Response:
    try:
        content = await file.read()
        data = MapData.model_validate_json(content)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Invalid map file: {exc}") from exc
    editor.load(data)
    return Response(status_code=200, headers={"HX-Redirect": "/editor"})
