/**
 * TypeScript Type Definitions — Proxy-Direct Dashboard
 *
 * Types for the consulting dashboard running against the customer gateway proxy.
 * Agents are tracked in the proxy's in-memory registry (not a database).
 */

// ═══════════════════════════════════════════════════════════
// AGENT TYPES
// ═══════════════════════════════════════════════════════════

export type AgentStatus = 'idle' | 'executing' | 'waiting' | 'blocked' | 'complete'

// Agent as tracked by the proxy's in-memory registry
export interface Agent {
  id: string
  name: string
  model: string
  status: AgentStatus | null
  inputTokens: number
  outputTokens: number
  totalCost: number
  task?: string
  createdAt: number | string
  // Compatibility fields used by components
  input_tokens: number
  output_tokens: number
  total_cost: number
  archived: boolean
  system_prompt: string | null
  working_dir: string | null
  git_worktree: string | null
  session_id: string | null
  adw_id: string | null
  adw_step: string | null
  metadata: Record<string, any>
  log_count?: number
  latest_summary?: string
  created_at: string
  updated_at: string
}

// Orchestrator totals (from proxy's orchestrator_updated events)
export interface OrchestratorTotals {
  total_cost: number
  input_tokens: number
  output_tokens: number
  agent_count: number
  active_count: number
}

// ═══════════════════════════════════════════════════════════
// EVENT STREAM TYPES
// ═══════════════════════════════════════════════════════════

export type EventCategory = 'hook' | 'response'
export type LogLevel = 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR'
export type EventStreamFilter = 'all' | 'errors' | 'hooks' | 'responses'
export type EventSourceType = 'agent_log' | 'system_log' | 'orchestrator_chat' | 'thinking_block' | 'tool_use_block'

export interface EventStreamEntry {
  id: string
  lineNumber: number
  sourceType?: EventSourceType
  level: LogLevel | 'SUCCESS'
  agentId?: string
  agentName?: string
  content: string
  tokens?: number
  timestamp: Date | string
  eventType?: string
  eventCategory?: EventCategory
  metadata?: Record<string, any>
}

// ═══════════════════════════════════════════════════════════
// CHAT TYPES
// ═══════════════════════════════════════════════════════════

export type ChatMessageType = 'text' | 'thinking' | 'tool_use'

export interface BaseChatMessage {
  id: string
  sender: 'user' | 'orchestrator'
  timestamp: string
  type: ChatMessageType
}

export interface TextChatMessage extends BaseChatMessage {
  type: 'text'
  content: string
}

export interface ThinkingChatMessage extends BaseChatMessage {
  type: 'thinking'
  thinking: string
}

export interface ToolUseChatMessage extends BaseChatMessage {
  type: 'tool_use'
  toolName: string
  toolInput: Record<string, any> | null
}

export type ChatMessage = TextChatMessage | ThinkingChatMessage | ToolUseChatMessage

// ═══════════════════════════════════════════════════════════
// UI TYPES
// ═══════════════════════════════════════════════════════════

export interface AppStats {
  active: number
  running: number
  logs: number
  cost: number
}

// Session from proxy's session_list response
export interface Session {
  id: string
  title: string
  status: 'active' | 'idle'
  createdAt?: string
  updatedAt?: string
}

// Agent log data shape (from proxy agent_log events)
export interface AgentLog {
  id: string
  agent_id: string
  agent_name?: string
  event_category: EventCategory
  event_type: string
  content: string | null
  payload: Record<string, any>
  summary: string | null
  timestamp: string
  session_id?: string | null
  task_slug?: string | null
  entry_index?: number | null
}

// System log
export interface SystemLog {
  id: string
  agent_id: string | null
  file_path: string | null
  adw_id: string | null
  level: LogLevel
  message: string
  metadata: Record<string, any>
  timestamp: string
}

// Orchestrator chat message
export interface OrchestratorChat {
  id: string
  created_at: string
  updated_at: string
  orchestrator_agent_id: string
  sender_type: 'user' | 'orchestrator' | 'agent'
  receiver_type: 'user' | 'orchestrator' | 'agent'
  message: string
  agent_id: string | null
  metadata: Record<string, any>
}

// Extended agent
export interface AgentWithStats extends Agent {
  logCount?: number
  isActive?: boolean
}

// Agent metadata
export interface AgentMetadata {
  template_name?: string
  template_color?: string
  [key: string]: any
}

// File tracking types
export interface FileChange {
  path: string
  absolute_path: string
  status: 'created' | 'modified' | 'deleted'
  lines_added: number
  lines_removed: number
  diff?: string
  summary?: string
  agent_id?: string
  agent_name?: string
}

export interface FileRead {
  path: string
  absolute_path: string
  line_count: number
  agent_id?: string
  agent_name?: string
}

export interface AgentLogMetadata {
  file_changes?: FileChange[]
  read_files?: FileRead[]
  total_files_modified?: number
  total_files_read?: number
  generated_at?: string
}

// OrchestratorAgent — kept for component compatibility
export interface OrchestratorAgent {
  id: string
  session_id: string | null
  system_prompt: string | null
  status: AgentStatus | null
  working_dir: string | null
  input_tokens: number
  output_tokens: number
  total_cost: number
  archived: boolean
  metadata: Record<string, any>
  created_at: string
  updated_at: string
}

// Component props
export interface AgentLogRowProps {
  event: AgentLog
  lineNumber: number
}

export interface SystemLogRowProps {
  event: SystemLog
  lineNumber: number
}

export interface OrchestratorChatRowProps {
  event: OrchestratorChat
  lineNumber: number
}
