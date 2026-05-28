import { useRef } from 'react'
import { NODE_COLORS, NODE_LABELS, TOOLS } from '../constants'

const HINTS = {
  pan:      'Drag to pan · scroll to zoom · click node/edge to select · Delete to remove',
  station:  'Click canvas to place a Station',
  platform: 'Click canvas to place a Platform',
  junction: 'Click canvas to place a Junction',
  depot:    'Click canvas to place a Depot',
  waypoint: 'Click canvas to place a Waypoint',
  endpoint: 'Click canvas to place an Endpoint',
}

export function Toolbar({ activeTool, onToolChange, meta, onLoadFile, onDownload, onSave, saving, onThemeToggle, theme }) {
  const fileRef = useRef(null)

  return (
    <div className="editor-toolbar">
      <a href="/" className="toolbar-brand">&#8592; Maps</a>
      <span className="toolbar-map-name">{meta.name}</span>
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

      <button
        className="toolbar-btn"
        title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
        onClick={onThemeToggle}
        style={{ marginLeft: 'auto' }}
      >
        {theme === 'dark' ? '☀' : '☾'}
      </button>

      <span className="toolbar-hint">{HINTS[activeTool] ?? ''}</span>
    </div>
  )
}
