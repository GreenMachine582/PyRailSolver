from enum import StrEnum

from pydantic import BaseModel

from app.core.config import settings


class NodeType(StrEnum):
    station = "station"
    platform = "platform"
    junction = "junction"
    depot = "depot"
    waypoint = "waypoint"
    endpoint = "endpoint"


class Direction(StrEnum):
    bidirectional = "bidirectional"
    forward = "forward"
    reverse = "reverse"


class MapMeta(BaseModel):
    name: str
    width: int
    height: int


class NodeRow(BaseModel):
    id: int
    type: NodeType
    x: int
    y: int
    name: str = ""
    capacity: int = 1


class EdgeRow(BaseModel):
    from_id: int
    to_id: int
    cost: int = 0
    distance: float = 1.0
    capacity: int = 1
    direction: Direction = Direction.bidirectional
    speed_limit: int = 100
    edge_type: str = settings.default_edge_type
    source_handle: str = ""
    target_handle: str = ""


class TrainRow(BaseModel):
    id: int
    origin_id: int
    destination_id: int
    cargo: str = ""
    speed: int = 50
    spawn_tick: int = 0
    priority: int = 1


class MapData(BaseModel):
    meta: MapMeta
    nodes: list[NodeRow]
    edges: list[EdgeRow]
    trains: list[TrainRow]
