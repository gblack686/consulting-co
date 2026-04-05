---
name: client-linkedin
description: "Quick LinkedIn professional overview for GBAutomation consulting. Navigates to LinkedIn profile via Chrome DevTools MCP, extracts headline/role/career/education/recommendations, and produces a tight markdown snapshot + 3-slide PowerPoint summary. Fast execution — under 5 minutes. Invoke with 'linkedin overview', 'linkedin profile', 'quick linkedin', 'pull their linkedin'."
model: sonnet
color: blue
---

# Client LinkedIn Skill

Quick professional snapshot from LinkedIn. In and out — headline, career arc, education, and recommendations. No fluff. Designed to be run before a session when you just need the professional baseline fast.

## When to Use

- Before a call when you want fast professional context
- When user says "linkedin overview", "pull their linkedin", "quick linkedin check"
- As Phase 1 before running `/client-personal-intel` for the full picture

## What You Produce

1. **Screenshots** — `profile-header.png`, `experience.png`, `education.png` → saved to `.claude/context/clients/{slug}/`
2. **Markdown snapshot** — `.claude/context/clients/{slug}/linkedin-profile.md`
3. **PowerPoint summary** — 3-slide deck: Overview → Career Timeline → Key Takeaways

## Prerequisites

- **Chrome DevTools MCP** must be connected (headed browser)
- **LinkedIn** must be logged in in the MCP Chrome profile (`C:\Users\gblac\.cache\chrome-devtools-mcp\chrome-profile`)
- If MCP errors with "browser already running" → ask user to close the Chrome window using that profile, then retry

---

## Pipeline

### Phase 1: Inputs

Collect from user:
- **Name** (required)
- **LinkedIn URL** (preferred) — skip search entirely if provided
- **Identifiers** (if no URL) — company, school, location

### Phase 2: Navigate to Profile

If URL provided:
1. Navigate directly to the LinkedIn profile URL

If no URL:
1. Navigate to `https://www.linkedin.com/search/results/all/?keywords={name}+{company}`
2. Screenshot → `search-results.png`
3. Take a11y snapshot, find the best match, navigate to it

### Phase 3: Extract Profile Data

1. Navigate to profile
2. Screenshot viewport → `profile-header.png`
3. Take a11y snapshot and extract:

| Field | Extract |
|---|---|
| Full name | Profile heading |
| Headline | Below name |
| Location | Location line |
| Current title + company | First experience entry |
| Connection degree | "1st", "2nd", "3rd" |
| Mutual connections | Count + names if shown |
| Services offered | Services section (if present) |

4. Scroll to experience section → screenshot `experience.png`
   - Extract ALL roles: company, title, dates, duration, key description bullets
5. Scroll to education → screenshot `education.png`
   - Extract: schools, degrees, fields, dates
6. Scroll to recommendations → extract received recommendations (name, role, full text)
7. Note top skills if visible

### Phase 4: Generate Outputs

#### Markdown Snapshot

Save to `.claude/context/clients/{slug}/linkedin-profile.md`:

```markdown
# LinkedIn Profile: {Full Name}

**Researched**: {date}
**LinkedIn**: {url}

---

## Summary

| Field | Value |
|---|---|
| Name | {name} |
| Headline | {headline} |
| Location | {location} |
| Current Role | {title} at {company} |
| Connection | {degree} |

## Career Timeline

### {Title} — {Company}
- **Dates**: {dates} ({duration})
- **Location**: {location}
- **Key points**: {bullets from description}

[... all roles ...]

## Education

| School | Degree | Field | Dates |
|---|---|---|---|
| {school} | {degree} | {field} | {dates} |

## Recommendations Received

**{Name}** — {Title}, {Company}
> "{quote}"

## Top Skills

{list}

## Key Professional Takeaways

1. {career arc narrative}
2. {domain expertise they bring}
3. {connection point with Greg / GBAutomation}
4. {automation/AI opportunity visible from their work history}
```

#### PowerPoint (3 slides)

Generate using `python-pptx`. GBAutomation colors: cream `#F3F1E7`, terracotta `#D97757`.

| Slide | Content |
|---|---|
| 1 | **Overview** — name, headline, current role, location, connection degree, LinkedIn URL |
| 2 | **Career Timeline** — all roles chronological with company, title, dates |
| 3 | **Key Takeaways** — 4-5 professional insights + 3 conversation starters from career arc |

Save as `.claude/context/clients/{slug}/{Name} - LinkedIn.pptx`

---

## Error Handling

- **LinkedIn not logged in** → Tell user to open Chrome, log in manually, then retry
- **2FA triggered** → Wait for user to approve, then continue
- **Profile not found** → Show search results, ask user to pick the right one
- **Chrome conflict** → Ask user to close the MCP Chrome window, then retry

---

## Usage Examples

```
/client-linkedin Patrick Bauer — Acquisition.com
/client-linkedin https://www.linkedin.com/in/patrick-bauer-86a29527/
quick linkedin on Jason Diaz before his session
```
