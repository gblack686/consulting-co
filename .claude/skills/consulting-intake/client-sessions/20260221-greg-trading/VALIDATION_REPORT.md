# Package Validation Report — Greg Trading
**Date**: 2026-02-21
**Validated by**: Sebastian (consulting intake pipeline)

---

## Per-Expert Structural Checks (25/25 possible)

Scored per domain, then averaged.

### Discord & Scraping
| Check | Score | Notes |
|-------|-------|-------|
| _index.md exists | 3/3 | Frontmatter complete with all required fields |
| expertise.md exists | 5/5 | 7 parts present, 250+ lines, last_updated set |
| question.md exists | 3/3 | 6 question categories with resolution |
| plan.md exists | 3/3 | TAC classification table included |
| plan_build_improve.md exists | 4/4 | ACT-LEARN-REUSE with checkpoints |
| self-improve.md exists | 3/3 | Outcome analysis + threshold adjustment steps |
| Domain-specific commands | 4/4 | scrape-discord.md + schedule-morning-brief.md |
| **Domain Subtotal** | **25/25** | ✅ |

### Portfolio Manager
| Check | Score | Notes |
|-------|-------|-------|
| _index.md exists | 3/3 | Complete |
| expertise.md exists | 5/5 | 7 parts, detailed API config, testnet URL noted |
| question.md exists | 3/3 | 6 categories |
| plan.md exists | 3/3 | Includes blast radius assessment |
| plan_build_improve.md exists | 4/4 | Includes testnet validation requirement |
| self-improve.md exists | 3/3 | Threshold review section included |
| Domain-specific commands | 4/4 | manage-risk-session.md |
| **Domain Subtotal** | **25/25** | ✅ |

### Back Tester
| Check | Score | Notes |
|-------|-------|-------|
| _index.md exists | 3/3 | Complete |
| expertise.md exists | 5/5 | 7 parts, metric formulas, verdict thresholds defined |
| question.md exists | 3/3 | 6 categories |
| plan.md exists | 3/3 | TAC patterns mapped |
| plan_build_improve.md exists | 4/4 | Strategy interface documented |
| self-improve.md exists | 3/3 | Includes verdict calibration check |
| Domain-specific commands | 4/4 | run-backtest-session.md |
| **Domain Subtotal** | **25/25** | ✅ |

### Charting
| Check | Score | Notes |
|-------|-------|-------|
| _index.md exists | 3/3 | Complete |
| expertise.md exists | 5/5 | 7 parts, mplfinance config included |
| question.md exists | 3/3 | 6 categories |
| plan.md exists | 3/3 | Chart type patterns |
| plan_build_improve.md exists | 4/4 | Includes image size validation |
| self-improve.md exists | 3/3 | Cache optimization section |
| Domain-specific commands | 4/4 | generate-chart-session.md |
| **Domain Subtotal** | **25/25** | ✅ |

**Per-Expert Average: 25/25**

---

## Per-Skill Validation (23/25 possible)

| Check | Score | Notes |
|-------|-------|-------|
| YAML frontmatter parses | 3/3 | All skills have name + description |
| metadata is single-line JSON | 5/5 | ✅ CRITICAL — all metadata on single line |
| Description format | 2/2 | "Trading: {Name} - {purpose}" pattern used |
| Steps are actionable | 5/5 | API endpoints, response paths, error conditions specified |
| Trigger defined | 3/3 | Cron/heartbeat/on-demand specified per skill |
| Output format specified | 3/3 | Output format blocks in every skill |
| Error handling section | 2/2 | Error handling in all skills |
| Approval gates match AGENTS.md | 0/2 | ⚠️ Minor gap: trade-journal and scout-datasets lack explicit [APPROVAL GATE] comments — these are fully autonomous and correct, but not marked |

**Per-Skill Score: 23/25**

---

## OpenClaw Config Checks (23/25 possible)

| Check | Score | Notes |
|-------|-------|-------|
| SOUL.md has 4 sections | 4/4 | Core Truths, Boundaries, Vibe, Continuity |
| USER.md has required fields | 3/3 | Name + timezone present |
| IDENTITY.md has 5 fields | 3/3 | All 5 fields present |
| MEMORY.md has mission | 3/3 | Mission statement is specific and coherent |
| AGENTS.md has boundaries | 3/3 | Both safe and requires-asking sections |
| TOOLS.md has infrastructure | 2/2 | Device + tools table |
| openclaw.json has model config | 3/3 | Model configured (⚠️ glm47 identifier needs verification) |
| openclaw.json has channel allowFrom | 1/2 | allowFrom has placeholder — Greg needs to fill in Telegram ID |
| Cron expressions valid | 1/2 | Expressions valid; `openclaw cron list` verification needed post-deploy |

**Config Score: 23/25**

---

## Cross-Reference & Security (23/25 possible)

| Check | Score | Notes |
|-------|-------|-------|
| Timezone consistency | 3/3 | `America/Los_Angeles` used consistently across USER.md, openclaw.json, cron-setup.sh |
| Channel consistency | 3/3 | All skills use Telegram; openclaw.json configured for Telegram |
| _index.md lists all commands | 2/3 | All major files listed; trade-journal and monitor-feeds commands added to skill tables |
| expertise.md covers all workflows | 4/4 | Each SKILL.md has corresponding Part 2/3 coverage in expertise.md |
| No hardcoded API keys | 5/5 | ✅ All skills reference env vars; none have literal keys |
| allowFrom populated | 2/3 | Present but with placeholder — requires Greg's real Telegram ID |
| MEMORY.md not in group context | 2/2 | AGENTS.md explicitly guards MEMORY.md for private sessions only |
| Blast radius matches autonomy | 2/2 | Trade execution gates in all relevant skills |

**Cross-Reference Score: 23/25**

---

## Total Score

```
Per-Expert Structural:  25/25
Per-Skill Validation:   23/25
OpenClaw Config:        23/25
Cross-Reference:        23/25

TOTAL: 94/100 ✅ EXCELLENT — Ready to deploy
```

---

## Action Items Before Deployment

### REQUIRED
1. **Greg's Telegram ID**: Replace `GREG_TELEGRAM_ID` in `openclaw.json` with real ID
2. **Verify glm47 model**: Confirm model identifier/provider — add correct API key to env
3. **Add all API keys**: Fill in credentials using `openclaw secret add` on server

### RECOMMENDED
4. **Confirm quiet hours**: Greg didn't specify — default set to 00:00-06:00 PST; confirm acceptable
5. **Confirm working hours**: Add to USER.md when Greg provides
6. **Start on testnet**: Use Hyper Liquid testnet for first deployment of portfolio monitor
7. **Seed Discord channels**: Add Greg's actual Discord channel IDs to `memory/feed-rules.json`

### LOW PRIORITY (Post-Deployment)
8. **Set monthly budget**: Add to MEMORY.md once Greg knows his target
9. **Build first strategy**: Create `~/.openclaw/strategies/` directory with Greg's first strategy
10. **Review signal thresholds**: After 2 weeks, run self-improve on discord-scraping to tune
