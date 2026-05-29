import { Link, useLocation, useNavigate } from 'react-router-dom'
import { api } from '../api'

export function NavBar({ theme, onThemeToggle }) {
  const { pathname } = useLocation()
  const navigate     = useNavigate()

  // If we're on a viewer page, extract the slug so the Editor button opens that map.
  const viewerMatch = pathname.match(/^\/maps\/([^/]+)$/)
  const viewerSlug  = viewerMatch ? decodeURIComponent(viewerMatch[1]) : null

  async function handleEditorClick(e) {
    if (!viewerSlug) return            // not on viewer — let Link navigate normally
    e.preventDefault()
    try { await api.openMap(viewerSlug) } catch { /* fall through — open editor with current state */ }
    navigate('/editor')
  }

  return (
    <nav className="prs-nav">
      <Link className="prs-nav-brand" to="/">&#x1F686; PyRailSolver</Link>
      <div className="prs-nav-spacer" />
      <Link className={`prs-nav-link${pathname === '/' ? ' active' : ''}`} to="/">
        Maps
      </Link>
      <Link
        className={`prs-nav-link${pathname === '/editor' ? ' active' : ''}`}
        to="/editor"
        onClick={handleEditorClick}
      >
        Editor
      </Link>
      <button
        className="prs-nav-btn prs-nav-btn--icon"
        title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
        onClick={onThemeToggle}
      >
        <i className={theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-fill'} />
      </button>
    </nav>
  )
}
