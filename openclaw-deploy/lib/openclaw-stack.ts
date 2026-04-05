import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as s3deploy from 'aws-cdk-lib/aws-s3-deployment';
import { Construct } from 'constructs';
import * as fs from 'fs';
import * as path from 'path';
import * as crypto from 'crypto';

export interface OpenClawStackProps extends cdk.StackProps {
  client: string;
  anthropicKey: string;
  gatewayToken?: string;
  modelTier?: 'cheap' | 'mid' | 'pro';
}

const MODEL_TIERS: Record<string, string> = {
  cheap: 'claude-haiku-4-5-20251001',
  mid: 'claude-sonnet-4-6',
  pro: 'claude-opus-4-6',
};

export class OpenClawStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: OpenClawStackProps) {
    super(scope, id, props);

    const { client, anthropicKey, modelTier = 'mid' } = props;
    const gatewayToken = props.gatewayToken || crypto.randomUUID();
    const defaultModel = MODEL_TIERS[modelTier] || MODEL_TIERS.mid;

    // --- Build openclaw.json from template ---
    const configTemplate = fs.readFileSync(
      path.join(__dirname, '..', 'config', 'openclaw.json.tmpl'),
      'utf8'
    );
    const openclawJson = configTemplate
      .replace(/\$\{DEFAULT_MODEL\}/g, defaultModel);

    // --- Build .env from template ---
    const envTemplate = fs.readFileSync(
      path.join(__dirname, '..', 'config', 'env.tmpl'),
      'utf8'
    );
    const envFile = envTemplate
      .replace(/\$\{ANTHROPIC_KEY\}/g, anthropicKey);

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

    // Write openclaw.json
    fs.writeFileSync(path.join(stageDir, 'openclaw.json'), openclawJson.replace(/\r\n/g, '\n'));

    // Write .env
    fs.writeFileSync(path.join(stageDir, '.env'), envFile.replace(/\r\n/g, '\n'));

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

