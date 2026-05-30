import { NodePanel } from './NodePanel'
import { EdgePanel } from './EdgePanel'

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
