import { onUnmounted, ref } from 'vue'

function makeWs(getUrl, onMessage, onConnected, onClose) {
  const connected = ref(false)
  let ws = null
  let retryDelay = 1000
  let retryTimer = null
  let destroyed = false

  function connect() {
    if (destroyed) return
    const url = typeof getUrl === 'function' ? getUrl() : getUrl
    if (!url) return

    ws = new WebSocket(url)

    ws.onopen = () => {
      connected.value = true
      retryDelay = 1000
      if (onConnected) onConnected()
    }

    ws.onmessage = (e) => {
      try {
        const msg = JSON.parse(e.data)
        onMessage(msg)
      } catch {}
    }

    ws.onclose = (e) => {
      connected.value = false
      if (onClose) onClose(e)
      // 4001 = rejected by server (unknown/deleted user) — don't retry
      if (!destroyed && e.code !== 4001) {
        retryTimer = setTimeout(() => {
          retryDelay = Math.min(retryDelay * 2, 30000)
          connect()
        }, retryDelay)
      }
    }

    ws.onerror = () => ws.close()
  }

  function disconnect() {
    destroyed = true
    clearTimeout(retryTimer)
    if (ws) ws.close()
  }

  onUnmounted(disconnect)

  return { connected, connect, disconnect }
}

function buildWsUrl(path) {
  const apiBase = import.meta.env.VITE_API_BASE_URL
  if (apiBase) {
    const wsBase = apiBase.replace(/^https/, 'wss').replace(/^http/, 'ws')
    return `${wsBase}${path}`
  }
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
  return `${protocol}://${window.location.host}${path}`
}

export function useWebSocket(getUserId, onMessage, onClose) {
  return makeWs(
    () => {
      const uid = typeof getUserId === 'function' ? getUserId() : getUserId
      if (!uid) return null
      return buildWsUrl(`/ws?user_id=${uid}`)
    },
    onMessage,
    undefined,
    onClose,
  )
}

export function useAdminWebSocket(getToken, onMessage) {
  return makeWs(
    () => {
      const tok = typeof getToken === 'function' ? getToken() : getToken
      if (!tok) return null
      return buildWsUrl(`/ws?admin_token=${tok}`)
    },
    onMessage,
  )
}
