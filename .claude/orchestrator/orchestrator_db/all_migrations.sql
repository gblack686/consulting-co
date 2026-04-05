-- ============================================================================
-- ORCHESTRATOR_AGENTS TABLE
-- ============================================================================
-- The orchestrator agent that manages other agents
--
-- Dependencies: None
-- Constraints:
--   - session_id must be unique (prevents duplicate sessions)

-- Create table with UNIQUE constraint on session_id (idempotent)
CREATE TABLE IF NOT EXISTS orchestrator_agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id TEXT UNIQUE,  -- UNIQUE constraint prevents duplicate session IDs
    system_prompt TEXT,
    status TEXT CHECK (status IN ('idle', 'executing', 'waiting', 'blocked', 'complete')),
    working_dir TEXT,
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    total_cost DECIMAL(10,4) DEFAULT 0.0000,
    archived BOOLEAN DEFAULT false,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Table and column comments
COMMENT ON TABLE orchestrator_agents IS 'Orchestrator agents that manage other agents';
COMMENT ON COLUMN orchestrator_agents.id IS 'Unique orchestrator identifier';
COMMENT ON COLUMN orchestrator_agents.session_id IS 'Unique Claude SDK session ID (NULL until first interaction)';
COMMENT ON COLUMN orchestrator_agents.system_prompt IS 'Orchestrator system prompt';
COMMENT ON COLUMN orchestrator_agents.status IS 'Current status: idle, executing, waiting, blocked, complete';
COMMENT ON COLUMN orchestrator_agents.working_dir IS 'Orchestrator working directory';
COMMENT ON COLUMN orchestrator_agents.input_tokens IS 'Cumulative input tokens consumed';
COMMENT ON COLUMN orchestrator_agents.output_tokens IS 'Cumulative output tokens generated';
COMMENT ON COLUMN orchestrator_agents.total_cost IS 'Cumulative cost in USD';
COMMENT ON COLUMN orchestrator_agents.archived IS 'Soft delete flag';
COMMENT ON COLUMN orchestrator_agents.metadata IS 'Orchestrator configuration (JSONB)';
-- ============================================================================
-- AGENTS TABLE
-- ============================================================================
-- Agent registry and configuration for managed agents
--
-- Dependencies: None
-- Note: Each agent has a unique name and tracks its own usage/costs

CREATE TABLE IF NOT EXISTS agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    orchestrator_agent_id UUID NOT NULL REFERENCES orchestrator_agents(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    model TEXT NOT NULL,
    system_prompt TEXT,
    working_dir TEXT,
    git_worktree TEXT,
    status TEXT CHECK (status IN ('idle', 'executing', 'waiting', 'blocked', 'complete')),
    session_id TEXT,
    adw_id TEXT,
    adw_step TEXT,
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    total_cost DECIMAL(10,4) DEFAULT 0.0000,
    archived BOOLEAN DEFAULT false,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Unique constraint: agent name must be unique per orchestrator
    CONSTRAINT unique_agent_name_per_orchestrator UNIQUE (orchestrator_agent_id, name)
);

-- Table and column comments
COMMENT ON TABLE agents IS 'Agent registry and configuration for managed agents (scoped to orchestrator)';
COMMENT ON COLUMN agents.id IS 'Unique agent identifier';
COMMENT ON COLUMN agents.orchestrator_agent_id IS 'Foreign key to orchestrator_agents table (required - agents belong to one orchestrator)';
COMMENT ON COLUMN agents.name IS 'Agent name (unique per orchestrator)';
COMMENT ON COLUMN agents.model IS 'Claude model ID (e.g., claude-sonnet-4-5-20250929)';
COMMENT ON COLUMN agents.system_prompt IS 'Agent custom system prompt';
COMMENT ON COLUMN agents.working_dir IS 'Agent working directory path';
COMMENT ON COLUMN agents.git_worktree IS 'Git worktree path if using worktrees';
COMMENT ON COLUMN agents.status IS 'Current status: idle, executing, waiting, blocked, complete';
COMMENT ON COLUMN agents.session_id IS 'Current Claude SDK session ID';
COMMENT ON COLUMN agents.adw_id IS 'AI Developer Workflow ID';
COMMENT ON COLUMN agents.adw_step IS 'AI Developer Workflow step identifier';
COMMENT ON COLUMN agents.input_tokens IS 'Cumulative input tokens consumed';
COMMENT ON COLUMN agents.output_tokens IS 'Cumulative output tokens generated';
COMMENT ON COLUMN agents.total_cost IS 'Cumulative cost in USD (from ResultMessage.usage.total_cost_usd)';
COMMENT ON COLUMN agents.archived IS 'Soft delete flag';
COMMENT ON COLUMN agents.metadata IS 'Agent configuration: allowed_tools, permission_mode, etc. (JSONB)';
-- ============================================================================
-- PROMPTS TABLE
-- ============================================================================
-- Prompts sent to agents (from engineers or orchestrator agent)
--
-- Dependencies: agents table (FK constraint)
-- Note: Cascades on delete when agent is removed

