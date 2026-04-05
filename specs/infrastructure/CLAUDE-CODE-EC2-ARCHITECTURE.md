# Claude Code EC2 Architecture Documentation

## Overview
Claude Code instance running on AWS Lightsail for automated consulting workflow and customer scope planning.

## Infrastructure Details

### Instance Information
- **Service**: AWS Lightsail (not EC2)
- **Instance Name**: `multi-agent-adw`
- **Type**: Ubuntu 22.04 on nano_3_0 plan
- **IP Address**: 44.208.161.19
- **Created**: October 20, 2025
- **Region**: us-east-1 (us-east-1a)
- **Monthly Cost**: ~$3.50/month

### Hardware Specs
- **vCPUs**: 2
- **RAM**: 0.5 GB
- **Disk**: 20 GB SSD (IOPS: 100)
- **Bandwidth**: 1024 GB/month

### Network Configuration
- **Private IP**: 172.26.14.88
- **Public IP**: 44.208.161.19
- **IPv6**: 2600:1f10:4658:f000:f33:5a2e:2680:66d
- **IP Type**: Dualstack (IPv4 + IPv6)

### Open Ports
- SSH (22): Open to public (0.0.0.0/0, ::/0)
- HTTP (80): Open to public (0.0.0.0/0, ::/0)
- ALL TCP (0-65535): Open to public (temporary for testing)

### Security
- **SSH Key**: LightsailDefaultKeyPair
- **Username**: ubuntu
- **Metadata Options**:
  - HTTP Tokens: optional
  - HTTP Endpoint: enabled
  - HTTP Put Response Hop Limit: 1
  - HTTP Protocol IPv6: disabled

## Claude Code Setup

### Installation Details
- **Installation Method**: unknown
- **Auto Updates**: Enabled
- **First Start**: October 21, 2025 03:40:43 UTC
- **User ID**: 33d557423bfa9d8ad76593a72117caf3cc92aa2963eea2ea28ea4a691ac92e50
- **Sonnet 4.5 Migration**: Complete

### Environment Configuration

**API Keys** (located in `/home/ubuntu/.env`):
```bash
ANTHROPIC_API_KEY=sk-ant-api03-YOUR_KEY_HERE
```

### Directory Structure

```
/home/ubuntu/
├── .claude/                          # Claude Code configuration
│   ├── commands/                     # Custom slash commands
│   ├── debug/                        # Debug logs (session-based)
│   │   └── latest -> [symlink to current session log]
│   ├── history.jsonl                 # Conversation history
│   ├── projects/                     # Project-specific settings
│   │   └── -home-ubuntu/            # Home directory project
│   ├── session-env/                  # Session environment data
│   │   ├── 716c7997-5926-448d-8af9-3fb42f1852a5/
│   │   └── fae8b337-c84b-4745-8ac3-7930ad94fac2/
│   ├── settings.json                 # User settings
│   ├── shell-snapshots/             # Shell environment snapshots
│   ├── statsig/                     # Feature flags/analytics
│   └── todos/                       # Task tracking data
├── .claude.json                      # Main configuration
├── .claude.json.backup              # Backup configuration
├── .env                             # Environment variables
├── .git/                            # Git repository
├── .gitconfig                       # Git configuration
├── .npm/                            # NPM cache
└── [various project directories]
    ├── adws/
    ├── agents/
    ├── apps/
    ├── tac8_app1__agent_layer_primitives/
    ├── tac8_app2__multi_agent_todone/
    ├── tac8_app3__out_loop_multi_agent_task_board/
    ├── tac8_app4__agentic_prototyping/
    └── tac8_app5__nlq_to_sql_aea/
```

### Features & Capabilities

**Enabled Features**:
- ✅ Skills system (managed, user, project)
- ✅ Plugin system (0 plugins currently installed)
- ✅ Auto-updates
- ✅ Session persistence
- ✅ Todo list tracking
- ✅ Shell snapshots (bash)
- ✅ Debug logging

**Tools Available**:
- Bash (command execution)
- Read/Write/Edit (file operations)
- Grep/Glob (code search)
- Task (subagent spawning)
- Skill (custom skills)
- SlashCommand (custom commands)
- Web search/fetch
- Git operations

### Logging & Monitoring

**Debug Logs Location**: `/home/ubuntu/.claude/debug/`
- Session-based log files (UUID named)
- Symlink to latest: `.claude/debug/latest`
- Captures: tool calls, hook events, API streams, shell snapshots

