# Domain Discovery — Bootstrap Reverse Prompts

These are the initial meta-prompts to give your OpenClaw agent after install. Each one kicks off a self-organizing workflow. Copy-paste any of these into Telegram/Discord.

---

## 1. The Big Scan

> Hey, I've given you access to my GitHub repos. I'd like you to scan all of them and figure out what I'm actually working on. Look at file structure, recency of commits, READMEs, and any openclaw.json or CLAUDE.md files. Group everything into domains — coherent areas of work, not just repo names. Tell me what you find, what's active vs. stale, and what connects to what. Then for each domain, suggest what workflows we could build together.

## 2. The Second Brain Setup

> I'd like to set up an Obsidian vault as a second brain for all my projects. Based on the domains you discovered, create a structured archive — one folder per domain with an overview, repo inventory, goals, and gaps. Make it so I can glance at the index and know exactly where everything stands. What's the best way to organize this?

## 3. The Reverse Prompt Generator

> For each domain you've identified, I want you to generate 3-5 "reverse prompts" — questions I can ask you that will help us build deeper skills and workflows for that domain. Follow this pattern: "Hey, I'd like to set up an advanced [DOMAIN] workflow. What system can we build where you [DO SOMETHING USEFUL] and then [TRIGGER FOLLOW-UP ACTIONS]?" Make them specific to my actual repos and APIs.

## 4. The Goal Setter

> Look at each domain and tell me: what am I trying to accomplish? What's the gap between where things are now and where they should be? For each domain, propose one concrete goal I should set for the next 2 weeks. Make it specific and measurable — not "improve trading" but "build a skill that scores Discord signals and posts top 3 to a daily brief channel."

## 5. The Connector

> Which of my domains should talk to each other? Where are there natural handoffs — like trading signals feeding into position management, or client research feeding into proposal generation? Help me design the cross-domain workflows that would make the whole system more than the sum of its parts.

## 6. The Skill Builder (Alex Finn pattern)

> Hey, I just did [THING] really well. Turn that into a skill so I can do it again.

> Hey, I just did [THING] poorly. Figure out what went wrong, come up with a better approach, and write yourself a skill so you don't make that mistake again.

## 7. The Daily Digest

> Set up a daily digest workflow. Every evening at 6pm, summarize what happened across all my active domains today — any new commits, any signals, any client messages, any tasks completed. Put it in a Discord channel called #daily-digest. What information do you need to make this work?

## 8. The Security Auditor

> Scan all my repos for exposed secrets — API keys, tokens, passwords in config files, .env files committed to git. Don't just find them — help me rotate them and move them into proper secret storage. What's the safest way to handle this?

---

## How to Use These

1. **Start with #1** (The Big Scan) — this gives your agent the lay of the land
2. **Then #2** (Second Brain) — this creates the archive structure
3. **Then #3** (Reverse Prompts) — this generates domain-specific prompts
4. **Use #6** ongoing — every time your agent does something well or poorly

The key insight: **you don't install skills, you have your agent build its own.** These prompts are conversation starters, not commands. Let the agent ask you follow-up questions. The back-and-forth is where the best workflows emerge.
