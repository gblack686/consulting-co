import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as s3deploy from 'aws-cdk-lib/aws-s3-deployment';
import { Construct } from 'constructs';
import * as fs from 'fs';
import * as path from 'path';
import * as crypto from 'crypto';

export interface ZeroClawStackProps extends cdk.StackProps {
  client: string;
  openrouterKey: string;
  gatewayToken?: string;
  modelTier?: 'cheap' | 'mid' | 'pro';
}

const MODEL_TIERS: Record<string, string> = {
  cheap: 'deepseek/deepseek-chat',
  mid: 'google/gemini-2.0-flash-001',
  pro: 'google/gemini-2.5-pro-preview',
};

export class ZeroClawStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: ZeroClawStackProps) {
    super(scope, id, props);

    const { client, openrouterKey, modelTier = 'cheap' } = props;
    const gatewayToken = props.gatewayToken || crypto.randomUUID();
    const defaultModel = MODEL_TIERS[modelTier] || MODEL_TIERS.cheap;

    // --- Build config.toml from template ---
    const configTemplate = fs.readFileSync(
      path.join(__dirname, '..', 'config', 'config.toml.tmpl'),
      'utf8'
    );
    const configToml = configTemplate
      .replace(/\$\{OPENROUTER_API_KEY\}/g, openrouterKey)
      .replace(/\$\{DEFAULT_MODEL\}/g, defaultModel)
      .replace(/\$\{GATEWAY_TOKEN\}/g, gatewayToken)
      .replace(/\$\{CLIENT_NAME\}/g, client);

    // --- Build tokens.json ---
    const tokensJson = JSON.stringify({
      [gatewayToken]: {
        customerId: client,
        createdAt: new Date().toISOString(),
        expiresAt: null,
      },
    }, null, 2);

    // --- Stage bundle directory ---
    const stageDir = path.join(__dirname, '..', '.stage', client);
    fs.mkdirSync(path.join(stageDir, 'workspace', 'skills'), { recursive: true });
    fs.mkdirSync(path.join(stageDir, 'proxy'), { recursive: true });

    // Write config.toml
    fs.writeFileSync(path.join(stageDir, 'config.toml'), configToml.replace(/\r\n/g, '\n'));

    // Copy workspace files
    const workspaceDir = path.join(__dirname, '..', 'workspace');
    for (const f of fs.readdirSync(workspaceDir)) {
      if (!fs.statSync(path.join(workspaceDir, f)).isFile()) continue;
      const content = fs.readFileSync(path.join(workspaceDir, f), 'utf8');
      fs.writeFileSync(path.join(stageDir, 'workspace', f), content.replace(/\r\n/g, '\n'));
    }

    // Copy skill files
    const skillsDir = path.join(__dirname, '..', 'skills');
    for (const d of fs.readdirSync(skillsDir)) {
      const skillPath = path.join(skillsDir, d, 'SKILL.md');
      if (fs.existsSync(skillPath)) {
        fs.mkdirSync(path.join(stageDir, 'workspace', 'skills', d), { recursive: true });
        const content = fs.readFileSync(skillPath, 'utf8');
        fs.writeFileSync(
          path.join(stageDir, 'workspace', 'skills', d, 'SKILL.md'),
          content.replace(/\r\n/g, '\n')
        );
      }
    }

    // Copy proxy files
    const proxyDir = path.join(__dirname, '..', 'proxy');
    for (const f of ['server.js', 'package.json']) {
      const content = fs.readFileSync(path.join(proxyDir, f), 'utf8');
      fs.writeFileSync(path.join(stageDir, 'proxy', f), content.replace(/\r\n/g, '\n'));
    }
    fs.writeFileSync(path.join(stageDir, 'proxy', 'tokens.json'), tokensJson.replace(/\r\n/g, '\n'));

    // --- S3 bucket for config bundle ---
    const bucket = new s3.Bucket(this, 'BundleBucket', {
      bucketName: `zeroclaw-bundle-${client}-${this.account}`,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
    });

    new s3deploy.BucketDeployment(this, 'BundleDeploy', {
      sources: [s3deploy.Source.asset(stageDir)],
      destinationBucket: bucket,
      destinationKeyPrefix: 'bundle',
    });

    // --- VPC (default) ---
    const vpc = ec2.Vpc.fromLookup(this, 'DefaultVpc', { isDefault: true });

