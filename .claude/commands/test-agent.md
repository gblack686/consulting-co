# Test Agent Prompts

Generate test prompts for any agent expert and capture the results in an isolated file with timestamps.

## Usage
```
/test-agent [agent_path] [num_prompts]
```

## Parameters
- **agent_path**: Path to the expert directory (absolute or relative)
  - Examples:
    - `AI-Agent-KB/07-Experts/tac`
    - `AI-Agent-KB/07-Experts/adw`
    - `.claude/commands/experts/database`
    - `C:/Users/gblac/OneDrive/Desktop/obsidian/Gbautomation/AI-Agent-KB/07-Experts/tac`
- **num_prompts**: Number of test prompts to generate (default: 5)

## Workflow

1. **Identify the Expert**
   - Read `{agent_path}/_index.md` to understand its domain
   - Read `{agent_path}/expertise.md` to understand its capabilities
   - Read `{agent_path}/question.md` to understand query categories

2. **Generate Diverse Test Prompts**
   - Create prompts across different categories the expert supports
   - Mix difficulty levels (basic, intermediate, advanced)
   - Include framework questions, pattern questions, how-to questions

3. **Execute Each Prompt**
   - Simulate running `/experts:{expert_name}:question [prompt]`
   - Capture the response based on expert knowledge

4. **Save Results**
   - Output file: `{agent_path}/tests/test_{YYYYMMDD_HHMMSS}.md`
   - Creates `tests/` subdirectory within the agent's directory
   - Include timestamp, prompt, and full response for each

## Output Format

```markdown
# {Expert Name} Expert - Test Prompts

**Generated**: {YYYY-MM-DD HH:MM:SS}
**Agent Path**: {agent_path}
**Command**: `.claude/commands/test-agent.md`
**Source Files**: {list of files read}

---

## Prompt 1: {Category}

**Question**: {prompt}

**Response**:
{full response}

**Source Files Referenced**:
- {source 1}
- {source 2}

---

## Prompt 2: {Category}
...
```

## Examples

```
/test-agent AI-Agent-KB/07-Experts/tac 5
```
Generates 5 test prompts for the TAC expert covering tactics, frameworks, patterns, ADWs, and projects.

```
/test-agent .claude/commands/experts/database 3
```
Generates 3 test prompts for the database expert.

```
/test-agent C:/Users/gblac/OneDrive/Desktop/obsidian/Gbautomation/AI-Agent-KB/07-Experts/adw
```
Generates 5 test prompts (default) for the ADW expert using absolute path.
