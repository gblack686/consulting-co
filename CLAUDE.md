## Always save file generated .md files in .claude/context/{group}/*.md unless told otherwise

## Obsidian Directory - C:\Users\gblac\OneDrive\Desktop\obsidian\Gbautomation

## Always use a template when creating new files in obsidian. Look for other files in the folder for template types. Templates can be found in desktop/obsidian/gbautomation/obsidian-docs/Template-Library-Index.md 

## Choose random ports rather than 3000. Random ports in range 3025-3099

## Linear-Coding-Agent-Harness (GBAutomation Marketplace)

### Location
`C:\Users\gblac\OneDrive\Desktop\gbautomation-marketplace-linear`

### Critical Fix: OAuth Token Issue
The Claude CLI uses its own stored credentials by default. Setting `ANTHROPIC_API_KEY` or `CLAUDE_CODE_OAUTH_TOKEN` in `.env` will OVERRIDE the CLI's valid internal auth with potentially expired tokens, causing "Invalid API key" errors.

**Solution**: Comment out both OAuth-related env vars in `.env`:
```
# CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-...  # Commented out
# ANTHROPIC_API_KEY=sk-ant-oat01-...        # Commented out
```

### How to Start the Agent
```bash
cd "C:/Users/gblac/OneDrive/Desktop/gbautomation-marketplace-linear"
python autonomous_agent_demo.py --project-dir "C:/Users/gblac/OneDrive/Desktop/gbautomation-marketplace-linear/generations"
```

For unlimited iterations (full project completion):
```bash
python autonomous_agent_demo.py --project-dir "C:/Users/gblac/OneDrive/Desktop/gbautomation-marketplace-linear/generations"
```

For testing with limited iterations:
```bash
python autonomous_agent_demo.py --project-dir "C:/Users/gblac/OneDrive/Desktop/gbautomation-marketplace-linear/generations" --max-iterations 5
```

### Linear Project
- Project: GBAutomation Marketplace Ecosystem
- URL: https://linear.app/ai-agent-mastery-gb/project/gbautomation-marketplace-ecosystem-e489c8c8b733
- Total Issues: 116 (AI-5 through AI-120)
- META Issue: AI-120 (tracks overall progress)