    // --- Security Group ---
    const sg = new ec2.SecurityGroup(this, 'ZeroClawSG', {
      vpc,
      description: `ZeroClaw gateway for ${client}`,
      allowAllOutbound: true,
    });
    sg.addIngressRule(ec2.Peer.anyIpv4(), ec2.Port.tcp(22), 'SSH');
    sg.addIngressRule(ec2.Peer.anyIpv4(), ec2.Port.tcp(3050), 'Gateway proxy');
    sg.addIngressRule(ec2.Peer.anyIpv4(), ec2.Port.tcp(18789), 'ZeroClaw gateway');

    // --- IAM Role (S3 read for bundle + SSM for Session Manager) ---
    const role = new iam.Role(this, 'ZeroClawRole', {
      assumedBy: new iam.ServicePrincipal('ec2.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonSSMManagedInstanceCore'),
      ],
    });
    bucket.grantRead(role);

    // --- User Data ---
    const userData = ec2.UserData.forLinux();
    userData.addCommands(
      '#!/bin/bash',
      'set -euo pipefail',
      'exec > /var/log/zeroclaw-setup.log 2>&1',
      'echo "=== ZeroClaw bootstrap starting ==="',
      '',
      '# 1. System deps + AWS CLI v2',
      'apt-get update -qq',
      'apt-get install -y -qq unzip curl',
      'curl -fsSL "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o /tmp/awscliv2.zip',
      'unzip -q /tmp/awscliv2.zip -d /tmp',
      '/tmp/aws/install',
      'rm -rf /tmp/awscliv2.zip /tmp/aws',
      '',
      '# 2. Download ZeroClaw binary',
      'ZEROCLAW_VERSION="v0.1.7"',
      'cd /tmp',
      'curl -fsSL "https://github.com/zeroclaw-labs/zeroclaw/releases/download/${ZEROCLAW_VERSION}/zeroclaw-x86_64-unknown-linux-gnu.tar.gz" -o zeroclaw.tar.gz',
      'tar xzf zeroclaw.tar.gz',
      'mv zeroclaw /usr/local/bin/zeroclaw',
      'chmod +x /usr/local/bin/zeroclaw',
      'rm zeroclaw.tar.gz',
      'echo "=== ZeroClaw binary installed ==="',
      '',
      '# 3. Download bundle from S3',
      `BUCKET="${bucket.bucketName}"`,
      'mkdir -p /home/ubuntu/.zeroclaw /opt/gateway-proxy',
      'aws s3 cp s3://$BUCKET/bundle/config.toml /home/ubuntu/.zeroclaw/config.toml',
      'aws s3 cp --recursive s3://$BUCKET/bundle/workspace/ /home/ubuntu/.zeroclaw/workspace/',
      'aws s3 cp --recursive s3://$BUCKET/bundle/proxy/ /opt/gateway-proxy/',
      'chown -R ubuntu:ubuntu /home/ubuntu/.zeroclaw',
      'echo "=== Bundle downloaded from S3 ==="',
      '',
      '# 4. ZeroClaw systemd service',
      'cat > /etc/systemd/system/zeroclaw.service << SVCEOF',
      '[Unit]',
      'Description=ZeroClaw Gateway',
      'After=network.target',
      '',
      '[Service]',
      'Type=simple',
      'User=ubuntu',
      'ExecStart=/usr/local/bin/zeroclaw daemon',
      'Restart=always',
      'RestartSec=3',
      'Environment=HOME=/home/ubuntu',
      `Environment=OPENROUTER_API_KEY=${openrouterKey}`,
      `Environment=ZEROCLAW_API_KEY=${openrouterKey}`,
      '',
      '[Install]',
      'WantedBy=multi-user.target',
      'SVCEOF',
      '',
      '# 5. Install Node.js 22',
      'curl -fsSL https://deb.nodesource.com/setup_22.x | bash -',
      'apt-get install -y nodejs',
      'echo "=== Node.js installed: $(node --version) ==="',
      '',
      '# 6. Install agent-browser globally',
      'npm install -g agent-browser',
      'echo "=== agent-browser installed: $(agent-browser --version 2>/dev/null || echo unknown) ==="',
      '',
      '# 7. Install Chromium deps for agent-browser headless (Ubuntu 24.04)',
      'apt-get install -y -qq libnss3 libatk1.0-0t64 libatk-bridge2.0-0t64 libcups2t64 \\',
      '  libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libgbm1 \\',
      '  libpango-1.0-0 libasound2t64 libxshmfence1 fonts-liberation xdg-utils || \\',
      '  apt-get install -y -qq libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 \\',
      '    libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libgbm1 \\',
      '    libpango-1.0-0 libasound2 libxshmfence1 fonts-liberation xdg-utils',
      '# Let agent-browser download its own Chromium on first run',
      'su - ubuntu -c "agent-browser --version" || true',
      'echo "=== Chromium deps installed ==="',
      '',
      '# 8. Install proxy dependencies',
      'cd /opt/gateway-proxy && npm install --production',
      'chown -R ubuntu:ubuntu /opt/gateway-proxy',
      '',
      '# 9. Gateway proxy systemd service',
      'cat > /etc/systemd/system/gateway-proxy.service << PROXYEOF',
      '[Unit]',
      'Description=Customer Gateway Proxy',
      'After=zeroclaw.service',
      '',
      '[Service]',
      'Type=simple',
      'User=ubuntu',
      'WorkingDirectory=/opt/gateway-proxy',
      'ExecStart=/usr/bin/node server.js',
      'Restart=always',
      'RestartSec=3',
      'Environment=ZEROCLAW_WS_URL=ws://127.0.0.1:18789/ws/chat',
      `Environment=ZEROCLAW_AUTH_TOKEN=${gatewayToken}`,
      'Environment=PORT=3050',
      '',
      '[Install]',
      'WantedBy=multi-user.target',
      'PROXYEOF',
      '',
      '# 10. Enable and start services',
      'systemctl daemon-reload',
      'systemctl enable zeroclaw gateway-proxy',
      'systemctl start zeroclaw',
      'sleep 2',
      'systemctl start gateway-proxy',
      '',
      'echo "=== ZeroClaw bootstrap complete ==="',
    );

    // --- EC2 Instance ---
    const instance = new ec2.Instance(this, 'ZeroClawInstance', {
      vpc,
      instanceType: ec2.InstanceType.of(ec2.InstanceClass.T3, ec2.InstanceSize.MEDIUM),
      machineImage: ec2.MachineImage.genericLinux({
        'us-east-1': 'ami-0071174ad8cbb9e17', // Ubuntu 24.04 (GLIBC 2.39+)
      }),
      securityGroup: sg,
      role,
      userData,
      blockDevices: [{
        deviceName: '/dev/sda1',
        volume: ec2.BlockDeviceVolume.ebs(20, {
          volumeType: ec2.EbsDeviceVolumeType.GP3,
        }),
      }],
      userDataCausesReplacement: true,
    });

    cdk.Tags.of(instance).add('Name', `zeroclaw-${client}`);
    cdk.Tags.of(instance).add('Project', 'zeroclaw');
    cdk.Tags.of(instance).add('Client', client);

    // --- Elastic IP ---
    const eip = new ec2.CfnEIP(this, 'ZeroClawEIP', {
      tags: [{ key: 'Name', value: `zeroclaw-${client}-eip` }],
    });

    new ec2.CfnEIPAssociation(this, 'ZeroClawEIPAssoc', {
      allocationId: eip.attrAllocationId,
      instanceId: instance.instanceId,
    });

    // --- Outputs ---
    new cdk.CfnOutput(this, 'PublicIp', {
      value: eip.attrPublicIp,
      description: 'ZeroClaw instance public IP',
    });

    new cdk.CfnOutput(this, 'InstanceId', {
      value: instance.instanceId,
      description: 'EC2 instance ID (for SSM Session Manager)',
    });

    new cdk.CfnOutput(this, 'GatewayToken', {
      value: gatewayToken,
      description: 'Gateway auth token (use in customer portal)',
    });

    new cdk.CfnOutput(this, 'ProxyUrl', {
      value: `ws://${eip.attrPublicIp}:3050`,
      description: 'Customer Gateway Proxy WebSocket URL',
    });

    new cdk.CfnOutput(this, 'SshCommand', {
      value: `ssh ubuntu@${eip.attrPublicIp}`,
      description: 'SSH into the instance',
    });

    new cdk.CfnOutput(this, 'SsmCommand', {
      value: `aws ssm start-session --target ${instance.instanceId}`,
      description: 'SSM Session Manager (no SSH key needed)',
    });

    new cdk.CfnOutput(this, 'HealthCheckUrl', {
      value: `http://${eip.attrPublicIp}:3050/health`,
      description: 'Proxy health check URL',
    });

    new cdk.CfnOutput(this, 'SetupLog', {
      value: `ssh ubuntu@${eip.attrPublicIp} "tail -f /var/log/zeroclaw-setup.log"`,
      description: 'Watch bootstrap progress',
    });
  }
}
