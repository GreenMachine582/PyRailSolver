import { Handle, Position } from '@xyflow/react'
import { NODE_COLORS } from '../constants'

const HANDLE_STYLE = {
  width: 8,
  height: 8,
  background: '#40916c',
  border: '1px solid white',
}

export function RailNode({ data, selected }) {
  const color = NODE_COLORS[data.nodeType] || '#6c757d'
  return (
    <div className="rail-node-wrapper">
      <Handle type="source" position={Position.Top}    id="t" style={HANDLE_STYLE} />
      <Handle type="source" position={Position.Right}  id="r" style={HANDLE_STYLE} />
      <Handle type="source" position={Position.Bottom} id="b" style={HANDLE_STYLE} />
      <Handle type="source" position={Position.Left}   id="l" style={HANDLE_STYLE} />
      <div
        className="rail-node-circle"
        style={{
          background: color,
          boxShadow: selected
            ? '0 0 0 3px #ffc107, 0 0 8px rgba(255,193,7,0.6)'
            : '0 0 0 2px white',
        }}
      />
      <div className="rail-node-label">
        {data.label || data.nodeType}
      </div>
    </div>
  )
}
