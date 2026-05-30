import re

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel

from app.api.maps import find_map_file, load_map_file, map_names
from app.core.config import settings
from app.editor.state import editor
from app.parser.models import Direction, MapData, NodeType

router = APIRouter(prefix="/api/editor", tags=["editor-api"])


def _slugify(name: str) -> str:
    return re.sub(r"[^\w\-]", "_", name).strip("_") or "untitled"


class _AddNodeReq(BaseModel):
    x: int
    y: int
    node_type: str = "station"
    name: str = ""


class _UpdateNodeReq(BaseModel):
    node_type: str = "station"
    name: str = ""


class _MoveNodeReq(BaseModel):
    x: int
    y: int


class _AddEdgeReq(BaseModel):
    from_id: int
    to_id: int
    direction: str = "bidirectional"
    cost: int = 0
    distance: float = 1.0
    capacity: int = 1
    speed_limit: int = 100
    edge_type: str = settings.default_edge_type
    source_handle: str = ""
    target_handle: str = ""


class _UpdateEdgeReq(BaseModel):
    direction: str = "bidirectional"
    cost: int = 0
    distance: float = 1.0
    capacity: int = 1
    speed_limit: int = 100
    edge_type: str = settings.default_edge_type
    source_handle: str = ""
    target_handle: str = ""


def _nt(value: str) -> NodeType:
    try:
        return NodeType(value)
    except ValueError:
        raise HTTPException(status_code=422, detail=f"Unknown node type: {value!r}") from None


def _dir(value: str) -> Direction:
    try:
        return Direction(value)
    except ValueError:
        raise HTTPException(status_code=422, detail=f"Invalid direction: {value!r}") from None


@router.get("/state", response_model=MapData)
async def get_state() -> MapData:
    return editor.map_data


@router.post("/nodes", response_model=MapData)
async def add_node(req: _AddNodeReq) -> MapData:
    md = editor.map_data
    if not (0 <= req.x < md.meta.width and 0 <= req.y < md.meta.height):
        raise HTTPException(status_code=422, detail="Coordinates out of bounds")
    editor.add_node(_nt(req.node_type), req.x, req.y, req.name.strip())
    return editor.map_data


@router.put("/nodes/{node_id}", response_model=MapData)
async def update_node(node_id: int, req: _UpdateNodeReq) -> MapData:
    if not editor.update_node(node_id, req.name.strip(), _nt(req.node_type)):
        raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
    return editor.map_data


@router.patch("/nodes/{node_id}/position", response_model=MapData)
async def move_node(node_id: int, req: _MoveNodeReq) -> MapData:
    md = editor.map_data
    if not (0 <= req.x < md.meta.width and 0 <= req.y < md.meta.height):
        raise HTTPException(status_code=422, detail="Coordinates out of bounds")
    if not editor.move_node(node_id, req.x, req.y):
        raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
    return editor.map_data


@router.delete("/nodes/{node_id}", response_model=MapData)
async def delete_node(node_id: int) -> MapData:
    if not editor.delete_node(node_id):
        raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
    return editor.map_data


@router.post("/edges", response_model=MapData)
async def add_edge(req: _AddEdgeReq) -> MapData:
    ids = {n.id for n in editor.map_data.nodes}
    if req.from_id not in ids:
        raise HTTPException(status_code=422, detail=f"from_id {req.from_id} not found")
    if req.to_id not in ids:
        raise HTTPException(status_code=422, detail=f"to_id {req.to_id} not found")
    if req.from_id == req.to_id:
        raise HTTPException(status_code=422, detail="from_id and to_id must differ")
    editor.add_edge(req.from_id, req.to_id, _dir(req.direction),
                    req.cost, req.distance, req.capacity, req.speed_limit,
                    req.edge_type, req.source_handle, req.target_handle)
    return editor.map_data


@router.put("/edges/{edge_index}", response_model=MapData)
async def update_edge(edge_index: int, req: _UpdateEdgeReq) -> MapData:
    if not editor.update_edge(edge_index, _dir(req.direction),
                               req.cost, req.distance, req.capacity, req.speed_limit,
                               req.edge_type, req.source_handle, req.target_handle):
        raise HTTPException(status_code=404, detail=f"Edge {edge_index} not found")
    return editor.map_data


@router.delete("/edges/{edge_index}", response_model=MapData)
async def delete_edge(edge_index: int) -> MapData:
    if not editor.delete_edge(edge_index):
        raise HTTPException(status_code=404, detail=f"Edge {edge_index} not found")
    return editor.map_data


class _RenameReq(BaseModel):
    name: str


@router.patch("/meta", response_model=MapData)
async def update_meta(req: _RenameReq) -> MapData:
    name = req.name.strip()
    if not name:
        raise HTTPException(status_code=422, detail="Name cannot be blank")
    if name != editor.map_data.meta.name:
        slug = _slugify(name)
        if slug in map_names() or (settings.maps_dir / f"{slug}.json").exists():
            raise HTTPException(status_code=409, detail=f"A map named '{name}' already exists")
    editor.rename(name)
    return editor.map_data


@router.post("/save", response_model=dict[str, str])
async def save_map() -> dict[str, str]:
    slug = _slugify(editor.map_data.meta.name)
    settings.maps_dir.mkdir(parents=True, exist_ok=True)
    path = settings.maps_dir / f"{slug}.json"
    path.write_text(editor.map_data.model_dump_json(indent=2), encoding="utf-8")
    return {"filename": path.name}


@router.get("/export")
async def export_map() -> Response:
    return Response(
        content=editor.map_data.model_dump_json(indent=2).encode(),
        media_type="application/json",
        headers={"Content-Disposition": 'attachment; filename="map.json"'},
    )


@router.post("/load", response_model=MapData)
async def load_map(file: UploadFile = File(...)) -> MapData:  # noqa: B008
    try:
        data = MapData.model_validate_json(await file.read())
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Invalid map file: {exc}") from exc
    editor.load(data)
    return editor.map_data


@router.post("/open/{name}", response_model=MapData)
async def open_map(name: str) -> MapData:
    path = find_map_file(name)
    editor.load(load_map_file(path))
    return editor.map_data


@router.post("/reset", response_model=MapData)
async def reset_state() -> MapData:
    editor.reset()
    return editor.map_data
