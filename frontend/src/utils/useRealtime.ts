import { onBeforeUnmount, onMounted, ref } from 'vue'

export type RealtimeChannel = 'websocket' | 'sse' | 'poll' | 'offline'

/**
 * 实时数据同步：三级通道保障。
 * 1. 优先 WebSocket 长连接（/api/realtime/ws/），数据变更后 1 秒内推送；
 * 2. WS 不可用时自动降级 SSE（/api/realtime/stream/）；
 * 3. 800ms 版本轮询作为最终兜底，任何通道失效时仍保证 1 秒内同步。
 * 断线后按指数退避自动重连，重连成功立即触发全量数据拉取，避免数据断层。
 */
export function useRealtime(onChange: (reason?: string) => void, options: { pollInterval?: number } = {}) {
  const connected = ref(false)
  const channel = ref<RealtimeChannel>('offline')
  const lastVersion = ref('')
  const lastSyncAt = ref('')
  let ws: WebSocket | null = null
  let source: EventSource | null = null
  let pollTimer: number | null = null
  let pingTimer: number | null = null
  let reconnectTimer: number | null = null
  let retryCount = 0
  let everConnected = false
  let disposed = false

  const httpBase = (() => {
    if (typeof document === 'undefined') return '/api'
    // 生产环境通过环境变量配置后端地址
    if (import.meta.env.VITE_API_BASE_URL) {
      return import.meta.env.VITE_API_BASE_URL
    }
    const hasViteClient = !!document.querySelector('script[src="/@vite/client"]')
    return hasViteClient ? '/api' : 'http://localhost:8000/api'
  })()
  const wsBase = httpBase.replace(/^http/, 'ws')

  const applyVersion = (version?: string) => {
    if (!version || disposed) return
    const isFirst = lastVersion.value === ''
    if (version === lastVersion.value) return
    lastVersion.value = version
    lastSyncAt.value = new Date().toLocaleTimeString('zh-CN', { hour12: false })
    // 首次拿到版本只做基线记录，不触发额外刷新
    if (!isFirst) onChange('data-change')
  }

  // 重连成功后立即全量拉取，补齐断开期间的所有变更
  const fullRefresh = (reason: string) => {
    if (!disposed) onChange(reason)
  }

  const wsAlive = () => !!ws && ws.readyState === WebSocket.OPEN

  const stopPing = () => {
    if (pingTimer) { window.clearInterval(pingTimer); pingTimer = null }
  }

  const closeSse = () => {
    if (source) { try { source.close() } catch { /* ignore */ } source = null }
  }

  const startSse = () => {
    if (disposed || source) return
    try {
      source = new EventSource(`${httpBase}/realtime/stream/`)
      source.onopen = () => {
        if (!wsAlive()) { connected.value = true; channel.value = 'sse' }
      }
      const onEvent = (event: MessageEvent) => {
        try { applyVersion(JSON.parse(event.data)?.version) } catch { /* ignore */ }
      }
      source.addEventListener('ready', onEvent)
      source.addEventListener('data-change', onEvent)
      source.onerror = () => {
        closeSse()
        if (!wsAlive()) { connected.value = false; channel.value = 'poll' }
      }
    } catch {
      // 浏览器不支持 SSE 时完全依赖轮询兜底
    }
  }

  const scheduleReconnect = () => {
    if (disposed || reconnectTimer) return
    retryCount += 1
    // 指数退避：1s → 2s → 4s … 封顶 15s
    const delay = Math.min(1000 * 2 ** (retryCount - 1), 15000)
    reconnectTimer = window.setTimeout(() => {
      reconnectTimer = null
      connectWs()
    }, delay)
  }

  const connectWs = () => {
    if (disposed) return
    try {
      ws = new WebSocket(`${wsBase}/realtime/ws/`)
    } catch {
      startSse()
      scheduleReconnect()
      return
    }
    ws.onopen = () => {
      const isReconnect = everConnected || retryCount > 0
      everConnected = true
      retryCount = 0
      connected.value = true
      channel.value = 'websocket'
      // WS 为主通道，建立后关闭 SSE 降级通道
      closeSse()
      stopPing()
      pingTimer = window.setInterval(() => {
        try { ws?.send('ping') } catch { /* ignore */ }
      }, 15000)
      // 重连成功：立即全量拉取补全断开期间的数据
      if (isReconnect) fullRefresh('reconnect')
    }
    ws.onmessage = (event: MessageEvent) => {
      try {
        const msg = JSON.parse(event.data)
        if (msg?.version) applyVersion(msg.version)
      } catch { /* ignore */ }
    }
    ws.onerror = () => {
      try { ws?.close() } catch { /* ignore */ }
    }
    ws.onclose = () => {
      stopPing()
      ws = null
      connected.value = false
      channel.value = source ? 'sse' : 'poll'
      // 降级到 SSE，并安排 WS 重连
      startSse()
      scheduleReconnect()
    }
  }

  const poll = async () => {
    if (disposed || document.hidden) return
    try {
      const res = await fetch(`${httpBase}/realtime/version/`, { cache: 'no-store' })
      const data = await res.json()
      applyVersion(data?.version)
      // 轮询可达但长连接未建立时，尝试恢复 WS
      if (!wsAlive() && !source && !reconnectTimer) scheduleReconnect()
    } catch {
      // 网络抖动时忽略，下一轮轮询会自动重试
    }
  }

  const onVisible = () => {
    if (document.hidden) return
    poll()
    if (!wsAlive() && !source) connectWs()
  }

  onMounted(() => {
    connectWs()
    poll()
    pollTimer = window.setInterval(poll, options.pollInterval ?? 800)
    document.addEventListener('visibilitychange', onVisible)
  })

  onBeforeUnmount(() => {
    disposed = true
    stopPing()
    if (ws) { try { ws.close() } catch { /* ignore */ } ws = null }
    closeSse()
    if (pollTimer) window.clearInterval(pollTimer)
    if (reconnectTimer) window.clearTimeout(reconnectTimer)
    document.removeEventListener('visibilitychange', onVisible)
  })

  return { connected, channel, lastVersion, lastSyncAt }
}
