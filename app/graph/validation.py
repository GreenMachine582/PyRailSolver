from app.core.validation import ValidationResult
from app.graph.rail_graph import RailGraph
from app.parser.models import MapData, NodeType


def validate_map_data(map_data: MapData) -> ValidationResult:
    """Validate structural and semantic constraints on raw map data."""
    result = ValidationResult()

    # Grid dimensions must be positive
    if map_data.meta.width <= 0:
        result.add_error("INVALID_WIDTH", f"Map width must be positive, got {map_data.meta.width}")
    if map_data.meta.height <= 0:
        result.add_error("INVALID_HEIGHT", f"Map height must be positive, got {map_data.meta.height}")

    # Node IDs must be unique
    seen_node_ids: set[int] = set()
    for node in map_data.nodes:
        if node.id in seen_node_ids:
            result.add_error("DUPLICATE_NODE_ID", f"Duplicate node ID: {node.id}")
        seen_node_ids.add(node.id)

    # Node coordinates must be within grid bounds
    for node in map_data.nodes:
        if not (0 <= node.x < map_data.meta.width):
            result.add_error(
                "NODE_OUT_OF_BOUNDS",
                f"Node {node.id} x={node.x} is outside grid width {map_data.meta.width}",
            )
        if not (0 <= node.y < map_data.meta.height):
            result.add_error(
                "NODE_OUT_OF_BOUNDS",
                f"Node {node.id} y={node.y} is outside grid height {map_data.meta.height}",
            )

    # Edges must not be self-loops, and must have valid cost/distance
    for i, edge in enumerate(map_data.edges, start=1):
        if edge.from_id == edge.to_id:
            result.add_error(
                "SELF_LOOP_EDGE",
                f"Edge {i}: from_id and to_id are both {edge.from_id}",
            )
        if edge.cost < 0:
            result.add_error(
                "NEGATIVE_EDGE_COST",
                f"Edge {i} ({edge.from_id}→{edge.to_id}) has negative cost {edge.cost}",
            )
        if edge.distance <= 0:
            result.add_error(
                "NON_POSITIVE_DISTANCE",
                f"Edge {i} ({edge.from_id}→{edge.to_id}) has non-positive distance {edge.distance}",
            )

    # Train IDs must be unique
    seen_train_ids: set[int] = set()
    for train in map_data.trains:
        if train.id in seen_train_ids:
            result.add_error("DUPLICATE_TRAIN_ID", f"Duplicate train ID: {train.id}")
        seen_train_ids.add(train.id)

    # Warn when two nodes occupy the same grid cell
    seen_positions: set[tuple[int, int]] = set()
    for node in map_data.nodes:
        pos = (node.x, node.y)
        if pos in seen_positions:
            result.add_warning(
                "DUPLICATE_NODE_POSITION",
                f"Multiple nodes share position ({node.x}, {node.y})",
            )
        seen_positions.add(pos)

    return result


def validate_rail_graph(graph: RailGraph, map_data: MapData) -> ValidationResult:
    """Validate semantic constraints that require the built graph."""
    result = ValidationResult()

    station_ids = {n.id for n in graph.nodes_of_type(NodeType.station)}

    for train in map_data.trains:
        if train.origin_id not in station_ids:
            result.add_error(
                "TRAIN_ORIGIN_NOT_STATION",
                f"Train {train.id}: origin node {train.origin_id} is not a station",
            )
        if train.destination_id not in station_ids:
            result.add_error(
                "TRAIN_DESTINATION_NOT_STATION",
                f"Train {train.id}: destination node {train.destination_id} is not a station",
            )
        if not graph.has_path(train.origin_id, train.destination_id):
            result.add_error(
                "NO_PATH",
                f"Train {train.id}: no path from node {train.origin_id} to node {train.destination_id}",
            )

    # Warn about isolated nodes (no connections at all)
    for node in graph.nodes:
        if graph.graph.degree(node.id) == 0:
            result.add_warning(
                "ISOLATED_NODE",
                f"Node {node.id} ({node.name!r}) has no track connections",
            )

    return result
