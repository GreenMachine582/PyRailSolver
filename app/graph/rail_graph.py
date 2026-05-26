import networkx as nx

from app.graph.models import EdgeData, NodeData
from app.parser.models import Direction, MapData, NodeType


class RailGraph:
    def __init__(self, graph: nx.DiGraph) -> None:
        self._graph = graph

    @property
    def graph(self) -> nx.DiGraph:
        return self._graph

    @property
    def node_count(self) -> int:
        return self._graph.number_of_nodes()

    @property
    def edge_count(self) -> int:
        return self._graph.number_of_edges()

    @property
    def nodes(self) -> list[NodeData]:
        return [attrs["data"] for _, attrs in self._graph.nodes(data=True)]

    @property
    def edges(self) -> list[EdgeData]:
        return [attrs["data"] for _, _, attrs in self._graph.edges(data=True)]

    def node(self, node_id: int) -> NodeData:
        try:
            return self._graph.nodes[node_id]["data"]  # type: ignore[no-any-return]
        except KeyError:
            raise KeyError(f"Node {node_id} not found in graph")

    def edge(self, from_id: int, to_id: int) -> EdgeData:
        try:
            return self._graph.edges[from_id, to_id]["data"]  # type: ignore[no-any-return]
        except KeyError:
            raise KeyError(f"Edge ({from_id}, {to_id}) not found in graph")

    def nodes_of_type(self, node_type: NodeType) -> list[NodeData]:
        return [n for n in self.nodes if n.type == node_type]

    def has_path(self, from_id: int, to_id: int) -> bool:
        return nx.has_path(self._graph, from_id, to_id)  # type: ignore[no-any-return]


def build_graph(map_data: MapData) -> RailGraph:
    """Build a directed RailGraph from a parsed MapData object."""
    g: nx.DiGraph = nx.DiGraph()

    for row in map_data.nodes:
        g.add_node(
            row.id,
            data=NodeData(
                id=row.id,
                type=row.type,
                x=row.x,
                y=row.y,
                name=row.name,
                capacity=row.capacity,
            ),
        )

    for row in map_data.edges:
        fwd = EdgeData(
            from_id=row.from_id,
            to_id=row.to_id,
            cost=row.cost,
            distance=row.distance,
            capacity=row.capacity,
            speed_limit=row.speed_limit,
        )
        rev = EdgeData(
            from_id=row.to_id,
            to_id=row.from_id,
            cost=row.cost,
            distance=row.distance,
            capacity=row.capacity,
            speed_limit=row.speed_limit,
        )

        match row.direction:
            case Direction.forward:
                g.add_edge(row.from_id, row.to_id, data=fwd)
            case Direction.reverse:
                g.add_edge(row.to_id, row.from_id, data=rev)
            case Direction.bidirectional:
                g.add_edge(row.from_id, row.to_id, data=fwd)
                g.add_edge(row.to_id, row.from_id, data=rev)

    return RailGraph(g)
