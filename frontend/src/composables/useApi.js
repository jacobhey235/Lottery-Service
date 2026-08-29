const BASE = import.meta.env.VITE_API_BASE_URL || ''

export async function apiUpload(formData) {
  const res = await fetch(`${BASE}/api/upload`, { method: 'POST', body: formData })
  if (!res.ok) throw await res.json()
  return res.json()
}

export async function apiStatus() {
  const res = await fetch(`${BASE}/api/status`)
  return res.json()
}

export async function apiVotingQueue(userId) {
  const res = await fetch(`${BASE}/api/voting/queue`, {
    headers: { 'X-User-ID': userId },
  })
  if (!res.ok) throw await res.json()
  return res.json()
}

export async function apiVote(userId, photoId, liked) {
  const res = await fetch(`${BASE}/api/vote`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-User-ID': userId },
    body: JSON.stringify({ photo_id: photoId, liked }),
  })
  if (!res.ok) throw await res.json()
  return res.json()
}

export async function apiResults() {
  const res = await fetch(`${BASE}/api/results`)
  if (!res.ok) throw await res.json()
  return res.json()
}

export function photoUrl(photoId, userId) {
  return `${BASE}/api/photos/${photoId}/image`
}

export async function adminLogin(password) {
  const res = await fetch(`${BASE}/api/admin/session`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ password }),
  })
  if (!res.ok) throw await res.json()
  return res.json()
}

export async function adminListPhotos(token) {
  const res = await fetch(`${BASE}/api/admin/photos`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!res.ok) throw await res.json()
  return res.json()
}

export async function adminDeletePhoto(token, photoId) {
  const res = await fetch(`${BASE}/api/admin/photos/${photoId}`, {
    method: 'DELETE',
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!res.ok) throw await res.json()
  return res.json()
}

export async function adminStartContest(token) {
  const res = await fetch(`${BASE}/api/admin/contest/start`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!res.ok) throw await res.json()
  return res.json()
}

export async function adminEndContest(token) {
  const res = await fetch(`${BASE}/api/admin/contest/end`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!res.ok) throw await res.json()
  return res.json()
}

export async function adminRestartContest(token) {
  const res = await fetch(`${BASE}/api/admin/contest/restart`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!res.ok) throw await res.json()
  return res.json()
}
