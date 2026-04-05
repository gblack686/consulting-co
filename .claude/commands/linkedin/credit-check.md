---
description: Check remaining LinkedIn InMail credits, connection limits, and subscription status
argument-hint:
---

# LinkedIn Credit Check

Navigate to LinkedIn settings/subscription page and report current credit balances.

## Variables

| Variable | Value | Description |
|----------|-------|-------------|
| SKILL | `claude-bowser` | Uses real Chrome (already logged in to LinkedIn) |
| MODE | `headed` | Visible browser |

## Workflow

1. Navigate to `https://www.linkedin.com/mypreferences/d/categories/account`
2. Wait for the page to load
3. Take a snapshot
4. Look for subscription type (Premium Business, Sales Navigator, etc.)
5. Navigate to `https://www.linkedin.com/messaging/` and check for InMail credit indicator
6. Take a snapshot
7. Navigate to `https://www.linkedin.com/mynetwork/invitation-manager/sent/`
8. Wait for the page to load
9. Take a snapshot — count pending connection requests
10. Navigate to `https://www.linkedin.com/me/profile-views/`
11. Take a snapshot — note viewer count for the week
12. Report all findings

## Report Format

```markdown
## LinkedIn Credit Report — {date}

### Subscription
- Type: {Premium Business / Sales Navigator / etc.}
- Status: {Active / Expiring on...}

### InMail Credits
- Available: {N}
- Used this month: {estimated}
- Monthly allocation: {15 for Premium / 50 for Sales Nav}
- Banked: {if visible}

### Connection Requests
- Pending sent: {N}
- Weekly limit remaining: ~{estimate based on LinkedIn's ~100/week soft cap}

### Profile Views
- Viewers this week: {N}
- Notable viewers (high fit): {list any ICP matches}

### Recommendation
{Based on credits remaining and days left in month, suggest how aggressively to campaign}
```

## Notes

- This skill uses NO credits — it's read-only
- Run this BEFORE any campaign to know your budget
- Run this AFTER campaigns to verify credit consumption
- LinkedIn doesn't always show exact credit counts — estimates are noted as such
