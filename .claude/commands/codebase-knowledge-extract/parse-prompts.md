# Parse Prompts

Extract TAC prompt entities from markdown files.

## What This Does

Parses all `.md` files in `.claude/commands/` and `specs/` directories to extract:
- Prompt structure (sections, workflow steps)
- Delegations (references to other prompts)
- Tool mentions (MCP tools, commands)
- Success criteria
- Metadata (frontmatter)

## Run

```bash
cd tac-learning-system
python parser/prompt_parser.py
```

## Output

Saves to: `tac-learning-system/data/tac-2/prompts.json`

## Expected Results

- Prompt entities with full structure
- Delegation relationships mapped
- Workflow steps extracted
- Prompt type classification (simple-task, orchestration, etc.)

## Example Output

```json
{
  "name": "Prime",
  "prompt_type": "simple-task",
  "sections": {
    "Run": "git ls-files",
    "Read": "README.md"
  },
  "delegations": [],
  "workflow_steps": []
}
```