CREATE TABLE IF NOT EXISTS prompts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    task_slug TEXT,
    author TEXT NOT NULL CHECK (author IN ('engineer', 'orchestrator_agent')),
    prompt_text TEXT NOT NULL,
    summary TEXT,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    session_id TEXT
);

-- Table and column comments
COMMENT ON TABLE prompts IS 'Prompts sent to agents from engineers or orchestrator';
COMMENT ON COLUMN prompts.id IS 'Unique prompt identifier';
COMMENT ON COLUMN prompts.agent_id IS 'Target agent receiving the prompt (nullable, only populated when author = orchestrator_agent)';
COMMENT ON COLUMN prompts.task_slug IS 'Associated task identifier (kebab-case)';
COMMENT ON COLUMN prompts.author IS 'Who sent the prompt: engineer or orchestrator_agent';
COMMENT ON COLUMN prompts.prompt_text IS 'The actual prompt content';
COMMENT ON COLUMN prompts.summary IS 'AI-generated 1-sentence summary of the prompt (50-100 chars)';
COMMENT ON COLUMN prompts.timestamp IS 'When the prompt was sent';
COMMENT ON COLUMN prompts.session_id IS 'Claude SDK session ID';
-- ============================================================================
-- AGENT_LOGS TABLE
-- ============================================================================
-- Unified event log - all hook events and agent responses during task execution
-- Combines operator logs (JSONL-style task tracking), hook events, and agent response blocks
--
-- Dependencies: agents table (FK constraint)
-- Note: Cascades on delete when agent is removed

CREATE TABLE IF NOT EXISTS agent_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    session_id TEXT,
    task_slug TEXT,
    adw_id TEXT,
    adw_step TEXT,
    entry_index INTEGER,
    event_category TEXT NOT NULL CHECK (event_category IN ('hook', 'response')),
    event_type TEXT NOT NULL,
    content TEXT,
    payload JSONB DEFAULT '{}'::jsonb,
    summary TEXT,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Table and column comments
COMMENT ON TABLE agent_logs IS 'Unified event log for hooks and agent responses during task execution';
COMMENT ON COLUMN agent_logs.id IS 'Unique log entry identifier';
COMMENT ON COLUMN agent_logs.agent_id IS 'Agent that generated this event';
COMMENT ON COLUMN agent_logs.session_id IS 'Claude SDK session ID';
COMMENT ON COLUMN agent_logs.task_slug IS 'Task identifier (kebab-case)';
COMMENT ON COLUMN agent_logs.adw_id IS 'AI Developer Workflow identifier';
COMMENT ON COLUMN agent_logs.adw_step IS 'AI Developer Workflow step identifier';
COMMENT ON COLUMN agent_logs.entry_index IS 'Sequential index within task for tail reading';
COMMENT ON COLUMN agent_logs.event_category IS 'Event category: hook or response';
COMMENT ON COLUMN agent_logs.event_type IS 'Specific event type - For hooks: PreToolUse, PostToolUse, UserPromptSubmit, Stop, SubagentStop, PreCompact; For responses: text, thinking, tool_use, tool_result';
COMMENT ON COLUMN agent_logs.content IS 'Text content for text/thinking blocks';
COMMENT ON COLUMN agent_logs.payload IS 'Complete event data (tool info, block details, etc.) as JSONB';
COMMENT ON COLUMN agent_logs.summary IS 'AI-generated summary of this event';
COMMENT ON COLUMN agent_logs.timestamp IS 'When the event occurred';
-- ============================================================================
-- SYSTEM_LOGS TABLE
-- ============================================================================
-- All application logs (global application events only)
--
-- Dependencies: None
-- Note: agent-related logs should go in agent_logs table

