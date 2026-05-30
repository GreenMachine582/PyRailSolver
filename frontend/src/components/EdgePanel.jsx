import { useState } from 'react'
import { EDGE_STYLES, DEFAULT_EDGE_TYPE } from '../constants'
import { buildEdgePayload } from '../utils/flowConvert'
import { ConfirmDialog } from './ConfirmDialog'

export function EdgePanel({ data, nodes, onSave, onDelete }) {
  const [direction,  setDirection]  = useState(data.direction   ?? 'bidirectional')
  const [cost,       setCost]       = useState(data.cost        ?? 0)
  const [distance,   setDistance]   = useState(data.distance    ?? 1.0)
  const [capacity,   setCapacity]   = useState(data.capacity    ?? 1)
  const [speed,      setSpeed]      = useState(data.speed_limit ?? 100)
  const [edgeType,   setEdgeType]   = useState(data.edge_type   ?? DEFAULT_EDGE_TYPE)
  const [confirming, setConfirming] = useState(false)

  const fromNode = nodes.find(n => n.id === String(data.from_id))
  const toNode   = nodes.find(n => n.id === String(data.to_id))
  const fromName = fromNode?.data?.label ?? `Node ${data.from_id}`
  const toName   = toNode?.data?.label   ?? `Node ${data.to_id}`

  return (
    <aside className="props-panel">
      <div className="props-header">Track</div>
      <div className="props-body">
        <div className="props-field">
          <label>Nodes</label>
          <span className="props-val small">{fromName} &harr; {toName}</span>
        </div>
        <div className="props-field">
          <label>Direction</label>
          <select
            className="form-select form-select-sm"
            value={direction}
            onChange={e => setDirection(e.target.value)}
          >
            <option value="bidirectional">↔ Bidirectional</option>
            <option value="forward">→ One-way</option>
          </select>
        </div>
        <div className="row g-2 mb-2">
          {[
            ['Cost',     cost,     setCost,     0,   1  ],
            ['Distance', distance, setDistance, 0.1, 0.1],
            ['Capacity', capacity, setCapacity, 1,   1  ],
            ['Speed',    speed,    setSpeed,    1,   1  ],
          ].map(([lbl, val, setter, min, step]) => (
            <div className="col-6" key={lbl}>
              <label className="form-label small mb-0">{lbl}</label>
              <input
                type="number" className="form-control form-control-sm"
                value={val} min={min} step={step}
                onChange={e => setter(Number(e.target.value))}
              />
            </div>
          ))}
        </div>
        <div className="props-field">
          <label>Style</label>
          <select
            className="form-select form-select-sm"
            value={edgeType}
            onChange={e => setEdgeType(e.target.value)}
          >
            {EDGE_STYLES.map(({ value, label }) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </select>
        </div>
        <div className="props-actions">
          <button
            className="btn btn-primary btn-sm"
            onClick={() => onSave(data.index, buildEdgePayload({
              direction, cost, distance, capacity, speed, edgeType,
              sourceHandle: data.source_handle || '',
              targetHandle: data.target_handle || '',
            }))}
          >Save</button>
          <button
            className="btn btn-outline-danger btn-sm"
            onClick={() => setConfirming(true)}
          >Delete</button>
        </div>
      </div>

      {confirming && (
        <ConfirmDialog
          message={`Delete track ${fromName} ↔ ${toName}?`}
          onConfirm={() => { setConfirming(false); onDelete(data.index) }}
          onCancel={() => setConfirming(false)}
        />
      )}
    </aside>
  )
}
