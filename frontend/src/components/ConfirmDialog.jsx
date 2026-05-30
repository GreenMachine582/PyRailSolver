export function ConfirmDialog({ message, onConfirm, onCancel }) {
  return (
    <div className="dialog-overlay">
      <div className="dialog-box" style={{ minWidth: 260, maxWidth: 340 }}>
        <div className="dialog-header">
          <h6 className="mb-0">Confirm</h6>
          <button className="btn-close btn-sm" onClick={onCancel} aria-label="Close" />
        </div>
        <div className="dialog-body">
          <p className="small mb-3">{message}</p>
          <div className="d-flex gap-2">
            <button className="btn btn-danger btn-sm" onClick={onConfirm}>Delete</button>
            <button className="btn btn-outline-secondary btn-sm" onClick={onCancel}>Cancel</button>
          </div>
        </div>
      </div>
    </div>
  )
}
