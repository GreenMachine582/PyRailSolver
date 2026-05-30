import { useState } from 'react'
import { NODE_COLORS, NODE_LABELS } from '../constants'
import { ConfirmDialog } from './ConfirmDialog'

export function NodePanel({ data, onSave, onDelete }) {
  const [name,       setName]       = useState(data.name ?? '')
  const [nodeType,   setNodeType]   = useState(data.nodeType ?? 'station')
  const [confirming, setConfirming] = useState(false)

  return (
    <aside className="props-panel">
      <div className="props-header">Node</div>
      <div className="props-body">
        <div className="props-field">
          <label>Position</label>
          <span className="props-val">({data.x}, {data.y})</span>
        </div>
        <div className="props-field">
          <label>Type</label>
          <select
            className="form-select form-select-sm"
            value={nodeType}
            onChange={e => setNodeType(e.target.value)}
          >
            {Object.entries(NODE_LABELS).map(([k, v]) => (
              <option key={k} value={k}>{v}</option>
            ))}
          </select>
        </div>
        <div className="props-field">
          <label>Name</label>
          <input
            type="text"
            className="form-control form-control-sm"
            value={name}
            placeholder="Node name"
            onChange={e => setName(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && onSave(data.nodeId, name.trim(), nodeType)}
          />
        </div>
        <div className="props-dot-preview">
          <span className="node-dot-sm" style={{ background: NODE_COLORS[nodeType] }} />
          <span className="small text-muted">{NODE_LABELS[nodeType]}</span>
        </div>
        <div className="props-actions">
          <button
            className="btn btn-primary btn-sm"
            onClick={() => onSave(data.nodeId, name.trim(), nodeType)}
          >Save</button>
          <button
            className="btn btn-outline-danger btn-sm"
            onClick={() => setConfirming(true)}
          >Delete</button>
        </div>
      </div>

      {confirming && (
        <ConfirmDialog
          message={`Delete "${data.label || data.nodeType}" and its connected tracks?`}
          onConfirm={() => { setConfirming(false); onDelete(data.nodeId) }}
          onCancel={() => setConfirming(false)}
        />
      )}
    </aside>
  )
}
