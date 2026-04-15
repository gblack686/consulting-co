# Tailscale Expertise — Mac Mini Serve & Funnel

## Quick Reference

| What | Command |
|------|---------|
| Binary path | `/Applications/Tailscale.app/Contents/MacOS/Tailscale` |
| `tailscale` not in PATH | Must use full path or `export PATH` first |
| Tailnet hostname | `gregs-mac-mini.tail4e0ac6.ts.net` |
| Public URL (Funnel) | `https://gregs-mac-mini.tail4e0ac6.ts.net/` |

## Commands

### Serve (tailnet only — requires Tailscale client)
```bash
/Applications/Tailscale.app/Contents/MacOS/Tailscale serve --bg --https=443 http://localhost:PORT
```

### Funnel (public internet — no Tailscale needed)
```bash
/Applications/Tailscale.app/Contents/MacOS/Tailscale funnel --bg --https=443 http://localhost:PORT
```

### Check status
```bash
/Applications/Tailscale.app/Contents/MacOS/Tailscale serve status
/Applications/Tailscale.app/Contents/MacOS/Tailscale funnel status
```

### Turn off
```bash
/Applications/Tailscale.app/Contents/MacOS/Tailscale funnel --https=443 off
/Applications/Tailscale.app/Contents/MacOS/Tailscale serve --https=PORT off
```

## Key Gotchas

1. **`tailscale` is NOT in PATH on Mac Mini** — always use full path `/Applications/Tailscale.app/Contents/MacOS/Tailscale`
2. **`serve` vs `funnel`**: `serve` = tailnet only (requires Tailscale client on viewer's device). `funnel` = public HTTPS (anyone with the URL can access)
3. **Switching from funnel to serve (or vice versa)**: setting one automatically removes the other for the same port
4. **Only HTTPS ports**: 443, 8443, 10000 are allowed for Funnel. Custom ports like 8000 are serve-only (tailnet)
5. **`--bg` flag**: runs in background. Without it, the command blocks the terminal
6. **Multiple paths on same port**: Use `--set-path` to add sub-paths (e.g., `/tui` → different backend)

## Current Port Mapping

| Tailscale Port | Backend | Service |
|---------------|---------|---------|
| :443 (Funnel) | localhost:3077 | Infinite UI (Vue gallery) |
| :8443 (Serve) | localhost:3051 + /tui→:7681 | Eagle Next.js + ttyd TUI |
| :8801 (Serve) | localhost:8800 | Claw Empire dashboard |

## Common Services on Mac Mini

| Service | Port | Notes |
|---------|------|-------|
| Infinite UI (Vite) | 3077 | Vue 3 gallery for reviewing generated UI |
| Eagle Next.js | 3051 | Main Eagle scaffold (needs backend for most routes) |
| Meridian SDK proxy | 3456 | Claude Code auth proxy (launchd) |
| Claude Bridge | 8077 | Pi → claude CLI shim (launchd) |
| Claw Empire | 8800 | Visual agent dashboard |
| ttyd TUI | 7681 | Web terminal |
