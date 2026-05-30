import { useParams, Link } from 'react-router-dom'
import { useState, useEffect } from 'react'
import {
  ReactFlow, Background, Controls, MiniMap,
  ReactFlowProvider, useNodesState, useEdgesState,
  ConnectionMode,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'

import { api }          from '../api'
import { PageLayout }   from '../components/PageLayout'
import { NODE_TYPES }   from '../nodeTypes/RailNode'
import { NODE_COLORS }  from '../constants'
import { toRFNode, toRFEdge } from '../utils/flowConvert'
import { useTheme }     from '../hooks/useTheme'

const toViewerNode = (node) => {
  const rf = toRFNode(node)
  return { ...rf, data: { ...rf.data, viewer: true } }
}

function ViewerCanvas({ mapData, theme }) {
  const [nodes, , onNodesChange] = useNodesState(mapData.nodes.map(toViewerNode))
  const [edges, , onEdgesChange] = useEdgesState(mapData.edges.map((e, i) => toRFEdge(e, i)))

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      nodeTypes={NODE_TYPES}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      connectionMode={ConnectionMode.Loose}
      nodesDraggable={false}
      nodesConnectable={false}
      elementsSelectable={false}
      panOnDrag
      fitView
      fitViewOptions={{ padding: 0.3 }}
      colorMode={theme}
    >
      <Background />
      <Controls />
      <MiniMap
        nodeColor={n => NODE_COLORS[n.data?.nodeType] || '#6c757d'}
        nodeStrokeWidth={2}
      />
    </ReactFlow>
  )
}

export function MapViewerPage() {
  const { name } = useParams()
  const [mapData, setMapData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState(null)
  const [theme]               = useTheme()

  useEffect(() => {
    setLoading(true)
    setError(null)
    api.getMap(name)
      .then(setMapData)
      .catch(err => setError(err.message))
      .finally(() => setLoading(false))
  }, [name])

  return (
    <PageLayout className="viewer-root" fluid>
      {loading && (
        <div className="viewer-status"><p className="text-muted mb-0">Loading…</p></div>
      )}
      {error && (
        <div className="viewer-status"><div className="prs-alert prs-alert--danger">{error}</div></div>
      )}

      {mapData && (
        <>
          <div className="viewer-header">
            <Link to="/" className="viewer-back" title="Back to Maps"><i className="bi bi-arrow-left" /></Link>
            <div className="viewer-sep" />
            <span className="viewer-title">{mapData.meta.name}</span>
            <div className="viewer-sep" />
            <span className="viewer-stat">{mapData.stats.node_count} nodes</span>
            <span className="viewer-stat">{mapData.stats.edge_count} edges</span>
            {mapData.stats.train_count > 0 && (
              <span className="viewer-stat">{mapData.stats.train_count} trains</span>
            )}
            <span className="viewer-stat">{mapData.meta.width}×{mapData.meta.height}</span>
            {!mapData.is_valid && (
              <span className="viewer-badge-invalid ms-1">Invalid</span>
            )}
          </div>

          {(mapData.errors.length > 0 || mapData.warnings.length > 0) && (
            <div className="viewer-alerts">
              {mapData.errors.map((e, i) => (
                <div key={i} className="viewer-alert viewer-alert--error">{e}</div>
              ))}
              {mapData.warnings.map((w, i) => (
                <div key={i} className="viewer-alert viewer-alert--warn">{w}</div>
              ))}
            </div>
          )}

          <div className="viewer-canvas">
            <ReactFlowProvider>
              <ViewerCanvas mapData={mapData} theme={theme} />
            </ReactFlowProvider>
          </div>
        </>
      )}
    </PageLayout>
  )
}
