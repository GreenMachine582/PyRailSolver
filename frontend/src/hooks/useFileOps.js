import { useState, useCallback } from 'react'
import { api } from '../api'

export function useFileOps({ loadState, notify, setSelected, setIsDirty }) {
  const [saving, setSaving] = useState(false)

  const handleSaveMap = useCallback(async () => {
    setSaving(true)
    try {
      const { filename } = await api.saveMap()
      notify(`Saved: ${filename}`)
      setIsDirty(false)
      return true
    } catch (err) {
      notify(`Save failed: ${err.message}`, 'error')
      return false
    } finally {
      setSaving(false)
    }
  }, [notify, setIsDirty])

  const handleRename = useCallback(async (name) => {
    try {
      const state = await api.renamemap(name)
      loadState(state, true)
      notify(`Renamed to "${name}"`)
    } catch (err) {
      notify(`Rename failed: ${err.message}`, 'error')
    }
  }, [loadState, notify])

  const handleDownload = useCallback(() => notify('Downloaded map.json'), [notify])

  const handleLoadFile = useCallback(async (file) => {
    try {
      const state = await api.loadFile(file)
      loadState(state, true)
      setSelected(null)
      notify(`Loaded: ${file.name}`)
    } catch (err) {
      notify(`Load failed: ${err.message}`, 'error')
    }
  }, [loadState, notify, setSelected])

  return { saving, handleSaveMap, handleRename, handleDownload, handleLoadFile }
}
