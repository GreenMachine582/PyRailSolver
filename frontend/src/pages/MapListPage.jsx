import { useState, useEffect, useCallback } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../api'
import { PageLayout } from '../components/PageLayout'

export function MapListPage() {
  const [maps,          setMaps]          = useState([])
  const [loading,       setLoading]       = useState(true)
  const [error,         setError]         = useState(null)
  const [confirmDelete, setConfirmDelete] = useState(null)
  const navigate = useNavigate()

  const loadMaps = useCallback(() => {
    api.getMaps()
      .then(setMaps)
      .catch(err => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => { loadMaps() }, [loadMaps])

  async function handleNewMap() {
    try {
      await api.resetEditor()
      navigate('/editor')
    } catch (err) {
      setError(`Could not start new map: ${err.message}`)
    }
  }

  async function handleEdit(name) {
    try {
      await api.openMap(name)
      navigate('/editor')
    } catch (err) {
      setError(`Could not open map: ${err.message}`)
    }
  }

  async function handleDelete(name) {
    try {
      await api.deleteMap(name)
      setConfirmDelete(null)
      setMaps(prev => prev.filter(m => m.slug !== name))
    } catch (err) {
      setError(`Could not delete map: ${err.message}`)
      setConfirmDelete(null)
    }
  }

  return (
    <PageLayout>
      <div className="page-heading">
        <h1 className="page-title">Available Maps</h1>
        <button className="prs-btn" onClick={handleNewMap}>+ New Map</button>
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
          {maps.map(({ name, slug, editable }) => (
            <div key={slug} className="map-list-item">
              <Link to={`/maps/${slug}`} className="map-list-name">{name}</Link>
              <div className="d-flex align-items-center gap-2">
                {confirmDelete === slug ? (
                  <>
                    <span className="text-danger small">Delete?</span>
                    <button className="btn btn-danger btn-sm"         onClick={() => handleDelete(slug)}>Yes</button>
                    <button className="btn btn-outline-secondary btn-sm" onClick={() => setConfirmDelete(null)}>No</button>
                  </>
                ) : (
                  <>
                    <Link to={`/maps/${slug}`} className="map-list-badge">View</Link>
                    {editable && (
                      <>
                        <button
                          className="btn btn-outline-secondary btn-sm"
                          title="Open in editor"
                          onClick={() => handleEdit(slug)}
                        >
                          <i className="bi bi-pencil" />
                        </button>
                        <button
                          className="btn btn-outline-danger btn-sm"
                          title="Delete map"
                          onClick={() => setConfirmDelete(slug)}
                        >
                          <i className="bi bi-trash" />
                        </button>
                      </>
                    )}
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </PageLayout>
  )
}
