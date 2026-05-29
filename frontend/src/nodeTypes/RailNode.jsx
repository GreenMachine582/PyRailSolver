import { Handle, Position } from '@xyflow/react'
import { NODE_COLORS, NODE_LABELS } from '../constants'

const HANDLE_STYLE = {
  width: 8,
  height: 8,
  background: '#40916c',
  border: '1px solid white',
}

const HANDLES = [
  { position: Position.Top,    id: 't' },
  { position: Position.Right,  id: 'r' },
  { position: Position.Bottom, id: 'b' },
  { position: Position.Left,   id: 'l' },
]

// Junction and waypoint are topology/flow nodes — rendered as circles,
// label below. Everything else is a named place — rendered as a rectangle
// with the label inside.
const CIRCLE_TYPES = new Set(['junction', 'waypoint'])

export function RailNode({ data, selected }) {
  const color = NODE_COLORS[data.nodeType] || '#6c757d'
  const isCircle = CIRCLE_TYPES.has(data.nodeType)
  const shadow = selected
    ? '0 0 0 3px #ffc107, 0 0 8px rgba(255,193,7,0.6)'
    : '0 0 0 2px white'

  return (
    <div className="rail-node-wrapper">
      {HANDLES.map(({ position, id }) => (
        <Handle key={id} type="source" position={position} id={id} style={HANDLE_STYLE} />
      ))}

      {isCircle ? (
        <>
          <div className="rail-node-circle" style={{ background: color, boxShadow: shadow }} />
          <div className="rail-node-label">{data.label || NODE_LABELS[data.nodeType] || data.nodeType}</div>
        </>
      ) : (
        <div className="rail-node-rect" style={{ background: color, boxShadow: shadow }}>
          {data.label || NODE_LABELS[data.nodeType] || data.nodeType}
        </div>
      )}
    </div>
  )
}
