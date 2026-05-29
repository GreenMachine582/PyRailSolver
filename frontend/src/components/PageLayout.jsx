import { NavBar } from './NavBar'
import { useTheme } from '../hooks/useTheme'

export function PageLayout({ children, className = 'page-root', fluid = false }) {
  const [theme, toggleTheme] = useTheme()

  return (
    <div className={className}>
      <NavBar theme={theme} onThemeToggle={toggleTheme} />
      {fluid ? children : <main className="page-main">{children}</main>}
    </div>
  )
}
