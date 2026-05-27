from app.parser.models import EdgeRow, MapData, MapMeta, NodeRow, NodeType


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


editor = EditorState()