**Session Data**: `/home/ubuntu/.claude/session-env/[session-id]/`
- Environment variables per session
- Working directory state
- Tool execution context

**History**: `/home/ubuntu/.claude/history.jsonl`
- JSONL format conversation history
- Includes timestamps and project context

## Access Methods

### SSH Access
```bash
# Via WSL (recommended)
wsl bash -c "ssh -i /tmp/ls-default-key -o StrictHostKeyChecking=no ubuntu@44.208.161.19"

# Download key first
aws lightsail download-default-key-pair --output json
```

### Read Logs Remotely
```bash
# Latest debug log
ssh ubuntu@44.208.161.19 'cat .claude/debug/latest'

# Recent history
ssh ubuntu@44.208.161.19 'tail -50 .claude/history.jsonl'

# Running processes
ssh ubuntu@44.208.161.19 'ps aux | grep claude'
```

### API Integration
The instance has the Anthropic API key configured, allowing programmatic access to Claude Code sessions.

## Projects on Instance

Based on directory structure, the instance contains multiple AI agent projects:
1. **agent_layer_primitives** - Low-level agent building blocks
2. **multi_agent_todone** - Multi-agent task management system
3. **out_loop_multi_agent_task_board** - External-loop agent orchestration
4. **agentic_prototyping** - Agent prototype development
5. **nlq_to_sql_aea** - Natural language to SQL agent

## Cost Analysis

**Current AWS Costs (Monthly)**:
- Lightsail Instance: ~$3.50/month
- Data Transfer: Included (1TB/month)
- API Calls: Billed separately to Anthropic account

**Total Infrastructure**: ~$3.50/month

## Integration Points

### GitHub Integration
- Git configured with credentials helper: `git-cred-helper.sh`
- Git credentials file: `.git-credentials`
- Ready for repository operations

### Claude API
- Direct API key authentication
- Configured for production use
- Session persistence enabled

## Security Considerations

⚠️ **Current Issues**:
1. All TCP ports (0-65535) are currently open - should restrict to SSH/HTTP only
2. API key visible in plain text in `.env` file
3. No CloudWatch logging configured
4. No automated backups configured
5. Root-level API access (no IAM roles)

✅ **Recommended Improvements**:
1. Restrict firewall to only SSH (22) and required application ports
2. Use AWS Secrets Manager for API keys
3. Enable CloudWatch agent for log aggregation
4. Set up automated snapshots (Lightsail supports this)
5. Create read-only IAM user for monitoring

## Usage for Customer Planning Workflow

### Current State
- Claude Code is installed and configured
- API access is working
- Session persistence is enabled
- No active processes currently running

### Next Steps for Customer Workflow
1. Create a dedicated web service/API to interact with Claude Code
2. Set up input queue (SQS or similar) for customer questions
3. Create output storage (S3 or DynamoDB) for scope documents
4. Build approval workflow (Step Functions or custom)
5. Add monitoring and alerting (CloudWatch)

### Recommended Architecture
```
Customer Request → API Gateway → Lambda → Claude Code (Lightsail)
                                              ↓
                                    Generate Scope Document
                                              ↓
                                    S3 Storage + DynamoDB
                                              ↓
                                    Email/Notification to Customer
                                              ↓
                                    Approval Workflow
```

## Maintenance

### Backup Strategy
- Session data: `/home/ubuntu/.claude/`
- Project files: `/home/ubuntu/[projects]`
- Configuration: `.claude.json`, `.env`, `.gitconfig`

### Update Process
- Auto-updates enabled for Claude Code
- Manual Ubuntu updates: `sudo apt update && sudo apt upgrade`

### Monitoring
- No automated monitoring currently configured
- Manual checks via SSH
- AWS Lightsail console for basic metrics

## Troubleshooting

### Access Debug Logs
```bash
ssh ubuntu@44.208.161.19 'tail -f .claude/debug/latest'
```

### Check Session State
```bash
ssh ubuntu@44.208.161.19 'ls -la .claude/session-env/'
```

### View Recent Commands
```bash
ssh ubuntu@44.208.161.19 'cat .claude/history.jsonl | tail -10'
```

### Restart Instance
```bash
aws lightsail reboot-instance --instance-name multi-agent-adw
```

---

**Last Updated**: November 8, 2025
**Instance Status**: Running
**Claude Code Version**: 2.0.28
