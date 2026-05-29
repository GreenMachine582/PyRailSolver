import { Link, useLocation } from 'react-router-dom'

export function NavBar({ theme, onThemeToggle }) {
  const { pathname } = useLocation()

  return (
    <nav className="prs-nav">
      <Link className="prs-nav-brand" to="/">&#x1F686; PyRailSolver</Link>
      <div className="prs-nav-spacer" />
      <Link className={`prs-nav-link${pathname === '/' ? ' active' : ''}`} to="/">
        Maps
      </Link>
      <Link className={`prs-nav-link${pathname === '/editor' ? ' active' : ''}`} to="/editor">
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
