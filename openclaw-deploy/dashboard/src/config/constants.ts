/**
 * Application Constants
 *
 * Configuration for the consulting dashboard running in proxy-direct mode.
 * The dashboard connects directly to the customer gateway proxy via WebSocket.
 */

// WebSocket URL — defaults to same origin (proxy serves both static files and WS)
export const WS_URL = import.meta.env.VITE_WS_URL || `ws://${location.host}`

// Auth token — passed as query param on WebSocket connection
export const AUTH_TOKEN = import.meta.env.VITE_AUTH_TOKEN || new URLSearchParams(location.search).get('token') || ''

// Event stream limits
export const DEFAULT_EVENT_HISTORY_LIMIT = 300
export const DEFAULT_CHAT_HISTORY_LIMIT = 300
