# Fisch Group Second-Brain — Ontology Improvement Log

**Date**: 2026-04-17
**Vault**: `archive/claude-repos/gbauto-fisch-group/second-brain/`

## Problem

Graph view showed a flat star topology — Dashboard connected to everything, nothing connected to each other. No intermediate MOC layer, no lateral cross-links, no tag ontology for graph coloring.

## Changes Made

### 1. Sub-MOCs Created (5 new files)
- `agents/_index.md` — agent directory + workflow map + architecture link
- `workflows/_index.md` — all 27 workflows by phase + blocker references
- `contacts/_index.md` — team + clients + ownership map
- `intelligence/_index.md` — sessions + decisions + decision→impact chain
- `projects/_index.md` — active projects + dependency chain diagram

### 2. Lateral Cross-Links Added (across all 20+ existing files)

**Agents** (5 files enriched):
- finn.md: links to delegates (4 agents), workflows owned (2), skills (2), depends-on (OpenClaw)
- client-ops.md: workflows owned (2), serves clients (3)
- data-airtable.md: workflows owned (3), primary client (Piermont), blocked-by (2)
- garys-cs.md: links to Gary's client, depends-on (internal stability)
- permissions.md: skill (Access Audit), serves clients (3) + team (2)

**Workflows** (5 files enriched):
- Each workflow now links to: executing agent, affected clients, related workflows, blockers
- Added workflow↔workflow links (e.g., Cash Position feeds Weekly Digest)

**Contacts** (5 files enriched):
- Piermont: added 4 workflow references showing automation coverage
- Gary's, Drop Fitness: updated stage tags
- Michael: added client links + approval scope
- Emil: added ownership links (projects, agent config)

**Projects** (2 files enriched):
- Supabase: added owner, discovery session, downstream effects
- OpenClaw: added dependent skills/crons, tool inventory link

**Intelligence** (3 files enriched):
- Sessions: added links to decisions produced, attendees, projects discovered
- Decisions: added links to source session, downstream agents/workflows

### 3. Tag Ontology Standardized

Replaced ad-hoc tags with namespace/value pattern:
- `domain/*` — finance, ecommerce, retail, infrastructure, operations, etc.
- `stage/*` — intake, planned, building, active, blocked, phase-2
- `role/*` — partner, engineer, operator, approver

### 4. Dashboard Updated
- Each section header now links to its sub-MOC (e.g., "Agents → Full Agent Directory")
- Added Projects section linking to projects/_index

### 5. Ontology Documentation
- `obsidian/ONTOLOGY.md` — full linking guide with required/lateral link types, tag taxonomy, recommended graph color groups and force settings

## Link Count

| Metric | Before | After |
|--------|--------|-------|
| Total wiki-links | ~47 | ~150+ |
| MOC files | 1 (Dashboard) | 6 (Dashboard + 5 sub-MOCs) |
| Lateral cross-links | ~5 | ~60+ |
| Files with frontmatter tags | ~15 | all 28+ |
| Orphan notes | several | 0 |

## Graph Topology

**Before**: Star (Dashboard → everything)
**After**: Hub-and-spoke with mesh (Dashboard → MOCs → notes ↔ notes)

## Recommended Next Steps

1. Set up graph color groups in Obsidian (see ONTOLOGY.md)
2. Install Waypoint plugin for auto-MOC maintenance
3. As new notes are added, follow ONTOLOGY.md linking guide
