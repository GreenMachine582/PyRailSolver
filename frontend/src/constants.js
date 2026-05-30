export const GRID_SIZE = 80

export const DEFAULT_EDGE_TYPE = 'smoothstep'

export const EDGE_STYLES = [
  { value: 'smoothstep', label: 'Smooth'   },
  { value: 'default',    label: 'Curved'   },
  { value: 'step',       label: 'Square'   },
  { value: 'straight',   label: 'Straight' },
]

export const NODE_COLORS = {
  station:  '#0d6efd',
  platform: '#6ea8fe',
  junction: '#6c757d',
  depot:    '#fd7e14',
  waypoint: '#198754',
  endpoint: '#dc3545',
}

export const NODE_LABELS = {
  station:  'Station',
  platform: 'Platform',
  junction: 'Junction',
  depot:    'Depot',
  waypoint: 'Waypoint',
  endpoint: 'Endpoint',
}

export const TOOLS = [
  { key: 'pan',      label: '⇖ Pan' },
  { key: 'station',  label: 'Station'  },
  { key: 'platform', label: 'Platform' },
  { key: 'junction', label: 'Junction' },
  { key: 'depot',    label: 'Depot'    },
  { key: 'waypoint', label: 'Waypoint' },
  { key: 'endpoint', label: 'Endpoint' },
]

// #40916c = --rs-500 (brand green) from editor.css
export const NODE_HANDLE_STYLE = {
  width:      8,
  height:     8,
  background: '#40916c',
  border:     '1px solid white',
}

export const NODE_SHADOW_SELECTED = '0 0 0 3px #ffc107, 0 0 8px rgba(255,193,7,0.6)'
export const NODE_SHADOW_DEFAULT  = '0 0 0 2px white'

export const TOOL_HINTS = {
  pan:      'Drag to pan · scroll to zoom · click node/edge to select · Delete to remove',
  station:  'Click canvas to place a Station',
  platform: 'Click canvas to place a Platform',
  junction: 'Click canvas to place a Junction',
  depot:    'Click canvas to place a Depot',
  waypoint: 'Click canvas to place a Waypoint',
  endpoint: 'Click canvas to place an Endpoint',
}
