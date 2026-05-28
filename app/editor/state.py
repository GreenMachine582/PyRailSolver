from app.parser.models import Direction, EdgeRow, MapData, MapMeta, NodeRow, NodeType


class EditorState:
    def __init__(self) -> None:
        self._meta = MapMeta(name="Untitled Map", width=20, height=15)
        self._nodes: list[NodeRow] = []
        self._edges: list[EdgeRow] = []
        self._next_id: int = 1

    @property
    def map_data(self) -> MapData:
        return MapData(
            meta=self._meta,
            nodes=list(self._nodes),
            edges=list(self._edges),
            trains=[],
        )

    def reset(self, name: str = "Untitled Map", width: int = 20, height: int = 15) -> None:
        self._meta = MapMeta(name=name, width=width, height=height)
        self._nodes = []
        self._edges = []
        self._next_id = 1

    def add_node(self, node_type: NodeType, x: int, y: int, name: str = "") -> NodeRow:
        node = NodeRow(id=self._next_id, type=node_type, x=x, y=y, name=name)
        self._nodes.append(node)
        self._next_id += 1
        return node

    def node_at(self, x: int, y: int) -> NodeRow | None:
        return next((n for n in self._nodes if n.x == x and n.y == y), None)

    def add_edge(
        self,
        from_id: int,
        to_id: int,
        direction: Direction = Direction.bidirectional,
        cost: int = 0,
        distance: float = 1.0,
        capacity: int = 1,
        speed_limit: int = 100,
    ) -> EdgeRow:
        edge = EdgeRow(
            from_id=from_id,
            to_id=to_id,
            direction=direction,
            cost=cost,
            distance=distance,
            capacity=capacity,
            speed_limit=speed_limit,
        )
        self._edges.append(edge)
        return edge

    def delete_node(self, node_id: int) -> bool:
        node = next((n for n in self._nodes if n.id == node_id), None)
        if node is None:
            return False
        self._nodes.remove(node)
        self._edges = [e for e in self._edges if e.from_id != node_id and e.to_id != node_id]
        return True

    def delete_edge(self, edge_index: int) -> bool:
        if edge_index < 0 or edge_index >= len(self._edges):
            return False
        del self._edges[edge_index]
        return True

    def load(self, data: MapData) -> None:
        self._meta = data.meta
        self._nodes = list(data.nodes)
        self._edges = list(data.edges)
        self._next_id = max((n.id for n in self._nodes), default=0) + 1


editor = EditorState()
