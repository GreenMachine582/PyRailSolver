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


def _px(coord: int) -> int:
    return _PAD + coord * _SCALE


def render_map(map_data: MapData, graph: RailGraph) -> str:
    w = _PAD * 2 + map_data.meta.width * _SCALE
    h = _PAD * 2 + map_data.meta.height * _SCALE

    parts: list[str] = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg"'
        f' width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
    )

    parts.append('<g class="grid" opacity="0.3">')
    for gx in range(map_data.meta.width + 1):
        for gy in range(map_data.meta.height + 1):
            parts.append(f'<circle cx="{_px(gx)}" cy="{_px(gy)}" r="1.5" fill="#adb5bd"/>')
    parts.append("</g>")

    seen: set[tuple[int, int]] = set()
    parts.append('<g class="edges">')
    for edge in graph.edges:
        key = (min(edge.from_id, edge.to_id), max(edge.from_id, edge.to_id))
        if key in seen:
            continue
        seen.add(key)
        n1 = graph.node(edge.from_id)
        n2 = graph.node(edge.to_id)
        parts.append(
            f'<line x1="{_px(n1.x)}" y1="{_px(n1.y)}"'
            f' x2="{_px(n2.x)}" y2="{_px(n2.y)}"'
            f' stroke="#6c757d" stroke-width="3" stroke-linecap="round"/>'
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
            f' fill="{color}" stroke="white" stroke-width="2"/>'
        )
        parts.append(
            f'<text x="{cx}" y="{cy - _R - 4}" text-anchor="middle"'
            f' font-size="11" font-family="sans-serif" fill="#212529">{label}</text>'
        )
    parts.append("</g>")

    parts.append("</svg>")
    return "\n".join(parts)
