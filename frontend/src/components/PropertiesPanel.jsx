import { useState } from 'react'
import { NODE_COLORS, NODE_LABELS, EDGE_STYLES, DEFAULT_EDGE_TYPE } from '../constants'

// ─── Inline confirm dialog ────────────────────────────────

function ConfirmDialog({ message, onConfirm, onCancel }) {
  return (
    <div className="dialog-overlay">
      <div className="dialog-box" style={{ minWidth: 260, maxWidth: 340 }}>
        <div className="dialog-header">
          <h6 className="mb-0">Confirm</h6>
          <button className="btn-close btn-sm" onClick={onCancel} aria-label="Close" />
        </div>
        <div className="dialog-body">
          <p className="small mb-3">{message}</p>
          <div className="d-flex gap-2">
            <button className="btn btn-danger btn-sm" onClick={onConfirm}>Delete</button>
            <button className="btn btn-outline-secondary btn-sm" onClick={onCancel}>Cancel</button>
          </div>
        </div>
      </div>
    </div>
  )
}

// ─── Panel router ─────────────────────────────────────────

export function PropertiesPanel({ selected, nodes, edges, onSaveNode, onDeleteNode, onSaveEdge, onDeleteEdge }) {
  if (selected?.type === 'node') {
    return (
      <NodePanel
        key={selected.data.nodeId}
        data={selected.data}
        onSave={onSaveNode}
        onDelete={onDeleteNode}
      />
    )
  }
  if (selected?.type === 'edge') {
    return (
      <EdgePanel
        key={selected.data.index}
        data={selected.data}
        nodes={nodes}
        onSave={onSaveEdge}
        onDelete={onDeleteEdge}
      />
    )
  }
  return (
    <aside className="props-panel">
      <div className="props-header">Properties</div>
      <div className="props-body">
        <p className="text-muted small">Select a node or edge to edit it.</p>
        <hr />
        <p className="small mb-1 text-muted">
          <strong>{nodes.length}</strong> nodes &nbsp;·&nbsp; <strong>{edges.length}</strong> edges
        </p>
      </div>
    </aside>
  )
}

// ─── Node panel ───────────────────────────────────────────

function NodePanel({ data, onSave, onDelete }) {
  const [name,       setName]      = useState(data.name ?? '')
  const [nodeType,   setNodeType]  = useState(data.nodeType ?? 'station')
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

// ─── Edge panel ───────────────────────────────────────────

function EdgePanel({ data, nodes, onSave, onDelete }) {
  const [direction,  setDirection] = useState(data.direction  ?? 'bidirectional')
  const [cost,       setCost]      = useState(data.cost       ?? 0)
  const [distance,   setDistance]  = useState(data.distance   ?? 1.0)
  const [capacity,   setCapacity]  = useState(data.capacity   ?? 1)
  const [speed,      setSpeed]     = useState(data.speed_limit ?? 100)
  const [edgeType,   setEdgeType]  = useState(data.edge_type  ?? DEFAULT_EDGE_TYPE)
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
            onClick={() => onSave(data.index, { direction, cost, distance, capacity, speed_limit: speed, edge_type: edgeType })}
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
