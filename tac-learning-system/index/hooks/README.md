# TAC Hook Index

80+ Claude Code hooks across TAC repositories.

## What is a Hook?

A Claude Code hook is a Python script that executes at specific lifecycle events during a Claude Code session. Hooks live in `.claude/hooks/`.

## Hook Types

| Hook | Event | Purpose |
|------|-------|---------|
| `session_start.py` | Session begins | Initialize context, load state |
| `pre_tool_use.py` | Before tool call | Validate, modify, block |
| `post_tool_use.py` | After tool call | Log, analyze, react |
| `pre_compact.py` | Before context compaction | Save important state |
| `user_prompt_submit.py` | User sends message | Intercept, enhance |
| `stop.py` | Session ends | Cleanup, summarize |
| `subagent_stop.py` | Subagent completes | Handle results |
| `notification.py` | Events occur | Alert user |

## Hook Evolution

| TAC | Hooks | Key Additions |
|-----|-------|---------------|
| agentic-prompt-engineering | 2 | context_bundle_builder, universal_hook_logger |
| building-specialized-agents | 3 | + dangerous_command_blocker |
| tac-4 | 8 | + notification, pre/post_tool_use, stop |
| tac-5 | 10 | + tts_notification |
| tac-6 | 12 | + pre_compact, user_prompt_submit |
| tac-7 | 14 | Enhanced utils |
| multi-agent-orchestration | 18 | + send_event, session_start |
| tac-8 | 14+ per app | Specialized variations |

## By Repository

### agentic-prompt-engineering (2 hooks)
Path: `C:\Users\gblac\OneDrive\Desktop\tac\agentic-prompt-engineering\.claude\hooks\`

- **[context_bundle_builder.py](file:///C:/Users/gblac/OneDrive/Desktop/tac/agentic-prompt-engineering/.claude/hooks/context_bundle_builder.py)** - Builds context bundles for prompts
- **[universal_hook_logger.py](file:///C:/Users/gblac/OneDrive/Desktop/tac/agentic-prompt-engineering/.claude/hooks/universal_hook_logger.py)** - Logs all hook events

### building-specialized-agents (3 hooks)
Path: `C:\Users\gblac\OneDrive\Desktop\tac\building-specialized-agents\.claude\hooks\`

- context_bundle_builder.py
- **[dangerous_command_blocker.py](file:///C:/Users/gblac/OneDrive/Desktop/tac/building-specialized-agents/.claude/hooks/dangerous_command_blocker.py)** - Blocks dangerous commands
- universal_hook_logger.py

### tac-4 (8 hooks)
Path: `C:\Users\gblac\OneDrive\Desktop\tac\tac-4\.claude\hooks\`

```
hooks/
├── notification.py
├── post_tool_use.py
├── pre_tool_use.py
├── stop.py
├── subagent_stop.py
└── utils/
    ├── constants.py
    └── llm/
        ├── anth.py
        └── oai.py
```

### tac-5 (10 hooks)
Path: `C:\Users\gblac\OneDrive\Desktop\tac\tac-5\.claude\hooks\`

All tac-4 hooks plus:
- **tts_notification.py** - Text-to-speech notifications

### tac-6 (12 hooks)
Path: `C:\Users\gblac\OneDrive\Desktop\tac\tac-6\.claude\hooks\`

All tac-5 hooks plus:
- **pre_compact.py** - Runs before context compaction
- **user_prompt_submit.py** - Intercepts user prompts

### tac-7 (14 hooks)
Path: `C:\Users\gblac\OneDrive\Desktop\tac\tac-7\.claude\hooks\`

Same as tac-6 with enhanced utilities

### multi-agent-orchestration (18 hooks)
Path: `C:\Users\gblac\OneDrive\Desktop\tac\multi-agent-orchestration\.claude\hooks\`

Most comprehensive hook set:

```
hooks/
├── notification.py
├── post_tool_use.py
├── pre_compact.py
├── pre_tool_use.py
├── send_event.py           # WebSocket events
├── session_start.py        # Initialize session
├── stop.py
├── subagent_stop.py
├── user_prompt_submit.py
└── utils/
    ├── constants.py
    ├── model_extractor.py
    ├── summarizer.py
    ├── llm/
    │   ├── anth.py
    │   ├── oai.py
    │   └── ollama.py
    └── tts/
        ├── elevenlabs_tts.py
        ├── openai_tts.py
        └── pyttsx3_tts.py
```

## Hook Utilities

Most TAC hooks share common utilities in `utils/`:

| Module | Purpose |
|--------|---------|
| `constants.py` | Shared constants |
| `llm/anth.py` | Anthropic API wrapper |
| `llm/oai.py` | OpenAI API wrapper |
| `llm/ollama.py` | Ollama integration |
| `tts/elevenlabs_tts.py` | ElevenLabs TTS |
| `tts/openai_tts.py` | OpenAI TTS |
| `tts/pyttsx3_tts.py` | Local TTS |
| `model_extractor.py` | Extract model info |
| `summarizer.py` | Summarize context |

## Hook Patterns

### 1. Validation Hook
Block or modify tool calls based on rules.
```python
# pre_tool_use.py
def validate(tool_name, args):
    if is_dangerous(tool_name, args):
        return {"block": True, "reason": "Dangerous command"}
```

### 2. Logging Hook
Record events for analysis.
```python
# post_tool_use.py
def log(tool_name, result):
    logger.info(f"{tool_name}: {result}")
```

### 3. Enhancement Hook
Add context or modify behavior.
```python
# user_prompt_submit.py
def enhance(prompt):
    return prompt + load_context()
```

### 4. Notification Hook
Alert user about events.
```python
# notification.py
def notify(event):
    send_tts(f"Task {event.status}")
```

## Related Resources

- [Claude Code Hook Expert](file:///C:/Users/gblac/OneDrive/Desktop/tac/agentic-prompt-engineering/.claude/commands/experts/cc_hook_expert/)
- [Consulting-co Hooks](file:///C:/Users/gblac/OneDrive/Desktop/consulting-co/.claude/hooks/)
