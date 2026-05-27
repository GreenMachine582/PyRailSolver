import networkx as nx

from app.graph.models import EdgeData, NodeData
from app.parser.models import Direction, MapData, NodeType


class RailGraph:
    def __init__(self, graph: nx.DiGraph[int]) -> None:
        self._graph = graph

    @property
    def graph(self) -> nx.DiGraph[int]:
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
            raise KeyError(f"Node {node_id} not found in graph") from None

    def edge(self, from_id: int, to_id: int) -> EdgeData:
        try:
            return self._graph.edges[from_id, to_id]["data"]  # type: ignore[no-any-return]
        except KeyError:
            raise KeyError(f"Edge ({from_id}, {to_id}) not found in graph") from None

    def nodes_of_type(self, node_type: NodeType) -> list[NodeData]:
        return [n for n in self.nodes if n.type == node_type]

    def has_path(self, from_id: int, to_id: int) -> bool:
        return nx.has_path(self._graph, from_id, to_id)

    def has_reverse_edge(self, from_id: int, to_id: int) -> bool:
        return bool(self._graph.has_edge(to_id, from_id))


def build_graph(map_data: MapData) -> RailGraph:
    """Build a directed RailGraph from a parsed MapData object."""
    g: nx.DiGraph[int] = nx.DiGraph()

    for node_row in map_data.nodes:
        g.add_node(
            node_row.id,
            data=NodeData(
                id=node_row.id,
                type=node_row.type,
                x=node_row.x,
                y=node_row.y,
                name=node_row.name,
                capacity=node_row.capacity,
            ),
        )

    for edge_row in map_data.edges:
        fwd = EdgeData(
            from_id=edge_row.from_id,
            to_id=edge_row.to_id,
            cost=edge_row.cost,
            distance=edge_row.distance,
            capacity=edge_row.capacity,
            speed_limit=edge_row.speed_limit,
        )
        rev = EdgeData(
            from_id=edge_row.to_id,
            to_id=edge_row.from_id,
            cost=edge_row.cost,
            distance=edge_row.distance,
            capacity=edge_row.capacity,
            speed_limit=edge_row.speed_limit,
        )

        match edge_row.direction:
            case Direction.forward:
                g.add_edge(edge_row.from_id, edge_row.to_id, data=fwd)
            case Direction.reverse:
                g.add_edge(edge_row.to_id, edge_row.from_id, data=rev)
            case Direction.bidirectional:
                g.add_edge(edge_row.from_id, edge_row.to_id, data=fwd)
                g.add_edge(edge_row.to_id, edge_row.from_id, data=rev)

    return RailGraph(g)
