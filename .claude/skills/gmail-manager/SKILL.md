---
name: gmail-manager
description: Comprehensive Gmail management with AI-powered email summarization, contact extraction, newsletter management, and draft generation
triggers:
  - gmail
  - email
  - inbox
  - summarize emails
  - newsletter
model: sonnet
---

# Gmail Manager Skill

Manage your Gmail inbox with AI assistance - summarize emails, extract contacts, manage newsletters, generate drafts, and more.

## Overview

This skill provides comprehensive Gmail management capabilities:
- **Mark as Read**: Bulk mark emails as read
- **Extract Contacts**: Archive unique email addresses and domains from inbox/sent
- **Summarize Emails**: AI-powered email summaries with action item extraction
- **Newsletter Management**: Detect, unsubscribe, or block newsletter senders
- **Draft Generation**: AI-generated email drafts and replies
- **Send Mail**: Send emails directly

## Setup Requirements

### 1. Google Cloud OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create or select a project
3. Enable the Gmail API
4. Configure OAuth consent screen:
   - User type: External
   - Add your email as a test user
   - Add scopes: `gmail.readonly`, `gmail.modify`, `gmail.compose`, `gmail.send`, `gmail.settings.basic`
5. Create OAuth credentials:
   - Type: **Desktop application**
   - Download JSON and save as `gmail_client_secret.json` in this skill directory

### 2. Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
ANTHROPIC_API_KEY=sk-ant-...
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=eyJ...
```

### 3. First-time Authentication

```bash
cd .claude/skills/gmail-manager
python scripts/main_workflow.py auth --credentials gmail_client_secret.json
```

This will open a browser for OAuth consent and save the token locally.

## Usage

### Extract Contacts

Extract unique email addresses and domains from your inbox or sent mail:

```bash
# From inbox
python scripts/main_workflow.py extract-contacts --source inbox --max 500

# From sent mail
python scripts/main_workflow.py extract-contacts --source sent --max 500
```

### Summarize Emails

Generate AI summaries of recent emails:

```bash
# Summarize unread emails
python scripts/main_workflow.py summarize --max 50

# Include read emails
python scripts/main_workflow.py summarize --max 100 --all
```

### Newsletter Management

```bash
# Detect newsletter senders
python scripts/main_workflow.py newsletters --detect

# Block a sender (auto-archive)
python scripts/main_workflow.py newsletters --block "sender@newsletter.com"

# Delete emails from sender
python scripts/main_workflow.py newsletters --block "sender@spam.com" --action trash
```

### Create Drafts

```bash
# New email draft
python scripts/main_workflow.py create-draft \
  --to "recipient@example.com" \
  --topic "Project update meeting" \
  --tone professional

# Reply to a message
python scripts/main_workflow.py reply \
  --message-id "abc123..." \
  --instructions "Politely decline the meeting"
```

### Send Email

```bash
python scripts/main_workflow.py send \
  --to "recipient@example.com" \
  --subject "Quick update" \
  --body "Hello, just wanted to follow up..."
```

### Mark as Read

```bash
# By query
python scripts/main_workflow.py mark-read --query "from:newsletter@example.com"

# By message IDs
python scripts/main_workflow.py mark-read --ids msg123 msg456
```

### View Statistics

```bash
python scripts/main_workflow.py stats
```

## Stored Data

Data is stored in Supabase tables:

- `gmail_contacts`: Unique email addresses with metadata
- `gmail_domains`: Unique domains with statistics
- `gmail_email_summaries`: AI-generated email summaries
- `gmail_filters`: Tracked Gmail filters created by this skill

## Capabilities Reference

| Capability | Command | Description |
|------------|---------|-------------|
| Auth | `auth` | Authenticate with Gmail |
| Extract Contacts | `extract-contacts` | Archive unique contacts/domains |
| Summarize | `summarize` | AI-summarize inbox emails |
| Detect Newsletters | `newsletters --detect` | Find newsletter senders |
| Block Sender | `newsletters --block` | Create filter to block/archive |
| Create Draft | `create-draft` | Generate AI email draft |
| Reply | `reply` | Generate AI reply draft |
| Send | `send` | Send an email |
| Mark Read | `mark-read` | Mark messages as read |
| Stats | `stats` | View statistics |

## Security Notes

- OAuth tokens are stored locally in `.tokens/gmail_oauth.pkl`
- Never commit credentials or tokens to version control
- The `.tokens` directory is gitignored
- Only request minimum necessary Gmail scopes
