---
name: subscription-usage-checker
description: Check credits, usage, and costs across all subscriptions - Anthropic, ElevenLabs, AWS, OpenAI, Supabase, Gemini, and more. Use when user asks about remaining credits, API usage, billing, or subscription status.
---

# Subscription Usage Checker

## Overview

This skill provides comprehensive subscription and usage monitoring across multiple AI/cloud services:
- **Anthropic** - Claude API usage and costs
- **ElevenLabs** - Voice character credits and usage
- **AWS** - Cost Explorer billing data
- **OpenAI** - API usage and credits
- **Supabase** - Project usage and plan status
- **Google Gemini** - API usage and billing
- **Apify** - Actor run credits

## When to Use This Skill

Activate this skill when:
- User asks about remaining credits or usage
- Checking subscription status across services
- Monitoring API costs and billing
- Planning budget allocation for AI services
- Auditing service consumption

## Quick Start

### Check All Services
```bash
cd .claude/skills/subscription-usage-checker
python scripts/check_all.py
```

### Check Specific Service
```bash
python scripts/check_anthropic.py
python scripts/check_elevenlabs.py
python scripts/check_aws.py
python scripts/check_openai.py
python scripts/check_supabase.py
python scripts/check_gemini.py
```

### Generate Report
```bash
python scripts/check_all.py --format markdown --output usage_report.md
```

## Services Monitored

### 1. Anthropic (Claude API)
- Monthly usage and costs
- Token consumption by model
- Rate limits and quotas
- Claude Code Max plan status

**Endpoint:** `https://api.anthropic.com/v1/usage`

### 2. ElevenLabs (Voice AI)
- Character credits remaining
- Monthly character usage
- Subscription tier
- Voice clone slots

**Endpoint:** `https://api.elevenlabs.io/v1/user/subscription`

### 3. AWS (Cloud Services)
- Month-to-date costs
- Cost breakdown by service
- Cost forecast
- Budget alerts

**Uses:** AWS Cost Explorer API

### 4. OpenAI (GPT API)
- Usage by model
- Monthly spend
- Rate limits
- Organization quotas

**Endpoint:** `https://api.openai.com/v1/usage`

### 5. Supabase (Backend)
- Database storage used
- Bandwidth consumption
- Edge function invocations
- Plan limits

**Endpoint:** Supabase Management API

### 6. Google Gemini
- API call count
- Token usage
- Billing status
- Quota limits

**Endpoint:** Google Cloud Billing API

### 7. Apify (Web Scraping)
- Actor run credits
- Monthly usage
- Platform credits remaining

**Endpoint:** `https://api.apify.com/v2/users/me`

## Configuration

Create `config/services.json`:

```json
{
  "anthropic": {
    "enabled": true,
    "api_key_source": "aws_secrets",
    "secret_name": "gbautomation/core/anthropic-api-key"
  },
  "elevenlabs": {
    "enabled": true,
    "api_key_source": "aws_secrets",
    "secret_name": "revstar/shared/elevenlabs"
  },
  "aws": {
    "enabled": true,
    "profile": "default",
    "accounts": ["274487662938"]
  },
  "openai": {
    "enabled": true,
    "api_key_source": "aws_secrets",
    "secret_name": "gbautomation/core/openai-api-key"
  },
  "supabase": {
    "enabled": true,
    "access_token_source": "env",
    "env_var": "SUPABASE_ACCESS_TOKEN"
  },
  "gemini": {
    "enabled": true,
    "credentials_source": "gcloud"
  },
  "apify": {
    "enabled": true,
    "api_key_source": "aws_secrets",
    "secret_name": "gbautomation/core/apify-api-token"
  }
}
```

## Output Formats

### Console (Default)
```
╭──────────────────────────────────────────────────────────╮
│           Subscription Usage Report - 2026-01-15         │
╰──────────────────────────────────────────────────────────╯

┌─────────────┬──────────────┬───────────┬─────────────────┐
│ Service     │ Used         │ Remaining │ Status          │
├─────────────┼──────────────┼───────────┼─────────────────┤
│ Anthropic   │ $45.23       │ $54.77    │ ⚠️ 55% used     │
│ ElevenLabs  │ 125,432 char │ 374,568   │ ✅ 25% used     │
│ AWS         │ $127.89      │ N/A       │ ℹ️ MTD          │
│ OpenAI      │ $12.50       │ $87.50    │ ✅ 12% used     │
│ Supabase    │ 2.1 GB       │ 7.9 GB    │ ✅ Free tier    │
│ Gemini      │ 50,000 req   │ Unlimited │ ✅ Active       │
│ Apify       │ 45 runs      │ 55 runs   │ ⚠️ 45% used     │
└─────────────┴──────────────┴───────────┴─────────────────┘
```

### Markdown Report
Generates a detailed markdown report with:
- Summary table
- Per-service breakdown
- Historical trends (if available)
- Recommendations

### JSON Export
```bash
python scripts/check_all.py --format json --output usage.json
```

## Scripts Reference

### scripts/check_all.py
Main orchestrator script that checks all enabled services.

```bash
# Options
--format [console|markdown|json]  # Output format
--output FILE                     # Save to file
--services SERVICE1,SERVICE2      # Check specific services only
--quiet                           # Minimal output
--verbose                         # Detailed output
```

### scripts/check_anthropic.py
```bash
# Check Anthropic API usage
python scripts/check_anthropic.py

# With date range
python scripts/check_anthropic.py --start 2026-01-01 --end 2026-01-15
```

### scripts/check_elevenlabs.py
```bash
# Check ElevenLabs subscription
python scripts/check_elevenlabs.py

# Show voice list
python scripts/check_elevenlabs.py --show-voices
```

### scripts/check_aws.py
```bash
# Check AWS costs (uses existing aws-config-manager)
python scripts/check_aws.py

# By service
python scripts/check_aws.py --by-service

# Forecast
python scripts/check_aws.py --forecast
```

### scripts/check_openai.py
```bash
# Check OpenAI usage
python scripts/check_openai.py

# By model
python scripts/check_openai.py --by-model
```

### scripts/check_supabase.py
```bash
# Check Supabase usage
python scripts/check_supabase.py

# Specific project
python scripts/check_supabase.py --project-ref unickqnwfheaczccvgbw
```

### scripts/check_gemini.py
```bash
# Check Gemini API usage
python scripts/check_gemini.py
```

## Credential Sources

The skill supports multiple credential sources:

1. **AWS Secrets Manager** (Recommended)
   - Secrets stored at `gbautomation/core/*`
   - Uses boto3 with default credentials

2. **Environment Variables**
   - Set `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, etc.

3. **Config File**
   - Store in `config/credentials.json` (gitignored)

## Alert Thresholds

Configure usage alerts in `config/alerts.json`:

```json
{
  "anthropic": {
    "warn_percent": 50,
    "critical_percent": 80
  },
  "elevenlabs": {
    "warn_percent": 60,
    "critical_percent": 85
  },
  "aws": {
    "warn_amount": 100,
    "critical_amount": 200
  }
}
```

## Dependencies

```txt
boto3>=1.34.0
requests>=2.31.0
rich>=13.0.0
click>=8.0.0
python-dateutil>=2.8.0
google-cloud-billing>=1.0.0
```

Install:
```bash
pip install -r requirements.txt
```

## Security

- API keys are retrieved from AWS Secrets Manager by default
- No credentials are stored in code or config files
- All API calls use HTTPS
- Sensitive data is masked in output

## Version

**Version:** 1.0.0
**Created:** January 15, 2026
