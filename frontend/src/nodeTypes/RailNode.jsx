import { Handle, Position } from '@xyflow/react'
import { NODE_COLORS, NODE_LABELS, NODE_HANDLE_STYLE, NODE_SHADOW_SELECTED, NODE_SHADOW_DEFAULT } from '../constants'

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
  const color    = NODE_COLORS[data.nodeType] || '#6c757d'
  const isCircle = CIRCLE_TYPES.has(data.nodeType)
  const shadow   = selected ? NODE_SHADOW_SELECTED : NODE_SHADOW_DEFAULT

  return (
    <div className="rail-node-wrapper">
      {HANDLES.map(({ position, id }) => (
        <Handle
          key={id} type="source" position={position} id={id}
          style={data.viewer ? { ...NODE_HANDLE_STYLE, visibility: 'hidden', pointerEvents: 'none' } : NODE_HANDLE_STYLE}
        />
      ))}

      {isCircle ? (
        <>
          <div className="rail-node-circle" style={{ background: color, boxShadow: shadow }} />
          <div className="rail-node-label" style={{ position: 'absolute', top: '100%', left: '50%', transform: 'translateX(-50%)', paddingTop: 3 }}>
            {data.label || NODE_LABELS[data.nodeType] || data.nodeType}
          </div>
        </>
      ) : (
        <div className="rail-node-rect" style={{ background: color, boxShadow: shadow }}>
          {data.label || NODE_LABELS[data.nodeType] || data.nodeType}
        </div>
      )}
    </div>
  )
}

export const NODE_TYPES = { railNode: RailNode }
