import { useState, useCallback, useEffect, useRef } from 'react'
import { useBlocker } from 'react-router-dom'
import {
  ReactFlow, Background, Controls, MiniMap,
  useNodesState, useEdgesState,
  ConnectionMode,
  useReactFlow, ReactFlowProvider,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'

import { RailNode }        from '../nodeTypes/RailNode'
import { Toolbar }         from '../components/Toolbar'
import { PropertiesPanel } from '../components/PropertiesPanel'
import { EdgeDialog }      from '../components/EdgeDialog'
import { Notifications }   from '../components/Notifications'
import { UnsavedModal }    from '../components/UnsavedModal'
import { PageLayout }      from '../components/PageLayout'
import { api }             from '../api'
import { GRID_SIZE, NODE_COLORS, DEFAULT_EDGE_TYPE } from '../constants'
import { toRFNode, toRFEdge }     from '../utils/flowConvert'
import { useTheme }               from '../hooks/useTheme'

const NODE_TYPES = { railNode: RailNode }

function EditorInner() {
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])
  const [meta,        setMeta]       = useState({ name: 'Loading…', width: 20, height: 15 })
  const [activeTool,  setActiveTool] = useState('pan')
  const [selected,    setSelected]   = useState(null)
  const [pendingConn, setPendingConn] = useState(null)
  const [theme]                       = useTheme()
  const [saving, setSaving]          = useState(false)
  const [isDirty, setIsDirty]        = useState(false)
  const [edgeType, setEdgeType]      = useState(
    () => localStorage.getItem('prs-edge-type') || DEFAULT_EDGE_TYPE
  )
  const [notifications, setNotifications] = useState([])
  const blocker = useBlocker(isDirty)

  useEffect(() => {
    localStorage.setItem('prs-edge-type', edgeType)
  }, [edgeType])

  function notify(message, type = 'success') {
    const id = Date.now()
    setNotifications(prev => [...prev, { id, message, type }])
  }

  function dismissNotification(id) {
    setNotifications(prev => prev.filter(n => n.id !== id))
  }

  const { screenToFlowPosition } = useReactFlow()
  const deletingNodes = useRef(false)

  function loadState(state, dirty = false) {
    setMeta(state.meta)
    setNodes(state.nodes.map(toRFNode))
    setEdges(state.edges.map((e, i) => toRFEdge(e, i)))
    if (dirty) setIsDirty(true)
  }

  useEffect(() => {
    api.getState().then(s => {
      loadState(s)
      if (s.nodes.length > 0 || s.edges.length > 0) {
        notify(`Session restored: "${s.meta.name}"`, 'info')
      }
    }).catch(console.error)
  }, [])

  const onPaneClick = useCallback(async (e) => {
    if (activeTool === 'pan') return
    const pos = screenToFlowPosition({ x: e.clientX, y: e.clientY })
    const gx = Math.max(0, Math.min(meta.width  - 1, Math.round(pos.x / GRID_SIZE)))
    const gy = Math.max(0, Math.min(meta.height - 1, Math.round(pos.y / GRID_SIZE)))
    try {
      const state = await api.addNode({ x: gx, y: gy, node_type: activeTool, name: '' })
      loadState(state, true)
      const newNode = state.nodes.at(-1)
      if (newNode) setSelected({ type: 'node', data: toRFNode(newNode).data })
    } catch (err) { console.error(err) }
  }, [activeTool, meta, screenToFlowPosition])

  const onConnect = useCallback((connection) => setPendingConn(connection), [])

  const onNodeDragStop = useCallback(async (_, node) => {
    const gx = Math.max(0, Math.min(meta.width  - 1, Math.round(node.position.x / GRID_SIZE)))
    const gy = Math.max(0, Math.min(meta.height - 1, Math.round(node.position.y / GRID_SIZE)))
    try {
      const state = await api.moveNode(parseInt(node.id), gx, gy)
      loadState(state, true)
    } catch (err) { console.error(err) }
  }, [meta])

  const onNodesDelete = useCallback(async (deleted) => {
    deletingNodes.current = true
    try {
      for (const n of deleted) await api.deleteNode(parseInt(n.id))
      const state = await api.getState()
      loadState(state, true)
      setSelected(null)
    } catch (err) { console.error(err) }
    finally { deletingNodes.current = false }
  }, [])

  const onEdgesDelete = useCallback(async (deleted) => {
    if (deletingNodes.current) return
    const indices = [...new Set(deleted.map(e => e.data.index))].sort((a, b) => b - a)
    try {
      for (const idx of indices) await api.deleteEdge(idx)
      const state = await api.getState()
      loadState(state, true)
      setSelected(null)
    } catch (err) { console.error(err) }
  }, [])

  const onNodeClick    = useCallback((_, node) => setSelected({ type: 'node', data: node.data }), [])
  const onEdgeClick    = useCallback((_, edge) => setSelected({ type: 'edge', data: edge.data }), [])
  const onPaneClickClear = useCallback(() => { if (activeTool === 'pan') setSelected(null) }, [activeTool])

  const handleSaveNode = useCallback(async (nodeId, name, nodeType) => {
    try {
      const state = await api.updateNode(nodeId, { name, node_type: nodeType })
      loadState(state, true)
      const updated = state.nodes.find(n => n.id === nodeId)
      if (updated) setSelected({ type: 'node', data: toRFNode(updated).data })
    } catch (err) { console.error(err) }
  }, [])

  const handleDeleteNode = useCallback(async (nodeId) => {
    try { const state = await api.deleteNode(nodeId); loadState(state, true); setSelected(null) }
    catch (err) { console.error(err) }
  }, [])

  const handleSaveEdge = useCallback(async (index, updates) => {
    try {
      const state = await api.updateEdge(index, updates)
      loadState(state, true)
      const e = state.edges[index]
      if (e) setSelected({ type: 'edge', data: toRFEdge(e, index).data })
    } catch (err) { console.error(err) }
  }, [])

  const handleDeleteEdge = useCallback(async (index) => {
    try { const state = await api.deleteEdge(index); loadState(state, true); setSelected(null) }
    catch (err) { console.error(err) }
  }, [])

  const handleEdgeConfirm = useCallback(async (props) => {
    if (!pendingConn) return
    const from_id = parseInt(pendingConn.source)
    const to_id = parseInt(pendingConn.target)
    const source_handle = pendingConn.sourceHandle || ''
    const target_handle = pendingConn.targetHandle || ''
    try {
      const state = await api.addEdge({ from_id, to_id, source_handle, target_handle, ...props })
      loadState(state, true)
    }
    catch (err) { console.error(err) }
    setPendingConn(null)
  }, [pendingConn])

  const handleSaveMap = useCallback(async () => {
    setSaving(true)
    try {
      const { filename } = await api.saveMap()
      notify(`Saved: ${filename}`)
      setIsDirty(false)
      return true
    } catch (err) {
      notify(`Save failed: ${err.message}`, 'error')
      return false
    } finally {
      setSaving(false)
    }
  }, [])

  const handleRename = useCallback(async (name) => {
    try {
      const state = await api.renamemap(name)
      loadState(state, true)
      notify(`Renamed to "${name}"`)
    } catch (err) {
      notify(`Rename failed: ${err.message}`, 'error')
    }
  }, [])

  const handleDownload = useCallback(() => notify('Downloaded map.json'), [])

  const handleLoadFile = useCallback(async (file) => {
    try {
      const state = await api.loadFile(file)
      loadState(state, true)
      setSelected(null)
      notify(`Loaded: ${file.name}`)
    } catch (err) {
      notify(`Load failed: ${err.message}`, 'error')
    }
  }, [])

  const handleSaveAndLeave = useCallback(async () => {
    const saved = await handleSaveMap()
    if (saved) blocker.proceed()
  }, [handleSaveMap, blocker])

  const handleDiscard = useCallback(() => {
    setIsDirty(false)
    blocker.proceed()
  }, [blocker])

  const isPan = activeTool === 'pan'

  return (
    <PageLayout className="editor-root" fluid>
      <Toolbar
        activeTool={activeTool}
        onToolChange={setActiveTool}
        meta={meta}
        onRename={handleRename}
        onRenameError={(msg) => notify(msg, 'error')}
        onSave={handleSaveMap}
        saving={saving}
        onDownload={handleDownload}
        onLoadFile={handleLoadFile}
        edgeType={edgeType}
        onEdgeTypeChange={setEdgeType}
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
          defaultEdgeType={edgeType}
          onConfirm={handleEdgeConfirm}
          onCancel={() => setPendingConn(null)}
        />
      )}

      <Notifications items={notifications} onDismiss={dismissNotification} />

      {blocker.state === 'blocked' && (
        <UnsavedModal
          mapName={meta.name}
          saving={saving}
          onSave={handleSaveAndLeave}
          onDiscard={handleDiscard}
          onCancel={() => blocker.reset()}
        />
      )}
    </PageLayout>
  )
}

export function EditorPage() {
  return (
    <ReactFlowProvider>
      <EditorInner />
    </ReactFlowProvider>
  )
}
