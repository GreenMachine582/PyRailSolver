import { useState, useCallback, useEffect, useRef } from 'react'
import { useNodesState, useEdgesState, useReactFlow } from '@xyflow/react'

import { api }              from '../api'
import { GRID_SIZE }        from '../constants'
import { toRFNode, toRFEdge } from '../utils/flowConvert'

export function useEditorState(activeTool) {
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])
  const [meta,         setMeta]        = useState({ name: 'Loading…', width: 20, height: 15 })
  const [isDirty,      setIsDirty]     = useState(false)
  const [selected,     setSelected]    = useState(null)
  const [pendingConn,  setPendingConn] = useState(null)
  const [notifications, setNotifications] = useState([])
  const deletingNodes = useRef(false)
  const { screenToFlowPosition } = useReactFlow()

  function loadState(state, dirty = false) {
    setMeta(state.meta)
    setNodes(state.nodes.map(toRFNode))
    setEdges(state.edges.map((e, i) => toRFEdge(e, i)))
    if (dirty) setIsDirty(true)
  }

  function notify(message, type = 'success') {
    const id = Date.now()
    setNotifications(prev => [...prev, { id, message, type }])
  }

  function dismissNotification(id) {
    setNotifications(prev => prev.filter(n => n.id !== id))
  }

  useEffect(() => {
    api.getState().then(s => {
      loadState(s)
      if (s.nodes.length > 0 || s.edges.length > 0)
        notify(`Session restored: "${s.meta.name}"`, 'info')
    }).catch(console.error)
  }, [])

  // ── Canvas interaction ──────────────────────────────────

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

  const onNodeClick     = useCallback((_, node) => setSelected({ type: 'node', data: node.data }), [])
  const onEdgeClick     = useCallback((_, edge) => setSelected({ type: 'edge', data: edge.data }), [])
  const onPaneClickClear = useCallback(() => { if (activeTool === 'pan') setSelected(null) }, [activeTool])

  // ── Properties panel handlers ───────────────────────────

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
    const from_id       = parseInt(pendingConn.source)
    const to_id         = parseInt(pendingConn.target)
    const source_handle = pendingConn.sourceHandle || ''
    const target_handle = pendingConn.targetHandle || ''
    try {
      const state = await api.addEdge({ from_id, to_id, source_handle, target_handle, ...props })
      loadState(state, true)
    } catch (err) { console.error(err) }
    setPendingConn(null)
  }, [pendingConn])

  return {
    nodes, onNodesChange,
    edges, onEdgesChange,
    meta, isDirty, setIsDirty,
    selected, setSelected,
    pendingConn, setPendingConn,
    notifications, dismissNotification,
    loadState, notify,
    onPaneClick, onConnect, onNodeDragStop,
    onNodesDelete, onEdgesDelete,
    onNodeClick, onEdgeClick, onPaneClickClear,
    handleSaveNode, handleDeleteNode,
    handleSaveEdge, handleDeleteEdge, handleEdgeConfirm,
  }
}
