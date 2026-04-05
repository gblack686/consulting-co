# Issue: Context Window Metric Shows Cumulative Tokens Instead of Actual Context Usage

**Created**: 2026-01-16
**Status**: Open
**Priority**: Medium

## Problem

The agent list displays context window usage as `306k/200k` which is impossible - a model can't have more context than its maximum.

## Root Cause

In `frontend/src/components/AgentList.vue:274-275`:
```javascript
const getTotalTokens = (agent: Agent): number => {
  return agent.input_tokens + agent.output_tokens;
};
```

This returns **cumulative** tokens across all API calls, not the current context window usage.

## Expected Behavior

The metric should show **actual context window usage** - the number of tokens currently in the conversation context, similar to what Claude Code's `/context` command returns.

## Suggested Fix

Options:
1. Track context window per session by capturing the `context_tokens` from API responses
2. Parse the `/context` output when available and store in a `context_window` field
3. Calculate from the most recent message's token count rather than cumulative sum
4. Add a `context_window` column to the agents table in the database schema

## Files to Modify

- `frontend/src/components/AgentList.vue` - Update `getTotalTokens` function
- `backend/models.py` - Add `context_window` field to Agent model
- `backend/services/agent_service.py` - Update context tracking logic

## Environment

- Frontend: Vue 3 + TypeScript
- Backend: Python FastAPI
- Database: Supabase PostgreSQL
