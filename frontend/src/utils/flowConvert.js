import { MarkerType } from '@xyflow/react'
import { GRID_SIZE, DEFAULT_EDGE_TYPE } from '../constants'

export function toRFNode(node) {
  return {
    id: String(node.id),
    type: 'railNode',
    position: { x: node.x * GRID_SIZE, y: node.y * GRID_SIZE },
    data: {
      nodeId:   node.id,
      nodeType: node.type,
      label:    node.name,
      name:     node.name,
      x: node.x,
      y: node.y,
      capacity: node.capacity,
    },
  }
}

export function toRFEdge(edge, index) {
  const directed = edge.direction !== 'bidirectional'
  return {
    id: `e-${index}`,
    source: String(edge.from_id),
    target: String(edge.to_id),
    sourceHandle: edge.source_handle || undefined,
    targetHandle: edge.target_handle || undefined,
    type: edge.edge_type || DEFAULT_EDGE_TYPE,
    animated: false,
    label: edge.cost > 0 ? String(edge.cost) : undefined,
    labelStyle: { fontSize: 10 },
    markerEnd: directed ? { type: MarkerType.ArrowClosed, width: 14, height: 14 } : undefined,
    style: { strokeWidth: 2 },
    data: {
      index,
      from_id:       edge.from_id,
      to_id:         edge.to_id,
      direction:     edge.direction,
      cost:          edge.cost,
      distance:      edge.distance,
      capacity:      edge.capacity,
      speed_limit:   edge.speed_limit,
      edge_type:     edge.edge_type     || DEFAULT_EDGE_TYPE,
      source_handle: edge.source_handle || '',
      target_handle: edge.target_handle || '',
    },
  }
}
