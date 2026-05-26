from dataclasses import dataclass

from app.parser.models import NodeType


@dataclass(frozen=True)
class NodeData:
    id: int
    type: NodeType
    x: int
    y: int
    name: str = ""
    capacity: int = 1


@dataclass(frozen=True)
class EdgeData:
    from_id: int
    to_id: int
    cost: int = 0
    distance: float = 1.0
    capacity: int = 1
    speed_limit: int = 100
