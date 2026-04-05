# META-3: YouTube Intelligence Agent — Universal Template Plan
**Date:** 2026-03-18
**Build location:** `.claude/skills/consulting-intake/templates/agents/youtube/`

---

## What to Build

Generalize the existing YouTube agent (currently tied to Greg's trading context) into a universal template that works for any client domain. Add a `channel-registry` skill and a `market-research` mode.

---

## Current State (Greg-specific — needs generalization)

```
templates/agents/youtube/
├── SOUL.md          ← Good, already domain-agnostic ✅
├── IDENTITY.md      ← Has trading-specific references — UPDATE
├── AGENTS.md        ← Has Greg-specific channels — UPDATE
└── skills/youtube/
    ├── extract-transcript/SKILL.md   ← Good ✅
    ├── scan-channel/SKILL.md         ← Has trading context — UPDATE
    └── summarize-video/SKILL.md      ← Mostly generic — minor update
```

---

## Files to Update

### IDENTITY.md — Remove trading references
Replace all trading-specific text. Generic template:
```
Name: Scout 📡
Role: YouTube Intelligence Agent
Domain: {client_domain}
Tracked channels: see channel-registry skill
Focus: Extract insights relevant to {client_industry}
```

### AGENTS.md — Remove Greg's hardcoded channels
Replace with placeholder channel list that gets populated from client profile:
```
Tracked channels: {youtube_channel_list}
(Populated from session_output/tool_inventory.json → youtube_channels field)
```

### scan-channel/SKILL.md — Generalize
Remove trading-specific language (signals, Hyper Liquid, etc.).
Add: `{channel_category}` and `{insight_type}` placeholders.
Add market-research mode: search YouTube by topic keyword, not just followed channels.

---

## Files to Create

### `templates/skills/youtube/channel-registry/SKILL.md`

Manages a list of tracked YouTube channels per client.

**Invocable commands:**
- `add-channel {url}` — add a channel to tracking list
- `remove-channel {handle}` — remove from list
- `list-channels` — show all tracked with last-scan date
- `import-from-session` — auto-populate from `tool_inventory.json`

**Storage:** `workspace/data/channel-registry.json`
```json
{
  "channels": [
    {"handle": "@channelname", "url": "...", "category": "competitor|education|news", "added": "YYYY-MM-DD", "last_scanned": "YYYY-MM-DD"}
  ]
}
```

### `references/youtube-agent.md`

Document:
- yt-dlp install: `C:/Users/gblac/AppData/Local/Programs/Python/Python312/Scripts/yt-dlp`
- yt-dlp command: `yt-dlp --write-auto-subs --write-info-json --skip-download --sub-langs en --sub-format json3 --output "{OUT}/%(id)s" "https://youtube.com/watch?v={ID}"`
- Chrome fallback: `openclaw browser` headless extraction
- Channel registry pattern: scan → summarize → write to Obsidian
- How to connect to Obsidian: summaries → `Obsidian/Research/YouTube/{YYYY-MM}/`
- Pi extensions that complement this: `badlogic/pi-skills` YouTube skill, `nicobailon/pi-web-access`
- Cron example: daily overnight scan of all tracked channels

---

## Acceptance Criteria

- [ ] IDENTITY.md contains no trading-specific references
- [ ] AGENTS.md uses `{youtube_channel_list}` placeholder
- [ ] `scan-channel/SKILL.md` has market-research mode (search by topic)
- [ ] `channel-registry/SKILL.md` created with add/remove/list/import commands
- [ ] `references/youtube-agent.md` documents yt-dlp setup fully
- [ ] `consulting-intake/SKILL.md` Step 2b references youtube agent as universal template
- [ ] Tested: generate a client workspace, confirm youtube agent has no Greg-specific text

---

## Prompt for OpenClaw

> "Generalize the YouTube agent template from the spec at `specs/meta3-youtube-universal-plan.md`. Update `templates/agents/youtube/IDENTITY.md` and `AGENTS.md` to remove trading-specific references. Create `templates/skills/youtube/channel-registry/SKILL.md`. Create `references/youtube-agent.md` documenting yt-dlp setup. The yt-dlp binary is at `C:/Users/gblac/AppData/Local/Programs/Python/Python312/Scripts/yt-dlp`."
