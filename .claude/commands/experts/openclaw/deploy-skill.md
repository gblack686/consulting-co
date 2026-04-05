---
allowed-tools: Read, Bash, Glob, Grep
description: Convert an Obsidian AI-Agent-KB file to OpenClaw SKILL.md format and deploy via SCP
argument-hint: [skill-name or path from find-skills results]
---

# OpenClaw Expert - Deploy Skill

Convert an Obsidian AI-Agent-KB skill/command/expert/script to OpenClaw SKILL.md format and deploy it to the instance.

## Variables

SKILL_INPUT: $ARGUMENTS
SSH: SSH key auth configured (ed25519, no passphrase)
INSTANCE_IP: Gregs-Mac-mini.local
KB_PATH: C:/Users/gblac/OneDrive/Desktop/obsidian/Gbautomation/AI-Agent-KB
DEPLOY_TARGET: /Users/greg/.openclaw/workspace/skills

## Instructions

1. Read expertise.yaml to get the current instance IP.
2. Resolve the skill source file from the input (name or path).
3. Read the Obsidian source file and extract frontmatter + content.
4. Strip Obsidian-specific syntax and convert to OpenClaw SKILL.md format.
5. Deploy to the instance via SCP.
6. Restart OpenClaw and verify.

## Workflow

### Step 0: Get Instance IP

Read `.claude/commands/experts/openclaw/expertise.yaml` and extract `infrastructure.our_instance.instance_ip`.
If the IP is "TBD", inform the user that no instance is deployed and suggest running the install wizard.

### Step 1: Resolve Source File

If SKILL_INPUT is a full path, use it directly.
If SKILL_INPUT is a name, search for it:

```bash
find "{KB_PATH}" -iname "*{SKILL_INPUT}*" -name "*.md" -not -name "_*" 2>/dev/null
```

Read the resolved file to get its full content.

### Step 2: Extract Metadata

From the frontmatter, extract:
- `name` - Use as the skill directory name (kebab-case)
- `type` - The entity type (skill, command, expert, script, ai-doc)
- `tags` - For the description keywords
- `status` - Must be `active` to deploy
- `category` - For organizing

### Step 3: Generate OpenClaw SKILL.md

Convert the Obsidian file to OpenClaw format:

```markdown
---
name: {kebab-case-name}
description: "{category-label}: {Display Name} - {purpose/description extracted from content}"
---

{Cleaned content body}
```

#### Content Conversion Rules

Strip these Obsidian-specific elements:
- **Wikilinks**: `[[page-name]]` -> `page-name`, `[[page|display]]` -> `display`
- **Image embeds**: `![[image.jpg]]` -> remove entirely
- **Banner lines**: Lines with only `![[_assets/...]]` -> remove
- **Dataview queries**: ` ```dataview ... ``` ` blocks -> remove
- **cssclasses**: Remove from frontmatter
- **MTG card fields**: Remove `mtg_card`, `mtg_color`, `mtg_edition`, `mtg_set_code`, `banner` from frontmatter
- **Obsidian comments**: `%%...%%` -> remove
- **Templater**: `<% tp.date... %>` -> replace with actual date
- **Mermaid diagrams**: Keep as-is (they're useful documentation)

### Step 4: Deploy to Instance via SCP

Skills must be placed in `/Users/greg/.openclaw/workspace/skills/{skill-name}/SKILL.md`.

1. Write the generated SKILL.md to a local temp file
2. Create the skill directory on the instance via SSH
3. Upload the file via SCP

```bash
# Write SKILL.md to local temp file
# (done programmatically by the agent)

# Create directory on instance
ssh -o ConnectTimeout=10 greg@Gregs-Mac-mini.local \
  "mkdir -p ~/.openclaw/workspace/skills/{skill-name}"

# Upload SKILL.md via SCP
scp -o ConnectTimeout=10 \
  /tmp/{skill-name}-SKILL.md \
  greg@Gregs-Mac-mini.local:~/.openclaw/workspace/skills/{skill-name}/SKILL.md
```

### Step 5: Restart and Verify

```bash
ssh -o ConnectTimeout=10 greg@Gregs-Mac-mini.local \
  "openclaw gateway restart && \
   sleep 3 && \
   ls -la ~/.openclaw/workspace/skills/{skill-name}/SKILL.md && \
   echo '=== Deployed Skills ===' && \
   ls ~/.openclaw/workspace/skills/"
```

## Report Format

```markdown
## Skill Deployment Report

**Skill**: {name}
**Source**: {obsidian path}
**Deployed to**: /Users/greg/.openclaw/workspace/skills/{skill-name}/SKILL.md
**Services**: {restarted/failed}

### SKILL.md Preview

{First 20 lines of generated SKILL.md}

### Verification

- [ ] Directory created
- [ ] SKILL.md written
- [ ] OpenClaw gateway restarted
- [ ] Skill visible in skills directory
```

## Batch Deployment

When deploying multiple skills, process each one sequentially:
1. Generate all SKILL.md files locally
2. SCP all skills to the instance
3. Restart OpenClaw gateway once at the end
4. Verify all skills appear

This is more efficient than restarting after each skill.
