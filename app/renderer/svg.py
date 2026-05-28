import html

from app.graph.rail_graph import RailGraph
from app.parser.models import MapData, NodeType

_SCALE: int = 40
_PAD: int = 30
_R: int = 10

_NODE_COLORS: dict[NodeType, str] = {
    NodeType.station: "#0d6efd",
    NodeType.platform: "#6ea8fe",
    NodeType.junction: "#6c757d",
    NodeType.depot: "#fd7e14",
    NodeType.waypoint: "#198754",
    NodeType.endpoint: "#dc3545",
}

_ARROW_DEFS = (
    "<defs>"
    '<marker id="arrow" markerWidth="10" markerHeight="10"'
    ' refX="5" refY="5" orient="auto" markerUnits="userSpaceOnUse">'
    '<path d="M0,0 L10,5 L0,10 z" fill="#495057"/>'
    "</marker>"
    "</defs>"
)


def _px(coord: int) -> int:
    return _PAD + coord * _SCALE


def render_map(map_data: MapData, graph: RailGraph) -> str:
    w = _PAD * 2 + map_data.meta.width * _SCALE
    h = _PAD * 2 + map_data.meta.height * _SCALE

    parts: list[str] = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" id="map-svg"'
        f' width="{w}" height="{h}" viewBox="0 0 {w} {h}"'
        f' data-scale="{_SCALE}" data-pad="{_PAD}"'
        f' data-grid-w="{map_data.meta.width}" data-grid-h="{map_data.meta.height}">'
    )

    parts.append('<g class="grid" opacity="0.3">')
    for gx in range(map_data.meta.width + 1):
        for gy in range(map_data.meta.height + 1):
            parts.append(f'<circle cx="{_px(gx)}" cy="{_px(gy)}" r="1.5" fill="#adb5bd"/>')
    parts.append("</g>")

    has_directed = any(
        not graph.has_reverse_edge(e.from_id, e.to_id) for e in graph.edges
    )
    if has_directed:
        parts.append(_ARROW_DEFS)

    seen: set[tuple[int, int]] = set()
    parts.append('<g class="edges">')
    for edge in graph.edges:
        key = (min(edge.from_id, edge.to_id), max(edge.from_id, edge.to_id))
        if key in seen:
            continue
        seen.add(key)
        n1 = graph.node(edge.from_id)
        n2 = graph.node(edge.to_id)
        x1, y1 = _px(n1.x), _px(n1.y)
        x2, y2 = _px(n2.x), _px(n2.y)
        edge_title = html.escape(
            f"Cost: {edge.cost} | Dist: {edge.distance:.1f} | Speed: {edge.speed_limit}"
        )
        if graph.has_reverse_edge(edge.from_id, edge.to_id):
            parts.append(
                f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"'
                f' stroke="#6c757d" stroke-width="3" stroke-linecap="round">'
                f'<title>{edge_title}</title></line>'
            )
        else:
            mx, my = (x1 + x2) // 2, (y1 + y2) // 2
            pts = f"{x1},{y1} {mx},{my} {x2},{y2}"
            parts.append(
                f'<polyline points="{pts}" stroke="#6c757d" stroke-width="3"'
                f' fill="none" stroke-linecap="round" marker-mid="url(#arrow)">'
                f'<title>{edge_title}</title></polyline>'
            )
    parts.append("</g>")

    parts.append('<g class="nodes">')
    for node in graph.nodes:
        cx = _px(node.x)
        cy = _px(node.y)
        color = _NODE_COLORS[node.type]
        label = html.escape(node.name or node.type.value)
        parts.append(
            f'<circle cx="{cx}" cy="{cy}" r="{_R}"'
            f' fill="{color}" stroke="white" stroke-width="2"'
            f' data-node-id="{node.id}"'
            f' data-node-name="{html.escape(node.name)}"'
            f' data-node-type="{node.type.value}"'
            f' data-node-x="{node.x}" data-node-y="{node.y}"'
            f' tabindex="0" data-bs-toggle="popover"'
            f' data-bs-placement="top" data-bs-title="{label}"/>'
        )
        parts.append(
            f'<text x="{cx}" y="{cy - _R - 4}" text-anchor="middle"'
            f' font-size="11" font-family="sans-serif" fill="#212529">{label}</text>'
        )
    parts.append("</g>")

    parts.append("</svg>")
    return "\n".join(parts)
