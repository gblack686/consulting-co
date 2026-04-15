# Mental Model

You maintain a personal expertise file that captures patterns and lessons learned during this pipeline run.

## Rules

1. **Update after each branch.** After generating or fixing a component, note any reusable patterns, tricky decisions, or things that worked well.

2. **Read before starting.** Check your expertise file for patterns from previous branches that apply to the current one.

3. **Keep it compact.** Max 200 lines. Use YAML format with keys like `patterns`, `decisions`, `reusable_snippets`.

4. **Share across branches.** If you discovered a good way to implement the compliance alert card in branch A, reference it when generating branch B.

## File Location

Your expertise file is at: `agents/expertise/{your-role}-patterns.yaml`
