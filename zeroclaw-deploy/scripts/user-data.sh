#!/bin/bash
set -euo pipefail
exec > /var/log/zeroclaw-setup.log 2>&1

echo "=== ZeroClaw bootstrap starting ==="

# 1. Download pre-built ZeroClaw binary
ZEROCLAW_VERSION="v0.1.7"
ARCH="x86_64-unknown-linux-gnu"
cd /tmp
curl -fsSL "https://github.com/zeroclaw-labs/zeroclaw/releases/download/${ZEROCLAW_VERSION}/zeroclaw-${ARCH}.tar.gz" -o zeroclaw.tar.gz
tar xzf zeroclaw.tar.gz
mv zeroclaw /usr/local/bin/zeroclaw
chmod +x /usr/local/bin/zeroclaw
rm zeroclaw.tar.gz
echo "=== ZeroClaw binary installed ==="

# 2. Create workspace dirs
mkdir -p /home/ubuntu/.zeroclaw/workspace/skills

# 3. Write config.toml
cat > /home/ubuntu/.zeroclaw/config.toml << 'CONFIGEOF'
${CONFIG_TOML}
CONFIGEOF
echo "=== config.toml written ==="

# 4. Write workspace files
${WORKSPACE_HEREDOCS}
echo "=== Workspace files written ==="

# 5. Write skills
${SKILL_HEREDOCS}
echo "=== Skills written ==="

# 6. Fix ownership
chown -R ubuntu:ubuntu /home/ubuntu/.zeroclaw

# 7. Create systemd service for ZeroClaw gateway
cat > /etc/systemd/system/zeroclaw.service << 'SVCEOF'
[Unit]
Description=ZeroClaw Gateway
After=network.target

[Service]
Type=simple
User=ubuntu
ExecStart=/usr/local/bin/zeroclaw gateway
Restart=always
RestartSec=3
Environment=HOME=/home/ubuntu

[Install]
WantedBy=multi-user.target
SVCEOF
echo "=== zeroclaw.service created ==="

# 8. Install Node.js 22 (for customer-gateway-proxy)
curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
apt-get install -y nodejs
echo "=== Node.js installed: $(node --version) ==="

# 9. Deploy customer-gateway-proxy
mkdir -p /opt/gateway-proxy

cat > /opt/gateway-proxy/server.js << 'PROXYJS_EOF'
${PROXY_SERVER_JS}
PROXYJS_EOF

cat > /opt/gateway-proxy/package.json << 'PROXYPKG_EOF'
${PROXY_PACKAGE_JSON}
PROXYPKG_EOF

cat > /opt/gateway-proxy/tokens.json << 'TOKENS_EOF'
${TOKENS_JSON}
TOKENS_EOF

cd /opt/gateway-proxy && npm install --production
chown -R ubuntu:ubuntu /opt/gateway-proxy
echo "=== Gateway proxy deployed ==="

# 10. Create systemd service for proxy
cat > /etc/systemd/system/gateway-proxy.service << 'PROXYEOF'
[Unit]
Description=Customer Gateway Proxy
After=zeroclaw.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/gateway-proxy
ExecStart=/usr/bin/node server.js
Restart=always
RestartSec=3
Environment=ZEROCLAW_WS_URL=ws://127.0.0.1:18789
Environment=ZEROCLAW_AUTH_TOKEN=${GATEWAY_TOKEN}
Environment=PORT=3050

[Install]
WantedBy=multi-user.target
PROXYEOF

# 11. Enable and start services
systemctl daemon-reload
systemctl enable zeroclaw gateway-proxy
systemctl start zeroclaw
sleep 2
systemctl start gateway-proxy

echo "=== ZeroClaw bootstrap complete ==="
echo "=== Services status ==="
systemctl status zeroclaw --no-pager || true
systemctl status gateway-proxy --no-pager || true
