# GitHub Authentication Setup Guide

## Option 1: Personal Access Token (PAT) - Recommended for HTTPS

### Step 1: Create a Personal Access Token
1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Direct link: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a descriptive name (e.g., "Telegram Development")
4. Set expiration (choose "No expiration" for permanent access)
5. Select scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `workflow` (Update GitHub Action workflows)
6. Click "Generate token"
7. **IMPORTANT**: Copy the token immediately (you won't see it again!)

### Step 2: Configure Git to Store Credentials

#### Windows (Git Credential Manager):
```bash
# This stores credentials permanently in Windows Credential Manager
git config --global credential.helper manager-core

# Or use the newer version
git config --global credential.helper manager
```

#### Alternative - Store in Git Credential Store (plain text):
```bash
# Stores credentials in ~/.git-credentials file (plain text)
git config --global credential.helper store
```

### Step 3: Clone Repository with Token
```bash
# When you clone, you'll be prompted for username and password
git clone https://github.com/YOUR_USERNAME/REPO_NAME.git

# Username: your-github-username
# Password: paste-your-personal-access-token-here
```

### Step 4: One-Time Setup (Alternative - Embed Token in URL)
```bash
# Clone with token embedded (credentials cached forever)
git clone https://YOUR_TOKEN@github.com/YOUR_USERNAME/REPO_NAME.git

# Example:
# git clone https://ghp_abc123xyz789@github.com/johndoe/my-repo.git
```

---

## Option 2: SSH Keys - Most Secure & Permanent

### Step 1: Generate SSH Key
```bash
# Generate new SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Press Enter to accept default location (~/.ssh/id_ed25519)
# Optionally set a passphrase (or press Enter for none)
```

### Step 2: Add SSH Key to SSH Agent
```bash
# Start SSH agent
eval "$(ssh-agent -s)"

# Add your SSH private key
ssh-add ~/.ssh/id_ed25519
```

### Step 3: Add Public Key to GitHub
```bash
# Copy your public key to clipboard
cat ~/.ssh/id_ed25519.pub
# Manually copy the output

# Or on Windows with clip
cat ~/.ssh/id_ed25519.pub | clip
```

1. Go to GitHub → Settings → SSH and GPG keys
   - Direct link: https://github.com/settings/keys
2. Click "New SSH key"
3. Title: "Telegram Dev Machine" (or whatever you want)
4. Key type: Authentication Key
5. Paste the public key
6. Click "Add SSH key"

### Step 4: Test SSH Connection
```bash
# Test the connection
ssh -T git@github.com

# You should see: "Hi username! You've successfully authenticated..."
```

### Step 5: Clone with SSH
```bash
# Clone using SSH (no password needed ever)
git clone git@github.com:YOUR_USERNAME/REPO_NAME.git
```

---

## Option 3: GitHub CLI - Easiest for Beginners

### Step 1: Install GitHub CLI
```bash
# Check if already installed
gh --version

# If not installed, download from: https://cli.github.com/
```

### Step 2: Authenticate
```bash
# Login to GitHub
gh auth login

# Follow prompts:
# - Choose: GitHub.com
# - Protocol: HTTPS (or SSH)
# - Authenticate: Login with web browser (easiest)
```

### Step 3: Clone Repository
```bash
# Clone using gh CLI (auto-authenticated)
gh repo clone YOUR_USERNAME/REPO_NAME
```

---

## Quick Reference: Setting Up for This Project

### Recommended Approach for Telegram/Remote Work:

1. **Create PAT with no expiration** (Steps above)
2. **Store credentials globally**:
   ```bash
   git config --global credential.helper manager
   ```

3. **Clone with embedded token** (one-time setup):
   ```bash
   git clone https://YOUR_TOKEN@github.com/YOUR_USERNAME/3d-avatar-telegram.git
   ```

4. **Future pushes/pulls work automatically** - No re-authentication needed

---

## Troubleshooting

### If you get "Authentication failed":
```bash
# Clear stored credentials
git credential-cache exit

# Or remove from credential store
rm ~/.git-credentials

# Then clone again with fresh token
```

### If SSH key isn't working:
```bash
# Check if SSH agent has your key
ssh-add -l

# If not, add it again
ssh-add ~/.ssh/id_ed25519
```

### Check current credential helper:
```bash
git config --global credential.helper
```

---

## Security Best Practices

1. **Never commit tokens/keys to repositories**
2. **Use environment variables** for tokens in code:
   ```bash
   export GITHUB_TOKEN=your_token_here
   ```
3. **Rotate tokens periodically** if using PAT
4. **Use SSH keys** for maximum security (recommended for long-term)
5. **Add `.env` to `.gitignore`** to prevent accidental commits

---

## Next Steps After Authentication

Once authenticated, you can:
```bash
# Make changes
git add .
git commit -m "Your message"
git push origin main

# All without re-entering credentials!
```
