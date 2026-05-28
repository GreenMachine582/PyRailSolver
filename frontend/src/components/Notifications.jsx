export function Notifications({ items, onDismiss }) {
  return (
    <div className="toast-container">
      {items.map(n => (
        <div
          key={n.id}
          className={`toast-item toast-${n.type}`}
          onAnimationEnd={() => onDismiss(n.id)}
        >
          {n.message}
        </div>
      ))}
    </div>
  )
}