    // Copy dashboard build (if exists) into proxy/dashboard/
    const dashboardDistDir = path.join(__dirname, '..', 'dashboard', 'dist');
    if (fs.existsSync(dashboardDistDir)) {
      const copyDirRecursive = (src: string, dest: string) => {
        fs.mkdirSync(dest, { recursive: true });
        for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
          const srcPath = path.join(src, entry.name);
          const destPath = path.join(dest, entry.name);
          if (entry.isDirectory()) {
            copyDirRecursive(srcPath, destPath);
          } else {
            fs.copyFileSync(srcPath, destPath);
          }
        }
      };
      copyDirRecursive(dashboardDistDir, path.join(stageDir, 'proxy', 'dashboard'));
    }

    // --- S3 bucket for config bundle ---
    const bucket = new s3.Bucket(this, 'BundleBucket', {
      bucketName: `openclaw-bundle-${client}-${this.account}`,
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
    const sg = new ec2.SecurityGroup(this, 'OpenClawSG', {
      vpc,
      description: `OpenClaw gateway for ${client}`,
      allowAllOutbound: true,
    });
    sg.addIngressRule(ec2.Peer.anyIpv4(), ec2.Port.tcp(22), 'SSH');
    sg.addIngressRule(ec2.Peer.anyIpv4(), ec2.Port.tcp(3050), 'Gateway proxy');
    sg.addIngressRule(ec2.Peer.anyIpv4(), ec2.Port.tcp(18789), 'OpenClaw gateway');

    // --- IAM Role (S3 read for bundle + SSM for Session Manager) ---
    const role = new iam.Role(this, 'OpenClawRole', {
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
      'exec > /var/log/openclaw-setup.log 2>&1',
      'echo "=== OpenClaw bootstrap starting ==="',
      '',
      '# 1. System deps',
      'apt-get update -qq',
      'apt-get install -y -qq unzip curl git build-essential',
      '',
      '# 2. AWS CLI v2',
      'curl -fsSL "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o /tmp/awscliv2.zip',
      'unzip -q /tmp/awscliv2.zip -d /tmp',
      '/tmp/aws/install',
      'rm -rf /tmp/awscliv2.zip /tmp/aws',
      'echo "=== AWS CLI installed ==="',
      '',
      '# 3. Node.js 22.x',
      'curl -fsSL https://deb.nodesource.com/setup_22.x | bash -',
      'apt-get install -y nodejs',
      'echo "=== Node.js installed: $(node --version) ==="',
      '',
      '# 4. npm global dir for ubuntu',
      'su - ubuntu -c "mkdir -p ~/.npm-global && npm config set prefix \'~/.npm-global\'"',
      'echo \'export PATH="$HOME/.npm-global/bin:$PATH"\' >> /home/ubuntu/.bashrc',
      '',
      '# 5. Install openclaw globally (as ubuntu)',
      'su - ubuntu -c \'export PATH="$HOME/.npm-global/bin:$PATH" && npm install -g openclaw\'',
      'echo "=== openclaw installed ==="',
      '',
      '# 6. openclaw setup (as ubuntu)',
      'su - ubuntu -c \'export PATH="$HOME/.npm-global/bin:$PATH" && openclaw setup --non-interactive\' || \\',
      '  su - ubuntu -c "mkdir -p ~/.openclaw/{workspace,agents}"',
      'echo "=== openclaw setup complete ==="',
      '',
      '# 7. Download bundle from S3',
      `BUCKET="${bucket.bucketName}"`,
      'mkdir -p /home/ubuntu/.openclaw /opt/gateway-proxy',
      'aws s3 cp s3://$BUCKET/bundle/openclaw.json /home/ubuntu/.openclaw/openclaw.json',
      'aws s3 cp s3://$BUCKET/bundle/.env /home/ubuntu/.openclaw/.env',
      'aws s3 cp --recursive s3://$BUCKET/bundle/workspace/ /home/ubuntu/.openclaw/workspace/',
      'aws s3 cp --recursive s3://$BUCKET/bundle/proxy/ /opt/gateway-proxy/',
      'chown -R ubuntu:ubuntu /home/ubuntu/.openclaw',
      'echo "=== Bundle downloaded from S3 ==="',
      '',
      '# 8. Install claude-code globally (as ubuntu)',
      'su - ubuntu -c \'export PATH="$HOME/.npm-global/bin:$PATH" && npm install -g @anthropic-ai/claude-code\' || true',
      'echo "=== claude-code installed ==="',
      '',
      '# 9. User-level systemd service for openclaw gateway',
      'UBUNTU_UID=$(id -u ubuntu)',
      'mkdir -p /home/ubuntu/.config/systemd/user',
      'cat > /home/ubuntu/.config/systemd/user/openclaw-gateway.service << \'SVCEOF\'',
      '[Unit]',
      'Description=OpenClaw Gateway',
      'After=network.target',
      '',
      '[Service]',
      'Type=simple',
      'EnvironmentFile=/home/ubuntu/.openclaw/.env',
      'Environment=PATH=/home/ubuntu/.npm-global/bin:/usr/local/bin:/usr/bin:/bin',
      'Environment=HOME=/home/ubuntu',
      'WorkingDirectory=/home/ubuntu/.openclaw',
      'ExecStart=/home/ubuntu/.npm-global/bin/openclaw gateway --port 18789',
      'Restart=always',
      'RestartSec=3',
      '',
      '[Install]',
      'WantedBy=default.target',
      'SVCEOF',
      'chown -R ubuntu:ubuntu /home/ubuntu/.config',
      '',
      '# 10. Enable linger for ubuntu (persistent user services)',
      'loginctl enable-linger ubuntu',
      '',
      '# 11. Start openclaw gateway (as ubuntu, user-level systemd)',
      'su - ubuntu -c "XDG_RUNTIME_DIR=/run/user/$UBUNTU_UID systemctl --user daemon-reload"',
      'su - ubuntu -c "XDG_RUNTIME_DIR=/run/user/$UBUNTU_UID systemctl --user enable openclaw-gateway"',
      'su - ubuntu -c "XDG_RUNTIME_DIR=/run/user/$UBUNTU_UID systemctl --user start openclaw-gateway"',
      'echo "=== OpenClaw gateway started ==="',
      '',
      '# 12. Install proxy deps',
      'cd /opt/gateway-proxy && npm install --production',
      'chown -R ubuntu:ubuntu /opt/gateway-proxy',
      '',
      '# 13. System-level systemd for gateway proxy',
      'cat > /etc/systemd/system/gateway-proxy.service << PROXYEOF',
      '[Unit]',
      'Description=Customer Gateway Proxy',
      'After=network.target',
      '',
      '[Service]',
      'Type=simple',
      'User=ubuntu',
      'WorkingDirectory=/opt/gateway-proxy',
      'ExecStart=/usr/bin/node server.js',
      'Restart=always',
      'RestartSec=3',
      'Environment=OPENCLAW_WS_URL=ws://127.0.0.1:18789',
      `Environment=OPENCLAW_AUTH_TOKEN=${gatewayToken}`,
      'Environment=PORT=3050',
      '',
      '[Install]',
      'WantedBy=multi-user.target',
      'PROXYEOF',
      '',
      '# 14. Enable and start proxy (initial start with placeholder token)',
      'systemctl daemon-reload',
      'systemctl enable gateway-proxy',
      'sleep 5',
      'systemctl start gateway-proxy',
      'echo "=== Gateway proxy started ==="',
      '',
      '# 15. Run openclaw doctor and configure gateway mode',
      'su - ubuntu -c \'export PATH="$HOME/.npm-global/bin:$PATH" && openclaw doctor --non-interactive\' || true',
      'su - ubuntu -c \'export PATH="$HOME/.npm-global/bin:$PATH" && openclaw config set gateway.mode local\' || true',
      '',
      '# 16. Patch proxy with actual OpenClaw gateway auth token',
      'OC_TOKEN=$(su - ubuntu -c \'cat ~/.openclaw/openclaw.json 2>/dev/null\' | python3 -c "import sys,json; print(json.load(sys.stdin).get(\'gateway\',{}).get(\'auth\',{}).get(\'token\',\'\'))" 2>/dev/null || true)',
      'if [ -n "$OC_TOKEN" ]; then',
      '  sed -i "s/Environment=OPENCLAW_AUTH_TOKEN=.*/Environment=OPENCLAW_AUTH_TOKEN=$OC_TOKEN/" /etc/systemd/system/gateway-proxy.service',
      '  systemctl daemon-reload',
      '  systemctl restart gateway-proxy',
      '  echo "=== Proxy patched with gateway token ==="',
      'fi',
      '',
      '# 17. Start OpenClaw gateway',
      'su - ubuntu -c \'export PATH="$HOME/.npm-global/bin:$PATH" && nohup openclaw gateway --port 18789 > /tmp/openclaw-gateway.log 2>&1 &\' || true',
      'sleep 5',
      '',
      'echo "=== OpenClaw bootstrap complete ==="',
    );

    // --- EC2 Instance ---
    const instance = new ec2.Instance(this, 'OpenClawInstance', {
      vpc,
      instanceType: ec2.InstanceType.of(ec2.InstanceClass.T3, ec2.InstanceSize.MEDIUM),
      machineImage: ec2.MachineImage.lookup({
        name: 'ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*',
        owners: ['099720109477'],
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

    cdk.Tags.of(instance).add('Name', `openclaw-${client}`);
    cdk.Tags.of(instance).add('Project', 'openclaw');
    cdk.Tags.of(instance).add('Client', client);

    // --- Elastic IP ---
    const eip = new ec2.CfnEIP(this, 'OpenClawEIP', {
      tags: [{ key: 'Name', value: `openclaw-${client}-eip` }],
    });

    new ec2.CfnEIPAssociation(this, 'OpenClawEIPAssoc', {
      allocationId: eip.attrAllocationId,
      instanceId: instance.instanceId,
    });

    // --- Outputs ---
    new cdk.CfnOutput(this, 'PublicIp', {
      value: eip.attrPublicIp,
      description: 'OpenClaw instance public IP',
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
      value: `ssh ubuntu@${eip.attrPublicIp} "tail -f /var/log/openclaw-setup.log"`,
      description: 'Watch bootstrap progress',
    });

    new cdk.CfnOutput(this, 'DashboardUrl', {
      value: `http://${eip.attrPublicIp}:3050/?token=${gatewayToken}`,
      description: 'Consulting dashboard URL',
    });

    new cdk.CfnOutput(this, 'AmplifyEnvVar', {
      value: `VITE_OPENCLAW_WS_URL=ws://${eip.attrPublicIp}:3050`,
      description: 'Set this env var on Amplify to connect frontend',
    });
  }
}
