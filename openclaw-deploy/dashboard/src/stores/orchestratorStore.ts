/**
 * Orchestrator Store — Proxy-Direct Mode
 *
 * Pinia store adapted for the customer gateway proxy.
 * No REST backend. All data comes via WebSocket from the proxy.
 * Agents are tracked in the proxy's in-memory registry.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  Agent,
  OrchestratorAgent,
  OrchestratorTotals,
  EventStreamEntry,
  EventCategory,
  LogLevel,
  ChatMessage,
  AppStats,
  EventStreamFilter
} from '../types'
import * as chatService from '../services/chatService'
import { WS_URL, AUTH_TOKEN } from '../config/constants'
import { useAgentPulse } from '../composables/useAgentPulse'

// Initialize pulse composable at module level
const agentPulse = useAgentPulse()

export const useOrchestratorStore = defineStore('orchestrator', () => {
  // ═══════════════════════════════════════════════════════════
  // STATE
  // ═══════════════════════════════════════════════════════════

  // Agents (populated from proxy's agent_created/agent_updated events)
  const agents = ref<Agent[]>([])
  const selectedAgentId = ref<string | null>(null)

  // Orchestrator totals (from proxy's orchestrator_updated events)
  const orchestratorAgent = ref<OrchestratorAgent | null>(null)
  const orchestratorTotals = ref<OrchestratorTotals>({
    total_cost: 0,
    input_tokens: 0,
    output_tokens: 0,
    agent_count: 0,
    active_count: 0
  })

  // Event Stream
  const eventStreamEntries = ref<EventStreamEntry[]>([])
  const eventStreamFilter = ref<EventStreamFilter>('all')
  const autoScroll = ref<boolean>(true)

  // File Tracking
  const fileTrackingEvents = ref<Map<string, any>>(new Map())

  // Chat
  const chatMessages = ref<ChatMessage[]>([])
  const isTyping = ref(false)

  // Command Input
  const commandInputVisible = ref<boolean>(false)

  // Chat Width
  const chatWidth = ref<'sm' | 'md' | 'lg'>('sm')

  // WebSocket
  const isConnected = ref(false)
  let wsConnection: WebSocket | null = null

  // Customer ID (from proxy connection_established)
  const customerId = ref<string | null>(null)

  // ═══════════════════════════════════════════════════════════
  // GETTERS
  // ═══════════════════════════════════════════════════════════

  const activeAgents = computed(() =>
    agents.value.filter(a => a.status !== 'complete')
  )

  const runningAgents = computed(() =>
    agents.value.filter(a => a.status === 'executing')
  )

  const idleAgents = computed(() =>
    agents.value.filter(a => a.status === 'idle')
  )

  const selectedAgent = computed(() =>
    selectedAgentId.value
      ? agents.value.find(a => a.id === selectedAgentId.value)
      : null
  )

  const filteredEventStream = computed(() => {
    switch (eventStreamFilter.value) {
      case 'errors':
        return eventStreamEntries.value.filter(e => e.level === 'ERROR')
      case 'hooks':
        return eventStreamEntries.value.filter(e => e.eventCategory === 'hook')
      case 'responses':
        return eventStreamEntries.value.filter(e => e.eventCategory === 'response')
      default:
        return eventStreamEntries.value
    }
  })

  const stats = computed<AppStats>(() => ({
    active: activeAgents.value.length,
    running: runningAgents.value.length,
    logs: eventStreamEntries.value.length,
    cost: orchestratorTotals.value.total_cost
  }))

  const chatWidthPixels = computed(() => {
    const widths = { sm: 418, md: 518, lg: 618 }
    return widths[chatWidth.value]
  })

  // ═══════════════════════════════════════════════════════════
  // ACTIONS - CHAT
  // ═══════════════════════════════════════════════════════════

  function addChatMessage(message: ChatMessage) {
    chatMessages.value = [...chatMessages.value, message]
  }

  function sendUserMessage(content: string) {
    // Add user message immediately to UI
    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      sender: 'user',
      type: 'text',
      content,
      timestamp: new Date().toISOString()
    }
    addChatMessage(userMessage)

    // Send via WebSocket to proxy
    if (wsConnection) {
      try {
        chatService.sendMessage(wsConnection, content)
        console.log('[Store] Message sent via WebSocket')
      } catch (error) {
        console.error('[Store] Failed to send message:', error)
        const errorMessage: ChatMessage = {
          id: crypto.randomUUID(),
          sender: 'orchestrator',
          type: 'text',
          content: `Error: ${error instanceof Error ? error.message : 'Failed to send message'}`,
          timestamp: new Date().toISOString()
        }
        addChatMessage(errorMessage)
      }
    } else {
      console.error('[Store] WebSocket not connected')
    }
  }

  function clearChat() {
    chatMessages.value = []
  }

  function toggleChatWidth() {
    const sizes = ['sm', 'md', 'lg'] as const
    const currentIndex = sizes.indexOf(chatWidth.value)
    const nextIndex = (currentIndex + 1) % sizes.length
    chatWidth.value = sizes[nextIndex]
    try {
      localStorage.setItem('dashboard_chat_width', chatWidth.value)
    } catch { /* ignore */ }
  }

  function initializeChatWidth() {
    try {
      const saved = localStorage.getItem('dashboard_chat_width')
      if (saved && ['sm', 'md', 'lg'].includes(saved)) {
        chatWidth.value = saved as 'sm' | 'md' | 'lg'
      }
    } catch { /* ignore */ }
  }

  // ═══════════════════════════════════════════════════════════
  // ACTIONS - WEBSOCKET
  // ═══════════════════════════════════════════════════════════

  function connectWebSocket() {
    if (wsConnection) {
      if (wsConnection.readyState === WebSocket.OPEN) {
        console.log('[Store] WebSocket already connected')
        return
      }
      wsConnection.close()
      wsConnection = null
    }

    // Build WebSocket URL with token auth
    const token = AUTH_TOKEN
    if (!token) {
      console.error('[Store] No auth token. Pass ?token=xxx in URL or set VITE_AUTH_TOKEN.')
      return
    }

    const wsUrl = `${WS_URL}?token=${token}`
    console.log('[Store] Connecting to proxy WebSocket:', WS_URL)

    try {
      wsConnection = chatService.connectWebSocket(wsUrl, {
        onChatStream: handleChatStream,
        onTyping: handleTyping,

        onAgentLog: (message) => {
          // Proxy sends: { type: 'agent_log', data: { message, level, agentId, agentName } }
          if (message.data) {
            addAgentLogFromProxy(message.data)
          }
        },

        onOrchestratorChat: (message) => {
          // Proxy sends: { type: 'orchestrator_chat', data: { sender, content, timestamp, agentId, agentName } }
          if (message.data) {
            addOrchestratorChatFromProxy(message.data)
          }
        },

        onThinkingBlock: (message) => {
          // Proxy sends: { type: 'thinking_block', data: { id, thinking, timestamp, agentId, agentName } }
          if (message.data) {
            addThinkingBlockEvent(message.data)
            addThinkingToChatMessage(message.data)
          }
        },

        onToolUseBlock: (message) => {
          // Proxy sends: { type: 'tool_use_block', data: { id, tool_name, tool_input, timestamp, agentId, agentName } }
          if (message.data) {
            addToolUseBlockEvent(message.data)
            addToolUseToChatMessage(message.data)
          }
        },

        onAgentCreated: (message) => {
          // Proxy sends: { type: 'agent_created', agent: { id, name, status, model, ... } }
          if (message.agent) {
            handleAgentCreated(message.agent)
          }
        },

        onAgentUpdated: (message) => {
          // Proxy sends: { type: 'agent_updated', agent: { id, name, status, ... } }
          if (message.agent) {
            handleAgentUpdated(message.agent)
          }
        },

        onAgentDeleted: (message) => {
          handleAgentDeleted(message)
        },

        onOrchestratorUpdated: (message) => {
          // Proxy sends: { type: 'orchestrator_updated', orchestrator: { total_cost, input_tokens, ... } }
          if (message.orchestrator) {
            handleOrchestratorUpdated(message.orchestrator)
          }
        },

        onSessionList: (message) => {
          console.log('[Store] Session list received:', message.sessions?.length || 0)
        },

        onSessionStarted: (message) => {
          console.log('[Store] Session started:', message.sessionId)
        },

        onError: handleWebSocketError,

        onConnected: (message) => {
          isConnected.value = true
          customerId.value = message?.customerId || null
          console.log('[Store] Connected to proxy, customerId:', customerId.value)
        },

        onDisconnected: () => {
          isConnected.value = false
          console.log('[Store] Disconnected from proxy')
        }
      })
    } catch (error) {
      console.error('[Store] Failed to connect WebSocket:', error)
    }
  }

  function disconnectWebSocket() {
    if (wsConnection) {
      chatService.disconnect(wsConnection)
      wsConnection = null
      isConnected.value = false
    }
    agentPulse.clearAllPulses()
  }

  function handleChatStream(chunk: string, isComplete: boolean) {
    if (!isComplete) {
      isTyping.value = true
    } else {
      isTyping.value = false
    }
  }

  function handleTyping(typing: boolean) {
    isTyping.value = typing
  }

  function handleWebSocketError(error: any) {
    console.error('[Store] WebSocket error:', error)
    isTyping.value = false
  }

  // ═══════════════════════════════════════════════════════════
  // AGENT HANDLERS (from proxy events)
  // ═══════════════════════════════════════════════════════════

  function handleAgentCreated(agent: any) {
    // Normalize proxy agent format to frontend Agent type
    const frontendAgent: Agent = {
      id: agent.id,
      name: agent.name || `Agent-${agents.value.length + 1}`,
      model: agent.model || 'unknown',
      status: agent.status || 'idle',
      inputTokens: agent.inputTokens || 0,
      outputTokens: agent.outputTokens || 0,
      totalCost: agent.totalCost || 0,
      input_tokens: agent.inputTokens || 0,
      output_tokens: agent.outputTokens || 0,
      total_cost: agent.totalCost || 0,
      task: agent.task || '',
      createdAt: agent.createdAt || Date.now(),
      archived: false,
      system_prompt: null,
      working_dir: null,
      git_worktree: null,
      session_id: null,
      adw_id: null,
      adw_step: null,
      metadata: {},
      created_at: new Date(agent.createdAt || Date.now()).toISOString(),
      updated_at: new Date().toISOString()
    }

    // Check if agent already exists (avoid duplicates)
    const existing = agents.value.findIndex(a => a.id === agent.id)
    if (existing !== -1) {
      agents.value[existing] = { ...agents.value[existing], ...frontendAgent }
    } else {
      agents.value = [...agents.value, frontendAgent]
    }
    console.log(`[Store] Agent created: ${agent.id} (${agent.name})`)
  }

  function handleAgentUpdated(agent: any) {
    const index = agents.value.findIndex(a => a.id === agent.id)
    if (index !== -1) {
      agents.value[index] = {
        ...agents.value[index],
        status: agent.status ?? agents.value[index].status,
        inputTokens: agent.inputTokens ?? agents.value[index].inputTokens,
        outputTokens: agent.outputTokens ?? agents.value[index].outputTokens,
        totalCost: agent.totalCost ?? agents.value[index].totalCost,
        input_tokens: agent.inputTokens ?? agents.value[index].input_tokens,
        output_tokens: agent.outputTokens ?? agents.value[index].output_tokens,
        total_cost: agent.totalCost ?? agents.value[index].total_cost,
        updated_at: new Date().toISOString()
      }
    }
  }

  function handleAgentDeleted(message: any) {
    const agentId = message.agent_id || message.agentId
    if (agentId) {
      agents.value = agents.value.filter(a => a.id !== agentId)
    }
  }

  function handleOrchestratorUpdated(data: OrchestratorTotals) {
    orchestratorTotals.value = {
      total_cost: data.total_cost ?? orchestratorTotals.value.total_cost,
      input_tokens: data.input_tokens ?? orchestratorTotals.value.input_tokens,
      output_tokens: data.output_tokens ?? orchestratorTotals.value.output_tokens,
      agent_count: data.agent_count ?? orchestratorTotals.value.agent_count,
      active_count: data.active_count ?? orchestratorTotals.value.active_count
    }

    // Update the orchestratorAgent ref for component compatibility
    if (orchestratorAgent.value) {
      orchestratorAgent.value = {
        ...orchestratorAgent.value,
        input_tokens: orchestratorTotals.value.input_tokens,
        output_tokens: orchestratorTotals.value.output_tokens,
        total_cost: orchestratorTotals.value.total_cost,
        updated_at: new Date().toISOString()
      }
    }
  }

  // ═══════════════════════════════════════════════════════════
  // AGENTS
  // ═══════════════════════════════════════════════════════════

  function selectAgent(id: string) {
    selectedAgentId.value = id
  }

  function clearAgentSelection() {
    selectedAgentId.value = null
  }

  function addAgent(agent: Agent) {
    agents.value = [...agents.value, agent]
  }

  function updateAgent(id: string, updates: Partial<Agent>) {
    const index = agents.value.findIndex(a => a.id === id)
    if (index !== -1) {
      agents.value[index] = { ...agents.value[index], ...updates }
    }
  }

  function removeAgent(id: string) {
    agents.value = agents.value.filter(a => a.id !== id)
  }

  // ═══════════════════════════════════════════════════════════
  // EVENT STREAM
  // ═══════════════════════════════════════════════════════════

  function addEventStreamEntry(entry: EventStreamEntry) {
    eventStreamEntries.value = [...eventStreamEntries.value, entry]
  }

  function clearEventStream() {
    eventStreamEntries.value = []
  }

  function setEventStreamFilter(filter: EventStreamFilter) {
    eventStreamFilter.value = filter
  }

  function toggleAutoScroll() {
    autoScroll.value = !autoScroll.value
  }

  function toggleCommandInput() {
    commandInputVisible.value = !commandInputVisible.value
  }

  function showCommandInput() {
    commandInputVisible.value = true
  }

  function hideCommandInput() {
    commandInputVisible.value = false
  }

  function exportEventStream() {
    const data = JSON.stringify(filteredEventStream.value, null, 2)
    const blob = new Blob([data], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `event-stream-${new Date().toISOString()}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  // ═══════════════════════════════════════════════════════════
  // EVENT HANDLERS (from proxy WebSocket)
  // ═══════════════════════════════════════════════════════════

  /**
   * Handle agent_log events from proxy
   * Proxy format: { message, level, agentId, agentName }
   */
  function addAgentLogFromProxy(data: any) {
    const agentId = data.agentId || data.agent_id
    const agentName = data.agentName || data.agent_name || agentId

    // Trigger pulse
    if (agentId) {
      agentPulse.triggerPulse(agentId)
    }

    const entry: EventStreamEntry = {
      id: crypto.randomUUID(),
      lineNumber: eventStreamEntries.value.length + 1,
      sourceType: 'agent_log',
      level: mapLevel(data.level),
      agentId,
      agentName,
      content: data.message || 'Agent event',
      timestamp: new Date(),
      eventType: data.eventType || data.event_type,
      eventCategory: data.eventCategory || data.event_category
    }

    eventStreamEntries.value = [...eventStreamEntries.value, entry]
  }

  // Kept for API compatibility
  function addAgentLogEvent(log: any) {
    addAgentLogFromProxy(log)
  }

  /**
   * Handle orchestrator_chat events from proxy
   * Proxy format: { sender, content, timestamp, agentId, agentName }
   */
  function addOrchestratorChatFromProxy(data: any) {
    const content = data.content || data.message || ''

    // Add to event stream
    const entry: EventStreamEntry = {
      id: crypto.randomUUID(),
      lineNumber: eventStreamEntries.value.length + 1,
      sourceType: 'orchestrator_chat',
      level: 'INFO',
      content,
      timestamp: new Date(data.timestamp || Date.now()),
      metadata: {
        sender: data.sender,
        agentId: data.agentId,
        agentName: data.agentName
      }
    }
    eventStreamEntries.value = [...eventStreamEntries.value, entry]

    // Add to chat messages
    const chatMessage: ChatMessage = {
      id: crypto.randomUUID(),
      sender: 'orchestrator',
      type: 'text',
      content,
      timestamp: new Date(data.timestamp || Date.now()).toISOString()
    }
    chatMessages.value = [...chatMessages.value, chatMessage]
  }

  // Kept for API compatibility
  function addOrchestratorChatEvent(chat: any) {
    addOrchestratorChatFromProxy(chat)
  }

  /**
   * Add thinking block event
   */
  function addThinkingBlockEvent(data: any) {
    if (data.agentId) {
      agentPulse.triggerPulse(data.agentId)
    }

    const thinking = data.thinking || ''
    const entry: EventStreamEntry = {
      id: data.id || crypto.randomUUID(),
      lineNumber: eventStreamEntries.value.length + 1,
      sourceType: 'thinking_block',
      level: 'INFO',
      content: `Thinking: ${thinking.slice(0, 100)}${thinking.length > 100 ? '...' : ''}`,
      timestamp: data.timestamp ? new Date(data.timestamp) : new Date(),
      agentId: data.agentId,
      agentName: data.agentName,
      metadata: { data }
    }

    eventStreamEntries.value = [...eventStreamEntries.value, entry]
  }

  /**
   * Add tool use block event
   */
  function addToolUseBlockEvent(data: any) {
    if (data.agentId) {
      agentPulse.triggerPulse(data.agentId)
    }

    const entry: EventStreamEntry = {
      id: data.id || crypto.randomUUID(),
      lineNumber: eventStreamEntries.value.length + 1,
      sourceType: 'tool_use_block',
      level: 'INFO',
      content: `Tool: ${data.tool_name || 'unknown'}`,
      timestamp: data.timestamp ? new Date(data.timestamp) : new Date(),
      agentId: data.agentId,
      agentName: data.agentName,
      metadata: { data }
    }

    eventStreamEntries.value = [...eventStreamEntries.value, entry]
  }

  function addThinkingToChatMessage(data: any) {
    const thinkingMessage: ChatMessage = {
      id: data.id || crypto.randomUUID(),
      sender: 'orchestrator',
      type: 'thinking',
      thinking: data.thinking || '',
      timestamp: data.timestamp || new Date().toISOString()
    }
    chatMessages.value = [...chatMessages.value, thinkingMessage]
  }

  function addToolUseToChatMessage(data: any) {
    const toolUseMessage: ChatMessage = {
      id: data.id || crypto.randomUUID(),
      sender: 'orchestrator',
      type: 'tool_use',
      toolName: data.tool_name || 'unknown',
      toolInput: data.tool_input || null,
      timestamp: data.timestamp || new Date().toISOString()
    }
    chatMessages.value = [...chatMessages.value, toolUseMessage]
  }

  // ═══════════════════════════════════════════════════════════
  // HELPERS
  // ═══════════════════════════════════════════════════════════

  function mapLevel(level: string | undefined): LogLevel | 'SUCCESS' {
    if (!level) return 'INFO'
    const l = level.toUpperCase()
    if (l === 'ERROR') return 'ERROR'
    if (l === 'WARNING' || l === 'WARN') return 'WARNING'
    if (l === 'SUCCESS') return 'SUCCESS'
    if (l === 'DEBUG') return 'DEBUG'
    return 'INFO'
  }

  function mapEventCategoryToLevel(category: EventCategory | undefined, eventType: string): LogLevel | 'SUCCESS' {
    if (!eventType) return 'INFO'
    if (eventType.toLowerCase().includes('error')) return 'ERROR'
    if (eventType.toLowerCase().includes('warn')) return 'WARNING'
    if (eventType.toLowerCase().includes('success')) return 'SUCCESS'
    if (eventType.toLowerCase().includes('debug')) return 'DEBUG'
    return 'INFO'
  }

  // ═══════════════════════════════════════════════════════════
  // INITIALIZATION
  // ═══════════════════════════════════════════════════════════

  function initialize() {
    console.log('[Store] Initializing dashboard store (proxy-direct mode)...')

    // Initialize chat width from localStorage
    initializeChatWidth()

    // Initialize a placeholder orchestrator agent for component compatibility
    orchestratorAgent.value = {
      id: 'proxy-orchestrator',
      session_id: null,
      system_prompt: null,
      status: null,
      working_dir: null,
      input_tokens: 0,
      output_tokens: 0,
      total_cost: 0,
      archived: false,
      metadata: {},
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }

    // Connect to proxy WebSocket — everything else comes via events
    connectWebSocket()

    console.log('[Store] Dashboard store initialized')
  }

  // ═══════════════════════════════════════════════════════════
  // RETURN PUBLIC API
  // ═══════════════════════════════════════════════════════════

  return {
    // State
    agents,
    selectedAgentId,
    orchestratorAgent,
    orchestratorTotals,
    eventStreamEntries,
    eventStreamFilter,
    autoScroll,
    fileTrackingEvents,
    chatMessages,
    chatWidth,
    isTyping,
    isConnected,
    commandInputVisible,
    customerId,

    // Getters
    activeAgents,
    runningAgents,
    idleAgents,
    selectedAgent,
    filteredEventStream,
    stats,
    chatWidthPixels,

    // Actions
    selectAgent,
    clearAgentSelection,
    addAgent,
    updateAgent,
    removeAgent,
    addEventStreamEntry,
    clearEventStream,
    setEventStreamFilter,
    toggleAutoScroll,
    toggleCommandInput,
    showCommandInput,
    hideCommandInput,
    exportEventStream,
    addChatMessage,
    sendUserMessage,
    clearChat,
    toggleChatWidth,
    initializeChatWidth,
    connectWebSocket,
    disconnectWebSocket,
    initialize,

    // Event stream actions
    addAgentLogEvent,
    addOrchestratorChatEvent,

    // Agent pulse actions
    triggerAgentPulse: agentPulse.triggerPulse,
    isAgentPulsing: agentPulse.isAgentPulsing,
    getAgentPulseClass: agentPulse.getAgentPulseClass,
    getPulsingAgents: agentPulse.getPulsingAgents,
    isPulsing: agentPulse.isPulsing
  }
})
