import { useState, useCallback, useEffect } from 'react'
import { useBlocker } from 'react-router-dom'
import {
  ReactFlow, Background, Controls, MiniMap,
  ConnectionMode, ReactFlowProvider,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'

import { NODE_TYPES }      from '../nodeTypes/RailNode'
import { Toolbar }         from '../components/Toolbar'
import { PropertiesPanel } from '../components/PropertiesPanel'
import { EdgeDialog }      from '../components/EdgeDialog'
import { Notifications }   from '../components/Notifications'
import { UnsavedModal }    from '../components/UnsavedModal'
import { PageLayout }      from '../components/PageLayout'
import { GRID_SIZE, NODE_COLORS, DEFAULT_EDGE_TYPE } from '../constants'
import { useTheme }        from '../hooks/useTheme'
import { useEditorState }  from '../hooks/useEditorState'
import { useFileOps }      from '../hooks/useFileOps'

function EditorInner() {
  const [activeTool, setActiveTool] = useState('pan')
  const [edgeType, setEdgeType]     = useState(
    () => localStorage.getItem('prs-edge-type') || DEFAULT_EDGE_TYPE
  )
  const [theme] = useTheme()

  const {
    nodes, onNodesChange, edges, onEdgesChange,
    meta, isDirty, setIsDirty,
    selected, setSelected, pendingConn, setPendingConn,
    notifications, dismissNotification,
    loadState, notify,
    onPaneClick, onConnect, onNodeDragStop,
    onNodesDelete, onEdgesDelete,
    onNodeClick, onEdgeClick, onPaneClickClear,
    handleSaveNode, handleDeleteNode,
    handleSaveEdge, handleDeleteEdge, handleEdgeConfirm,
  } = useEditorState(activeTool)

  const { saving, handleSaveMap, handleRename, handleDownload, handleLoadFile } = useFileOps({
    loadState, notify, setSelected, setIsDirty,
  })

  const blocker = useBlocker(isDirty)

  useEffect(() => {
    localStorage.setItem('prs-edge-type', edgeType)
  }, [edgeType])

  const handleSaveAndLeave = useCallback(async () => {
    const saved = await handleSaveMap()
    if (saved) blocker.proceed()
  }, [handleSaveMap, blocker])

  const handleDiscard = useCallback(() => {
    setIsDirty(false)
    blocker.proceed()
  }, [blocker, setIsDirty])

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
