import { useRef, useState } from 'react'
import { NODE_COLORS, NODE_LABELS, TOOLS, EDGE_STYLES } from '../constants'

const HINTS = {
  pan:      'Drag to pan · scroll to zoom · click node/edge to select · Delete to remove',
  station:  'Click canvas to place a Station',
  platform: 'Click canvas to place a Platform',
  junction: 'Click canvas to place a Junction',
  depot:    'Click canvas to place a Depot',
  waypoint: 'Click canvas to place a Waypoint',
  endpoint: 'Click canvas to place an Endpoint',
}

export function Toolbar({ activeTool, onToolChange, meta, onLoadFile, onDownload, onSave, saving, onRename, onRenameError = () => {}, edgeType, onEdgeTypeChange }) {
  const fileRef = useRef(null)
  const nameRef = useRef(null)
  const [editing, setEditing] = useState(false)
  const [draft,   setDraft]   = useState('')

  function startEdit() {
    setDraft(meta.name)
    setEditing(true)
    setTimeout(() => nameRef.current?.select(), 0)
  }

  function commitEdit() {
    const trimmed = draft.trim()
    setEditing(false)
    if (!trimmed) {
      onRenameError('Map name cannot be blank')
      return
    }
    if (trimmed !== meta.name) onRename(trimmed)
  }

  function onKeyDown(e) {
    if (e.key === 'Enter') { e.preventDefault(); commitEdit() }
    if (e.key === 'Escape') setEditing(false)
  }

  return (
    <>
      <div className="editor-toolbar">
          {editing ? (
          <input
            ref={nameRef}
            className="toolbar-map-name-input"
            value={draft}
            onChange={e => setDraft(e.target.value)}
            onBlur={commitEdit}
            onKeyDown={onKeyDown}
          />
        ) : (
          <span
            className="toolbar-map-name toolbar-map-name--editable"
            onClick={startEdit}
            title="Click to rename"
          >
            {meta.name}
          </span>
        )}
        <div className="toolbar-sep" />

        {TOOLS.map(({ key, label }) => (
          <button
            key={key}
            className={`toolbar-btn${activeTool === key ? ' active' : ''}`}
            onClick={() => onToolChange(key)}
            title={key === 'pan' ? 'Pan / zoom' : `Place ${NODE_LABELS[key]}`}
          >
            {key !== 'pan' && (
              <span className="node-dot-sm" style={{ background: NODE_COLORS[key] }} />
            )}
            {label}
          </button>
        ))}

        <div className="toolbar-sep" />

        <button
          className="toolbar-btn"
          title="Save map to project"
          onClick={onSave}
          disabled={saving}
        >
          {saving ? 'Saving…' : 'Save'}
        </button>
        <a
          href="/api/editor/export"
          className="toolbar-btn"
          download="map.json"
          title="Download map as JSON"
          onClick={onDownload}
        >
          Download
        </a>
        <button
          className="toolbar-btn"
          title="Load map from JSON"
          onClick={() => fileRef.current?.click()}
        >
          Load
        </button>
        <input
          ref={fileRef}
          type="file"
          accept=".json"
          style={{ display: 'none' }}
          onChange={e => {
            const f = e.target.files?.[0]
            if (f) onLoadFile(f)
            e.target.value = ''
          }}
        />

        <div className="toolbar-sep" />

        <select
          className="toolbar-select"
          value={edgeType}
          onChange={e => onEdgeTypeChange(e.target.value)}
          title="Track style"
        >
          {EDGE_STYLES.map(({ value, label }) => (
            <option key={value} value={value}>{label}</option>
          ))}
        </select>

      </div>

      <div className="toolbar-hint-bar">
        {HINTS[activeTool] ?? ''}
      </div>
    </>
  )
}
