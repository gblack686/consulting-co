---
allowed-tools: Read, Glob, Grep, Bash
description: Plan library catalog changes — adding skills, restructuring, syncing to new devices
argument-hint: [what to plan]
---

# Library Expert - Plan Mode

Plan changes to the-library catalog without executing them.

## Variables

USER_REQUEST: $ARGUMENTS
EXPERTISE_PATH: .claude/commands/experts/library/expertise.yaml
LIBRARY_YAML: C:/Users/gblac/OneDrive/Desktop/tac/the-library/library.yaml

## Instructions

- DO NOT modify any files — planning only
- Read expertise and catalog to understand current state
- Propose specific changes with exact YAML entries and commands

## Workflow

1. Read `EXPERTISE_PATH` and `LIBRARY_YAML`
2. Analyze USER_REQUEST against current catalog state
3. Propose plan with:
   - Entries to add/modify/remove in library.yaml
   - Obsidian notes to generate
   - Commands to run (`/library add`, `python scripts/generate_obsidian_notes.py`, etc.)
4. List risks and dependencies
