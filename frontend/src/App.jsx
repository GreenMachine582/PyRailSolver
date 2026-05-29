import { Routes, Route } from 'react-router-dom'
import './editor.css'
import { ThemeProvider } from './hooks/useTheme'
import { MapListPage }   from './pages/MapListPage'
import { MapViewerPage } from './pages/MapViewerPage'
import { EditorPage }    from './pages/EditorPage'

export function App() {
  return (
    <ThemeProvider>
      <Routes>
        <Route path="/"           element={<MapListPage />} />
        <Route path="/maps/:name" element={<MapViewerPage />} />
        <Route path="/editor"     element={<EditorPage />} />
      </Routes>
    </ThemeProvider>
  )
}
