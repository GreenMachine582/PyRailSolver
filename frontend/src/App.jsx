import { useState, useCallback, useEffect, useRef } from 'react'
import {
  ReactFlow, Background, Controls, MiniMap,
  useNodesState, useEdgesState,
  ConnectionMode, MarkerType,
  useReactFlow, ReactFlowProvider,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import './editor.css'

import { RailNode }         from './nodeTypes/RailNode'
import { Toolbar }          from './components/Toolbar'
import { PropertiesPanel }  from './components/PropertiesPanel'
import { EdgeDialog }       from './components/EdgeDialog'
import { Notifications }    from './components/Notifications'
import { api }              from './api'
import { GRID_SIZE, NODE_COLORS } from './constants'

const NODE_TYPES = { railNode: RailNode }

function toRFNode(node) {
  return {
    id: String(node.id),
    type: 'railNode',
    position: { x: node.x * GRID_SIZE, y: node.y * GRID_SIZE },
    data: {
      nodeId:   node.id,
      nodeType: node.type,
      label:    node.name || node.type,
      name:     node.name,
      x: node.x,
      y: node.y,
      capacity: node.capacity,
    },
  }
}

function toRFEdge(edge, index) {
  const directed = edge.direction !== 'bidirectional'
  return {
    id: `e-${index}`,
    source: String(edge.from_id),
    target: String(edge.to_id),
    type: 'smoothstep',
    animated: false,
    label: edge.cost > 0 ? String(edge.cost) : undefined,
    labelStyle: { fontSize: 10 },
    markerEnd:  directed ? { type: MarkerType.ArrowClosed, width: 14, height: 14 } : undefined,
    style: { strokeWidth: 2 },
    data: {
      index,
      from_id:    edge.from_id,
      to_id:      edge.to_id,
      direction:  edge.direction,
      cost:       edge.cost,
      distance:   edge.distance,
      capacity:   edge.capacity,
      speed_limit: edge.speed_limit,
    },
  }
}

// ─────────────────────────────────────────────────────────
// Inner component — uses useReactFlow (must live inside provider)
// ─────────────────────────────────────────────────────────

function EditorInner() {
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])
  const [meta,       setMeta]       = useState({ name: 'Loading…', width: 20, height: 15 })
  const [activeTool, setActiveTool] = useState('pan')
  const [selected,   setSelected]   = useState(null)
  const [pendingConn, setPendingConn] = useState(null)
  const [theme, setTheme] = useState(
    () => document.documentElement.getAttribute('data-bs-theme') || 'light'
  )
  const [saving, setSaving] = useState(false)
  const [notifications, setNotifications] = useState([])

  function notify(message, type = 'success') {
    const id = Date.now()
    setNotifications(prev => [...prev, { id, message, type }])
  }

  function dismissNotification(id) {
    setNotifications(prev => prev.filter(n => n.id !== id))
  }

  const { screenToFlowPosition } = useReactFlow()
  const deletingNodes = useRef(false)

  // ── state sync ──────────────────────────────────────────

  function loadState(state) {
    setMeta(state.meta)
    setNodes(state.nodes.map(toRFNode))
    setEdges(state.edges.map((e, i) => toRFEdge(e, i)))
  }

  useEffect(() => {
    api.getState().then(loadState).catch(console.error)
  }, [])

  // ── theme ───────────────────────────────────────────────

  function toggleTheme() {
    const next = theme === 'dark' ? 'light' : 'dark'
    setTheme(next)
    document.documentElement.setAttribute('data-bs-theme', next)
    localStorage.setItem('prs-theme', next)
  }

  // ── canvas interactions ─────────────────────────────────

  const onPaneClick = useCallback(async (e) => {
    if (activeTool === 'pan') return
    const pos = screenToFlowPosition({ x: e.clientX, y: e.clientY })
    const gx = Math.max(0, Math.min(meta.width  - 1, Math.round(pos.x / GRID_SIZE)))
    const gy = Math.max(0, Math.min(meta.height - 1, Math.round(pos.y / GRID_SIZE)))
    try {
      const state = await api.addNode({ x: gx, y: gy, node_type: activeTool, name: '' })
      loadState(state)
      const newNode = state.nodes.at(-1)
      if (newNode) setSelected({ type: 'node', data: toRFNode(newNode).data })
    } catch (err) {
      console.error(err)
    }
  }, [activeTool, meta, screenToFlowPosition])

  const onConnect = useCallback((connection) => {
    setPendingConn(connection)
  }, [])

  const onNodeDragStop = useCallback(async (_, node) => {
    const gx = Math.max(0, Math.min(meta.width  - 1, Math.round(node.position.x / GRID_SIZE)))
    const gy = Math.max(0, Math.min(meta.height - 1, Math.round(node.position.y / GRID_SIZE)))
    try {
      const state = await api.moveNode(parseInt(node.id), gx, gy)
      loadState(state)
    } catch (err) {
      console.error(err)
    }
  }, [meta])

  const onNodesDelete = useCallback(async (deleted) => {
    deletingNodes.current = true
    try {
      for (const n of deleted) await api.deleteNode(parseInt(n.id))
      const state = await api.getState()
      loadState(state)
      setSelected(null)
    } catch (err) {
      console.error(err)
    } finally {
      deletingNodes.current = false
    }
  }, [])

  const onEdgesDelete = useCallback(async (deleted) => {
    if (deletingNodes.current) return
    const indices = [...new Set(deleted.map(e => e.data.index))].sort((a, b) => b - a)
    try {
      for (const idx of indices) await api.deleteEdge(idx)
      const state = await api.getState()
      loadState(state)
      setSelected(null)
    } catch (err) {
      console.error(err)
    }
  }, [])

  const onNodeClick = useCallback((_, node) => {
    setSelected({ type: 'node', data: node.data })
  }, [])

  const onEdgeClick = useCallback((_, edge) => {
    setSelected({ type: 'edge', data: edge.data })
  }, [])

  const onPaneClickClear = useCallback(() => {
    if (activeTool === 'pan') setSelected(null)
  }, [activeTool])

  // ── property panel actions ──────────────────────────────

  const handleSaveNode = useCallback(async (nodeId, name, nodeType) => {
    try {
      const state = await api.updateNode(nodeId, { name, node_type: nodeType })
      loadState(state)
      const updated = state.nodes.find(n => n.id === nodeId)
      if (updated) setSelected({ type: 'node', data: toRFNode(updated).data })
    } catch (err) { console.error(err) }
  }, [])

  const handleDeleteNode = useCallback(async (nodeId) => {
    try {
      const state = await api.deleteNode(nodeId)
      loadState(state)
      setSelected(null)
    } catch (err) { console.error(err) }
  }, [])

  const handleSaveEdge = useCallback(async (index, updates) => {
    try {
      const state = await api.updateEdge(index, updates)
      loadState(state)
      const e = state.edges[index]
      if (e) setSelected({ type: 'edge', data: toRFEdge(e, index).data })
    } catch (err) { console.error(err) }
  }, [])

  const handleDeleteEdge = useCallback(async (index) => {
    try {
      const state = await api.deleteEdge(index)
      loadState(state)
      setSelected(null)
    } catch (err) { console.error(err) }
  }, [])

  const handleEdgeConfirm = useCallback(async (props) => {
    if (!pendingConn) return
    const from_id = parseInt(pendingConn.source)
    const to_id   = parseInt(pendingConn.target)
    try {
      const state = await api.addEdge({ from_id, to_id, ...props })
      loadState(state)
    } catch (err) { console.error(err) }
    setPendingConn(null)
  }, [pendingConn])

  const handleSaveMap = useCallback(async () => {
    setSaving(true)
    try {
      const { filename } = await api.saveMap()
      notify(`Saved: ${filename}`)
    } catch (err) {
      notify(`Save failed: ${err.message}`, 'error')
    } finally {
      setSaving(false)
    }
  }, [])

  const handleDownload = useCallback(() => {
    notify('Downloaded map.json')
  }, [])

  const handleLoadFile = useCallback(async (file) => {
    try {
      const state = await api.loadFile(file)
      loadState(state)
      setSelected(null)
      notify(`Loaded: ${file.name}`)
    } catch (err) {
      notify(`Load failed: ${err.message}`, 'error')
    }
  }, [])

  // ── React Flow props ────────────────────────────────────

  const isPan = activeTool === 'pan'

  return (
    <div className="editor-root">
      <Toolbar
        activeTool={activeTool}
        onToolChange={setActiveTool}
        meta={meta}
        onSave={handleSaveMap}
        saving={saving}
        onDownload={handleDownload}
        onLoadFile={handleLoadFile}
        onThemeToggle={toggleTheme}
        theme={theme}
      />
      <div className="editor-body">
        <div className="editor-canvas" style={{ cursor: isPan ? undefined : 'crosshair' }}>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeDragStop={onNodeDragStop}
            onNodesDelete={onNodesDelete}
            onEdgesDelete={onEdgesDelete}
            onNodeClick={onNodeClick}
            onEdgeClick={onEdgeClick}
            onPaneClick={isPan ? onPaneClickClear : onPaneClick}
            nodeTypes={NODE_TYPES}
            connectionMode={ConnectionMode.Loose}
            snapToGrid
            snapGrid={[GRID_SIZE, GRID_SIZE]}
            panOnDrag={isPan ? [0, 1, 2] : false}
            nodesDraggable={isPan}
            nodesConnectable={isPan}
            elementsSelectable={isPan}
            deleteKeyCode={isPan ? 'Delete' : null}
            fitView
            fitViewOptions={{ padding: 0.3 }}
            colorMode={theme}
          >
            <Background gap={GRID_SIZE} size={1} />
            <Controls />
            <MiniMap
              nodeColor={n => NODE_COLORS[n.data?.nodeType] || '#6c757d'}
              nodeStrokeWidth={2}
            />
          </ReactFlow>
        </div>
        <PropertiesPanel
          selected={selected}
          nodes={nodes}
          edges={edges}
          onSaveNode={handleSaveNode}
          onDeleteNode={handleDeleteNode}
          onSaveEdge={handleSaveEdge}
          onDeleteEdge={handleDeleteEdge}
        />
      </div>

      {pendingConn && (
        <EdgeDialog
          connection={pendingConn}
          nodes={nodes}
          onConfirm={handleEdgeConfirm}
          onCancel={() => setPendingConn(null)}
        />
      )}

      <Notifications items={notifications} onDismiss={dismissNotification} />
    </div>
  )
}

// ─────────────────────────────────────────────────────────
// Exported root — wraps inner in ReactFlowProvider
// ─────────────────────────────────────────────────────────

export function App() {
  return (
    <ReactFlowProvider>
      <EditorInner />
    </ReactFlowProvider>
  )
}
