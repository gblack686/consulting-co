# /note-create Command

Create a new note in the Obsidian vault using a template.

## Usage

```
/note-create [title] [category?]
```

## Parameters

- `title` (required): The title of the note to create
- `category` (optional): The note category - defaults to "daily"
  - Options: `daily`, `architecture`, `learning`, `task`, `meeting`

## Examples

```bash
# Create a daily note
/note-create "Working on landing page redesign"

# Create an architecture decision
/note-create "Lambda vs ECS Decision" architecture

# Create a learning note
/note-create "AWS CDK Best Practices" learning

# Create a task note
/note-create "Implement SSL certificates" task
```

## Behavior

When you run this command, Claude will:

1. Load the appropriate template for the category
2. Generate frontmatter with:
   - Current date/time
   - Appropriate tags
   - Project name
   - Auto-generated metadata
3. Create the note in the correct folder (based on vault settings)
4. Return the file path for reference
5. Optionally open the note for editing

## Configuration

The command uses settings from:
- `.claude/skills/obsidian-vault/config/vault-settings.json`
- `.claude/skills/obsidian-vault/config/note-categories.yaml`

## Related Commands

- `/note-search` - Search for existing notes
- `/decision-log` - Create an ADR specifically
- `/daily-note` - Create/open today's daily note
- `/context-load` - Load a note into conversation

## Integration

This command is part of the **obsidian-vault** skill and works seamlessly with:
- SessionStart hook (auto-creates daily notes)
- Stop hook (logs session to note)
- @knowledge-curator agent
