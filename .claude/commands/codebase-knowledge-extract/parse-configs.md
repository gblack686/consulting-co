# Parse Configs

Extract configuration entities from MCP, env, and dependency files.

## What This Does

Parses configuration files to extract:
- **MCP Servers**: From `.mcp.json` (command, args, env vars)
- **Environment Variables**: From `.env` files (with secret masking)
- **Dependencies**:
  - Python: `requirements.txt`
  - Node.js: `package.json`
- **YAML/JSON Configs**: Settings and configurations

## Run

```bash
cd tac-learning-system
python parser/config_parser.py
```

## Output

Saves to: `tac-learning-system/data/tac-2/config_entities.json`

## Expected Results

- MCP server definitions extracted
- Environment variables identified (secrets masked)
- Dependency lists (Python and Node)
- Build scripts from package.json
- Configuration settings from YAML/JSON

## Example Output

```json
{
  "mcp_servers": [
    {
      "name": "my-server",
      "command": "python",
      "args": ["-m", "server"],
      "env_vars": {"API_KEY": "required"}
    }
  ],
  "env_vars": [
    {
      "name": "OPENAI_API_KEY",
      "value": "***MASKED***",
      "required": true
    }
  ],
  "dependencies": {
    "python": ["anthropic", "fastapi"],
    "node": {
      "dependencies": {"react": "^18.0.0"},
      "devDependencies": {"typescript": "~5.8.3"}
    }
  }
}
```

## Security Features

- Automatic masking of secrets (API keys, tokens, passwords)
- Detection of sensitive environment variables
- Safe parsing of configuration files
