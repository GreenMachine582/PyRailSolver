import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'
import { PageLayout } from '../components/PageLayout'

export function MapListPage() {
  const [maps,    setMaps]    = useState([])
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState(null)

  useEffect(() => {
    api.getMaps()
      .then(setMaps)
      .catch(err => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  return (
    <PageLayout>
      <div className="page-heading">
        <h1 className="page-title">Available Maps</h1>
        <Link to="/editor" className="prs-btn">+ New Map</Link>
      </div>

      {loading && <p className="text-secondary">Loading…</p>}

      {error && (
        <div className="prs-alert prs-alert--danger">{error}</div>
      )}

      {!loading && !error && maps.length === 0 && (
        <div className="prs-empty">
          No maps found. Add <code>.csv</code> files to the <code>examples/</code> or{' '}
          <code>maps/</code> directory.
        </div>
      )}

      {maps.length > 0 && (
        <div className="map-list">
          {maps.map(name => (
            <Link key={name} to={`/maps/${name}`} className="map-list-item">
              <span className="map-list-name">{name}</span>
              <span className="map-list-badge">View</span>
            </Link>
          ))}
        </div>
      )}
    </PageLayout>
  )
}
