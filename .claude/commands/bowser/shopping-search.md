---
description: Search multiple shopping sites for a product, compare prices, and return a summary report
argument-hint: "<product description> [--budget <max_price>] [--sites amazon,ebay,newegg]"
---

# Shopping Search

Search multiple shopping sites for a product using agent-browser (headless WSL Playwright), extract prices and listings, and generate a comparison report.

## Variables

| Variable | Value | Description |
|----------|-------|-------------|
| AGENT | `agent-browser-agent` | Headless WSL browser via agent-browser |
| MODE | `headless` | No visible browser needed |
| DEFAULT_SITES | `amazon,ebay,newegg` | Sites to search |
| OUTPUT_DIR | `.claude/context/shopping` | Where reports are saved |

## Input Parsing

Parse the user's prompt to extract:
- **QUERY**: The product description (e.g., "mini PC 64GB DDR5 Ryzen")
- **BUDGET**: Optional max price from `--budget <N>` (default: no limit)
- **SITES**: Optional comma-separated list from `--sites <list>` (default: amazon,ebay,newegg)

## Workflow

### Phase 1: Setup

```bash
export AGENT_BROWSER_ARGS="--no-sandbox,--disable-dev-shm-usage"
DATE=$(date +%Y-%m-%d)
mkdir -p .claude/context/shopping
```

### Phase 2: Search Each Site

For each site in SITES, run the appropriate search:

#### Amazon
```bash
SEARCH_URL="https://www.amazon.com/s?k=$(echo "$QUERY" | sed 's/ /+/g')"
agent-browser open "$SEARCH_URL"
agent-browser wait --load networkidle
agent-browser scroll down 500
agent-browser wait 3000
RESULTS=$(agent-browser eval "JSON.stringify([...document.querySelectorAll('[data-component-type=\"s-search-result\"]')].slice(0, 10).map(el => ({title: el.querySelector('h2')?.innerText?.trim() || '', price: el.querySelector('.a-price .a-offscreen')?.innerText?.trim() || 'N/A', url: 'https://www.amazon.com' + (el.querySelector('h2 a')?.getAttribute('href') || ''), rating: el.querySelector('.a-icon-alt')?.innerText?.trim() || 'N/A'})))")
```

#### eBay
```bash
SEARCH_URL="https://www.ebay.com/sch/i.html?_nkw=$(echo "$QUERY" | sed 's/ /+/g')&_sop=15"
agent-browser open "$SEARCH_URL"
agent-browser wait --load networkidle
agent-browser scroll down 500
agent-browser wait 3000
RESULTS=$(agent-browser eval "JSON.stringify([...document.querySelectorAll('.s-item')].slice(1, 11).map(el => ({title: el.querySelector('.s-item__title')?.innerText?.trim() || '', price: el.querySelector('.s-item__price')?.innerText?.trim() || 'N/A', url: el.querySelector('.s-item__link')?.href || '', condition: el.querySelector('.SECONDARY_INFO')?.innerText?.trim() || 'N/A'})))")
```

#### Newegg
```bash
SEARCH_URL="https://www.newegg.com/p/pl?d=$(echo "$QUERY" | sed 's/ /+/g')"
agent-browser open "$SEARCH_URL"
agent-browser wait --load networkidle
agent-browser scroll down 500
agent-browser wait 3000
RESULTS=$(agent-browser eval "JSON.stringify([...document.querySelectorAll('.item-cell')].slice(0, 10).map(el => ({title: el.querySelector('.item-title')?.innerText?.trim() || '', price: el.querySelector('.price-current')?.innerText?.trim() || 'N/A', url: el.querySelector('.item-title')?.href || ''})))")
```

#### Facebook Marketplace
If `facebook` is in SITES (requires login — use `--session` with saved cookies):
```bash
SEARCH_URL="https://www.facebook.com/marketplace/search/?query=$(echo "$QUERY" | sed 's/ /+/g')&exact=false"
agent-browser --session fb-shop open "$SEARCH_URL"
agent-browser --session fb-shop wait --load networkidle
agent-browser --session fb-shop scroll down 500
agent-browser --session fb-shop wait 4000
RESULTS=$(agent-browser --session fb-shop eval "document.body.innerText")
```
Note: Facebook Marketplace requires authenticated session. Parse results from raw text.

### Phase 3: Decode and Filter

For each site's results:
1. Decode the JSON (double-decode: shell + eval encoding)
2. If BUDGET is set, filter out items with price > BUDGET
3. Sort by price ascending
4. Keep top 5 per site

```python
import json

def decode_results(raw):
    """Double-decode agent-browser eval output."""
    try:
        return json.loads(json.loads(raw))
    except (json.JSONDecodeError, TypeError):
        try:
            return json.loads(raw)
        except:
            return []

def filter_by_budget(items, budget):
    """Filter items by max price."""
    if not budget:
        return items
    filtered = []
    for item in items:
        price_str = item.get('price', 'N/A')
        try:
            price = float(price_str.replace('$', '').replace(',', '').split()[0])
            if price <= budget:
                filtered.append(item)
        except (ValueError, IndexError):
            filtered.append(item)  # keep items with unparseable prices
    return filtered
```

### Phase 4: Generate Report

Write a comparison report to `.claude/context/shopping/{DATE}-{sanitized_query}.md`:

```markdown
# Shopping Search: {QUERY}

**Date**: {DATE}
**Budget**: {BUDGET or "No limit"}
**Sites searched**: {SITES}

---

## Amazon

| # | Product | Price | Rating | Link |
|---|---------|-------|--------|------|
| 1 | {title} | {price} | {rating} | [View]({url}) |
...

## eBay

| # | Product | Price | Condition | Link |
|---|---------|-------|-----------|------|
| 1 | {title} | {price} | {condition} | [View]({url}) |
...

## Newegg

| # | Product | Price | Link |
|---|---------|-------|------|
| 1 | {title} | {price} | [View]({url}) |
...

---

## Best Deals

Top 5 across all sites sorted by price:

| Product | Price | Site | Link |
|---------|-------|------|------|
...
```

### Phase 5: Cleanup

```bash
agent-browser close-all
```

## Output

Report the top 3-5 best deals with prices and direct links. Save full report to `.claude/context/shopping/`.

## Error Handling

- If a site blocks the scrape (CAPTCHA, bot detection): skip that site, note in report
- If no results found on a site: note "No results" in report
- Always close agent-browser sessions, even on error
- Timeout per site: 30 seconds max
