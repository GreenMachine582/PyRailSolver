import { createBrowserRouter } from 'react-router-dom'
import { MapListPage }   from './pages/MapListPage'
import { MapViewerPage } from './pages/MapViewerPage'
import { EditorPage }    from './pages/EditorPage'

export const router = createBrowserRouter([
  { path: '/',           element: <MapListPage /> },
  { path: '/maps/:name', element: <MapViewerPage /> },
  { path: '/editor',     element: <EditorPage /> },
])
