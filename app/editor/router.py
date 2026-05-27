from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, Response

from app.editor.state import editor
from app.graph.rail_graph import build_graph
from app.parser.models import NodeType
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