CREATE TABLE IF NOT EXISTS system_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_path TEXT,
    adw_id TEXT,
    adw_step TEXT,
    level TEXT NOT NULL CHECK (level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR')),
    message TEXT NOT NULL,
    summary TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Table and column comments
COMMENT ON TABLE system_logs IS 'Application-level system logs (global application events only)';
COMMENT ON COLUMN system_logs.id IS 'Unique log entry identifier';
COMMENT ON COLUMN system_logs.file_path IS 'Associated file path where log was written';
COMMENT ON COLUMN system_logs.adw_id IS 'Associated ADW identifier';
COMMENT ON COLUMN system_logs.adw_step IS 'AI Developer Workflow step identifier';
COMMENT ON COLUMN system_logs.level IS 'Log level: DEBUG, INFO, WARNING, ERROR';
COMMENT ON COLUMN system_logs.message IS 'Log message';
COMMENT ON COLUMN system_logs.summary IS 'AI-generated 1-sentence summary of the log message (50-100 chars)';
COMMENT ON COLUMN system_logs.metadata IS 'Additional log context (JSONB)';
COMMENT ON COLUMN system_logs.timestamp IS 'When the log was created';
-- ============================================================================
-- INDEXES
-- ============================================================================
-- Performance indexes for all tables
--
-- Dependencies: All tables (0-4) must exist
-- Note: Idempotent - can be run multiple times safely

-- orchestrator_agents indexes
CREATE INDEX IF NOT EXISTS idx_orchestrator_agents_status ON orchestrator_agents(status);
CREATE INDEX IF NOT EXISTS idx_orchestrator_agents_updated_at ON orchestrator_agents(updated_at DESC);

-- agents indexes
CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);
CREATE INDEX IF NOT EXISTS idx_agents_archived ON agents(archived);
CREATE INDEX IF NOT EXISTS idx_agents_updated_at ON agents(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_agents_name ON agents(name);

-- prompts indexes
CREATE INDEX IF NOT EXISTS idx_prompts_agent_id ON prompts(agent_id);
CREATE INDEX IF NOT EXISTS idx_prompts_author ON prompts(author);
CREATE INDEX IF NOT EXISTS idx_prompts_timestamp ON prompts(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_prompts_task_slug ON prompts(task_slug) WHERE task_slug IS NOT NULL;

-- agent_logs indexes
CREATE INDEX IF NOT EXISTS idx_agent_logs_agent_id ON agent_logs(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_logs_task_slug ON agent_logs(task_slug) WHERE task_slug IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_agent_logs_adw_id ON agent_logs(adw_id) WHERE adw_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_agent_logs_adw_step ON agent_logs(adw_step) WHERE adw_step IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_agent_logs_task_index ON agent_logs(task_slug, entry_index) WHERE task_slug IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_agent_logs_category ON agent_logs(event_category);
CREATE INDEX IF NOT EXISTS idx_agent_logs_type ON agent_logs(event_type);
CREATE INDEX IF NOT EXISTS idx_agent_logs_category_type ON agent_logs(event_category, event_type);
CREATE INDEX IF NOT EXISTS idx_agent_logs_timestamp ON agent_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_agent_logs_session ON agent_logs(session_id) WHERE session_id IS NOT NULL;

-- system_logs indexes
CREATE INDEX IF NOT EXISTS idx_system_logs_level ON system_logs(level);
CREATE INDEX IF NOT EXISTS idx_system_logs_timestamp ON system_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_system_logs_adw_id ON system_logs(adw_id) WHERE adw_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_system_logs_adw_step ON system_logs(adw_step) WHERE adw_step IS NOT NULL;
-- ============================================================================
-- TRIGGER FUNCTIONS
-- ============================================================================
-- Functions used by triggers for automatic timestamp updates
--
-- Dependencies: orchestrator_agents and agents tables must exist
-- Note: Idempotent - CREATE OR REPLACE allows safe re-runs

-- Auto-update updated_at timestamp on orchestrator_agents
CREATE OR REPLACE FUNCTION update_orchestrator_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Auto-update updated_at timestamp on agents
CREATE OR REPLACE FUNCTION update_agents_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
-- ============================================================================
-- TRIGGERS
-- ============================================================================
-- Automatic triggers for timestamp updates
--
-- Dependencies: Functions from 6_functions.sql must exist
-- Note: Idempotent - DROP IF EXISTS + CREATE allows safe re-runs

-- Trigger for orchestrator_agents updated_at
DROP TRIGGER IF EXISTS update_orchestrator_agents_updated_at ON orchestrator_agents;
CREATE TRIGGER update_orchestrator_agents_updated_at
  BEFORE UPDATE ON orchestrator_agents
  FOR EACH ROW
  EXECUTE FUNCTION update_orchestrator_updated_at();

-- Trigger for agents updated_at
DROP TRIGGER IF EXISTS update_agents_updated_at ON agents;
CREATE TRIGGER update_agents_updated_at
  BEFORE UPDATE ON agents
  FOR EACH ROW
  EXECUTE FUNCTION update_agents_updated_at();
-- ═══════════════════════════════════════════════════════════
-- ORCHESTRATOR_CHAT TABLE
-- ═══════════════════════════════════════════════════════════
--
-- Tracks all conversations in the multi-agent orchestration system.
--
-- Key Features:
-- - Captures 3-way communication: user ↔ orchestrator ↔ command_agents
-- - sender_type and receiver_type provide directionality
-- - Single message field (no split user_message/orchestrator_message)
-- - Nullable agent_id references command agents when involved
-- - Append-only log for full conversation history
-- - JSONB metadata for extensibility
-- - Turn counter derived from row count per orchestrator_agent_id
--
-- Message Flow Examples:
-- - user → orchestrator: sender='user', receiver='orchestrator', agent_id=NULL
-- - orchestrator → user: sender='orchestrator', receiver='user', agent_id=NULL
-- - orchestrator → agent: sender='orchestrator', receiver='agent', agent_id=builder_id
-- - agent → orchestrator: sender='agent', receiver='orchestrator', agent_id=builder_id
--
-- Dependencies:
-- - orchestrator_agents table (FK: orchestrator_agent_id)
-- - agents table (FK: agent_id - nullable)
--
-- ═══════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS orchestrator_chat (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Foreign key to orchestrator agent (required)
    orchestrator_agent_id UUID NOT NULL REFERENCES orchestrator_agents(id) ON DELETE CASCADE,

    -- Sender and receiver (required)
    sender_type TEXT NOT NULL CHECK (sender_type IN ('user', 'orchestrator', 'agent')),
    receiver_type TEXT NOT NULL CHECK (receiver_type IN ('user', 'orchestrator', 'agent')),

    -- Message content (required)
    message TEXT NOT NULL,

    -- AI-generated summary (optional)
    summary TEXT,

    -- Foreign key to command agent (nullable - only when sender or receiver is 'agent')
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,

    -- Extensible metadata storage
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Constraint: agent_id must be set when sender_type or receiver_type is 'agent'
    CONSTRAINT agent_id_required_for_agents CHECK (
        (sender_type = 'agent' OR receiver_type = 'agent') = (agent_id IS NOT NULL)
    )
);

-- ═══════════════════════════════════════════════════════════
-- INDEXES
-- ═══════════════════════════════════════════════════════════

-- Index for querying by orchestrator_agent_id (for conversation history)
CREATE INDEX IF NOT EXISTS idx_orchestrator_chat_orch_id ON orchestrator_chat(orchestrator_agent_id);

-- Index for querying by agent_id (for command agent message history)
CREATE INDEX IF NOT EXISTS idx_orchestrator_chat_agent_id ON orchestrator_chat(agent_id);

-- Index for querying by sender_type (for filtering by sender)
CREATE INDEX IF NOT EXISTS idx_orchestrator_chat_sender_type ON orchestrator_chat(sender_type);

-- Index for querying by receiver_type (for filtering by receiver)
CREATE INDEX IF NOT EXISTS idx_orchestrator_chat_receiver_type ON orchestrator_chat(receiver_type);

-- Composite index for ordered conversation retrieval
CREATE INDEX IF NOT EXISTS idx_orchestrator_chat_orch_created ON orchestrator_chat(orchestrator_agent_id, created_at DESC);

-- Composite index for agent conversation retrieval
CREATE INDEX IF NOT EXISTS idx_orchestrator_chat_agent_created ON orchestrator_chat(agent_id, created_at DESC);

-- ═══════════════════════════════════════════════════════════
-- COMMENTS
-- ═══════════════════════════════════════════════════════════

COMMENT ON TABLE orchestrator_chat IS
    'Append-only conversation log capturing 3-way communication: user ↔ orchestrator ↔ agents. Turn counter derived from row count per orchestrator_agent_id.';

COMMENT ON COLUMN orchestrator_chat.orchestrator_agent_id IS
    'Foreign key to orchestrator_agents table (required)';

COMMENT ON COLUMN orchestrator_chat.sender_type IS
    'Who sent this message: user, orchestrator, or agent';

COMMENT ON COLUMN orchestrator_chat.receiver_type IS
    'Who receives this message: user, orchestrator, or agent';

COMMENT ON COLUMN orchestrator_chat.message IS
    'The message text content';

COMMENT ON COLUMN orchestrator_chat.summary IS
    'AI-generated 1-sentence summary of the message (50-100 chars)';

COMMENT ON COLUMN orchestrator_chat.agent_id IS
    'Foreign key to agents table (required when sender_type or receiver_type is agent, NULL otherwise)';

COMMENT ON COLUMN orchestrator_chat.metadata IS
    'Extensible JSONB field for additional context (tools_used, task_slug, etc)';
