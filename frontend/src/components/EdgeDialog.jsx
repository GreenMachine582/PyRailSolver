import { useState } from 'react'
import { EDGE_STYLES, DEFAULT_EDGE_TYPE } from '../constants'
import { buildEdgePayload } from '../utils/flowConvert'

export function EdgeDialog({ connection, nodes, defaultEdgeType = DEFAULT_EDGE_TYPE, onConfirm, onCancel }) {
  const [direction, setDirection] = useState('bidirectional')
  const [cost,      setCost]      = useState(0)
  const [distance,  setDistance]  = useState(1.0)
  const [capacity,  setCapacity]  = useState(1)
  const [speed,     setSpeed]     = useState(100)
  const [edgeType,  setEdgeType]  = useState(defaultEdgeType)

  const fromNode = nodes.find(n => n.id === connection.source)
  const toNode   = nodes.find(n => n.id === connection.target)
  const fromName = fromNode?.data?.label || `Node ${connection.source}`
  const toName   = toNode?.data?.label   || `Node ${connection.target}`

  return (
    <div className="dialog-overlay">
      <div className="dialog-box">
        <div className="dialog-header">
          <h6 className="mb-0">Draw Track Segment</h6>
          <button className="btn-close btn-sm" onClick={onCancel} aria-label="Close" />
        </div>
        <div className="dialog-body">
          <p className="small mb-3">
            <strong>{fromName}</strong>
            <span className="text-muted mx-1">&harr;</span>
            <strong>{toName}</strong>
          </p>

          <div className="mb-3">
            <p className="form-label small fw-semibold mb-1">Direction</p>
            <div className="d-flex gap-3">
              {[['bidirectional','↔ Bidirectional'],['forward','→ One-way']].map(([val, lbl]) => (
                <div className="form-check mb-0" key={val}>
                  <input
                    className="form-check-input" type="radio" name="dir"
                    id={`dir-${val}`} value={val}
                    checked={direction === val}
                    onChange={() => setDirection(val)}
                  />
                  <label className="form-check-label small" htmlFor={`dir-${val}`}>{lbl}</label>
                </div>
              ))}
            </div>
          </div>

          <div className="row g-2 mb-3">
            {[
              ['Cost',       cost,     setCost,     'number', 0,   1],
              ['Distance',   distance, setDistance, 'number', 0.1, 0.1],
              ['Capacity',   capacity, setCapacity, 'number', 1,   1],
              ['Speed limit',speed,    setSpeed,    'number', 1,   1],
            ].map(([label, val, setter, type, min, step]) => (
              <div className="col-6" key={label}>
                <label className="form-label small">{label}</label>
                <input
                  type={type} className="form-control form-control-sm"
                  value={val} min={min} step={step}
                  onChange={e => setter(Number(e.target.value))}
                />
              </div>
            ))}
          </div>

          <div className="mb-3">
            <label className="form-label small fw-semibold mb-1">Track style</label>
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

          <div className="d-flex gap-2">
            <button
              className="btn btn-primary btn-sm"
              onClick={() => onConfirm(buildEdgePayload({ direction, cost, distance, capacity, speed, edgeType }))}
            >Draw</button>
            <button className="btn btn-outline-secondary btn-sm" onClick={onCancel}>Cancel</button>
          </div>
        </div>
      </div>
    </div>
  )
}
