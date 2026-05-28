const BASE = '/api/editor'

async function _json(res) {
  if (!res.ok) {
    let detail = res.statusText
    try { detail = (await res.json()).detail ?? detail } catch { /* */ }
    throw new Error(`${res.status}: ${detail}`)
  }
  return res.json()
}

function _post(url, body) {
  return fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  }).then(_json)
}

function _put(url, body) {
  return fetch(url, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  }).then(_json)
}

function _patch(url, body) {
  return fetch(url, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  }).then(_json)
}

function _del(url) {
  return fetch(url, { method: 'DELETE' }).then(_json)
}

export const api = {
  getState:   ()             => fetch(`${BASE}/state`).then(_json),
  addNode:    (data)         => _post(`${BASE}/nodes`, data),
  updateNode: (id, data)     => _put(`${BASE}/nodes/${id}`, data),
  moveNode:   (id, x, y)     => _patch(`${BASE}/nodes/${id}/position`, { x, y }),
  deleteNode: (id)           => _del(`${BASE}/nodes/${id}`),
  addEdge:    (data)         => _post(`${BASE}/edges`, data),
  updateEdge: (idx, data)    => _put(`${BASE}/edges/${idx}`, data),
  deleteEdge: (idx)          => _del(`${BASE}/edges/${idx}`),
  renamemap:  (name)         => _patch(`${BASE}/meta`, { name }),
  saveMap:    ()             => _post(`${BASE}/save`, {}),
  loadFile:   (file)         => {
    const fd = new FormData()
    fd.append('file', file)
    return fetch(`${BASE}/load`, { method: 'POST', body: fd }).then(_json)
  },
}
