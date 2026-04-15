# Active Listener

Before every response, check what has already been done in this pipeline run.

## Rules

1. **Read before acting.** Check which branches have been generated, which have validation reports, which are marked failed. Don't regenerate what already exists.

2. **Check status in trees.yaml.** Branch statuses (`planned`, `generating`, `validating`, `validated`, `failed`) tell you what's been done.

3. **Read validation reports.** Before reviewing or fixing, read the existing reports in `validation/` to understand what's already been flagged.

4. **Don't repeat work.** If a component exists and is marked `validated`, skip it.
