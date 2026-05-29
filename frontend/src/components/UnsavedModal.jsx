export function UnsavedModal({ mapName, saving, onSave, onDiscard, onCancel }) {
  return (
    <div className="dialog-overlay">
      <div className="dialog-box" style={{ maxWidth: 380 }}>
        <div className="dialog-header">
          <h6 className="mb-0">Unsaved Changes</h6>
          <button className="btn-close btn-sm" onClick={onCancel} aria-label="Cancel" />
        </div>
        <div className="dialog-body">
          <p className="small mb-3">
            <strong>{mapName}</strong> has unsaved changes. Save before leaving?
          </p>
          <div className="d-flex gap-2">
            <button className="btn btn-primary btn-sm" onClick={onSave} disabled={saving}>
              {saving ? 'Saving…' : 'Save & Leave'}
            </button>
            <button className="btn btn-outline-danger btn-sm" onClick={onDiscard}>
              Discard
            </button>
            <button className="btn btn-outline-secondary btn-sm" onClick={onCancel}>
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
