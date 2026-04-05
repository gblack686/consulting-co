# /note-search Command

Search the Obsidian vault for notes matching a query.

## Usage

```
/note-search [query]
```

## Parameters

- `query` (required): The search query - can be:
  - Keywords or phrases
  - Tags (prefix with `#`)
  - Dates (ISO format: `2025-11-13`)
  - Combination of filters

## Examples

```bash
# Simple keyword search
/note-search authentication

# Search with tags
/note-search #architecture #aws

# Search by date range
/note-search date:2025-11-01..2025-11-13

# Search in specific folder
/note-search folder:Decisions lambda

# Combined search
/note-search #decision aws-lambda date:2025-11
```

## Behavior

When you run this command, Claude will:

1. Execute fuzzy search across:
   - Note titles
   - Note content
   - Tags
   - Frontmatter metadata
2. Rank results by relevance score
3. Display top results (default: 10) with:
   - Note title
   - Creation date
   - Relevant snippet
   - Tags
   - Match score
4. Offer to load any result into conversation context

## Search Filters

### Tag Filter
```bash
/note-search #tag-name
```

### Date Filter
```bash
# Exact date
/note-search date:2025-11-13

# Date range
/note-search date:2025-11-01..2025-11-13

# Relative dates
/note-search date:last-7-days
/note-search date:this-month
```

### Folder Filter
```bash
/note-search folder:Decisions
/note-search folder:Daily Notes
```

### Combined Filters
```bash
/note-search #architecture #aws folder:Decisions date:last-30-days lambda
```

## Configuration

Search settings are configured in:
```json
{
  "search": {
    "depth": 2,
    "maxResults": 10,
    "includeContent": true,
    "fuzzyThreshold": 0.3
  }
}
```

Located at: `.claude/skills/obsidian-vault/config/vault-settings.json`

## Output Example

```
Found 5 results for "authentication":

1. ⭐ ADR-012-Auth0-Integration.md (Nov 10, 2025) [Score: 0.95]
   Tags: #adr #architecture #authentication

   "...decided to use Auth0 for authentication instead of
   building custom solution. Factors: Time to market, security
   best practices, OAuth2/OIDC compliance..."

2. ⭐ Authentication-Flow-Design.md (Nov 5, 2025) [Score: 0.87]
   Tags: #learning #security #authentication

   "...JWT tokens stored in httpOnly cookies for maximum security.
   Refresh token rotation implemented to prevent token theft..."

[3 more results...]

Load any note with: /context-load [note-name]
```

## Related Commands

- `/note-create` - Create a new note
- `/context-load` - Load search result into context
- `/vault-sync` - Sync and re-index vault
- `/decision-log` - Create an architecture decision

## Performance

- **Small vaults** (< 1000 notes): < 100ms
- **Medium vaults** (1000-5000 notes): < 500ms
- **Large vaults** (> 5000 notes): < 2s

Search is optimized using:
- Fuzzy matching (Fuse.js)
- Indexed frontmatter
- Cached note metadata
- Incremental search

## Troubleshooting

### No Results Found
- Check spelling and try broader terms
- Verify vault is indexed: `/vault-sync`
- Check search threshold in config (lower = more fuzzy)

### Slow Search
- Reduce `searchDepth` in config
- Limit to specific folders
- Clear and rebuild index: `/vault-sync --rebuild`
