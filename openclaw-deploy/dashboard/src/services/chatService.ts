/**
 * Chat Service — Proxy-Direct Mode
 *
 * All communication goes through WebSocket to the customer gateway proxy.
 * No REST backend needed. The proxy handles:
 *   - Gateway protocol handshake (connect.challenge -> connect -> hello-ok)
 *   - Translates frontend messages into gateway req frames
 *   - Translates gateway events back into frontend-friendly messages
 */

/**
 * WebSocket connection callbacks
 * These match the event types emitted by the customer gateway proxy
 */
export interface WebSocketCallbacks {
  onChatStream: (chunk: string, isComplete: boolean) => void
  onTyping: (isTyping: boolean) => void
  onAgentLog?: (message: any) => void
  onOrchestratorChat?: (message: any) => void
  onThinkingBlock?: (message: any) => void
  onToolUseBlock?: (message: any) => void
  onAgentCreated?: (message: any) => void
  onAgentUpdated?: (message: any) => void
  onAgentDeleted?: (message: any) => void
  onOrchestratorUpdated?: (message: any) => void
  onSessionList?: (message: any) => void
  onSessionStarted?: (message: any) => void
  onError: (error: any) => void
  onConnected?: (message: any) => void
  onDisconnected?: () => void
}

/**
 * Connect to the customer gateway proxy via WebSocket
 */
export function connectWebSocket(
  url: string,
  callbacks: WebSocketCallbacks
): WebSocket {
  const ws = new WebSocket(url)

  ws.onopen = () => {
    console.log('[ChatService] WebSocket connected to proxy')
  }

  ws.onmessage = (event) => {
    try {
      const message = JSON.parse(event.data)

      switch (message.type) {
        // --- Streaming & Typing ---
        case 'chat_stream':
          callbacks.onChatStream(
            message.chunk || '',
            message.is_complete || false
          )
          break

        case 'chat_typing':
          callbacks.onTyping(message.isTyping || false)
          break

        // --- Agent Events (from Pi runtime via proxy) ---
        case 'agent_log':
          callbacks.onAgentLog?.(message)
          break

        case 'orchestrator_chat':
          callbacks.onOrchestratorChat?.(message)
          break

        case 'thinking_block':
          callbacks.onThinkingBlock?.(message)
          break

        case 'tool_use_block':
          callbacks.onToolUseBlock?.(message)
          break

        case 'agent_created':
          callbacks.onAgentCreated?.(message)
          break

        case 'agent_updated':
          callbacks.onAgentUpdated?.(message)
          break

        case 'agent_deleted':
          callbacks.onAgentDeleted?.(message)
          break

        case 'orchestrator_updated':
          callbacks.onOrchestratorUpdated?.(message)
          break

        // --- Session Management ---
        case 'session_list':
          callbacks.onSessionList?.(message)
          break

        case 'session_started':
          callbacks.onSessionStarted?.(message)
          break

        // --- Connection ---
        case 'connection_established':
          console.log('[ChatService] Proxy connection established:', message.customerId)
          callbacks.onConnected?.(message)
          break

        case 'error':
          console.error('[ChatService] Proxy error:', message.message)
          callbacks.onError(message)
          break

        default:
          console.log('[ChatService] Unknown message type:', message.type)
      }
    } catch (error) {
      console.error('[ChatService] Failed to parse WebSocket message:', error)
    }
  }

  ws.onerror = (error) => {
    console.error('[ChatService] WebSocket error:', error)
    callbacks.onError(error)
  }

  ws.onclose = () => {
    console.log('[ChatService] WebSocket disconnected')
    callbacks.onDisconnected?.()
  }

  return ws
}

/**
 * Send a user message via WebSocket
 * The proxy translates this to a gateway chat.send RPC call
 */
export function sendMessage(ws: WebSocket, content: string): void {
  if (ws.readyState !== WebSocket.OPEN) {
    throw new Error('WebSocket not connected')
  }
  ws.send(JSON.stringify({ type: 'user_message', content }))
}

/**
 * Start a new session via WebSocket
 */
export function startSession(ws: WebSocket, skill?: string, initialMessage?: string): void {
  if (ws.readyState !== WebSocket.OPEN) {
    throw new Error('WebSocket not connected')
  }
  ws.send(JSON.stringify({
    type: 'start_session',
    skill: skill || 'Planning Session',
    sessionType: 'planning',
    initialMessage
  }))
}

/**
 * Load an existing session via WebSocket
 */
export function loadSession(ws: WebSocket, sessionId: string): void {
  if (ws.readyState !== WebSocket.OPEN) {
    throw new Error('WebSocket not connected')
  }
  ws.send(JSON.stringify({ type: 'load_session', sessionId }))
}

/**
 * List sessions via WebSocket
 */
export function listSessions(ws: WebSocket): void {
  if (ws.readyState !== WebSocket.OPEN) {
    throw new Error('WebSocket not connected')
  }
  ws.send(JSON.stringify({ type: 'list_sessions' }))
}

/**
 * Disconnect WebSocket
 */
export function disconnect(ws: WebSocket): void {
  if (ws.readyState === WebSocket.OPEN) {
    ws.close()
  }
}
