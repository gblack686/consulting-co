#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { OpenClawStack } from '../lib/openclaw-stack';

const app = new cdk.App();

const client = app.node.tryGetContext('client');
if (!client) {
  throw new Error('Missing required context: --context client=<client-name>');
}

const anthropicKey = app.node.tryGetContext('anthropicKey');
if (!anthropicKey) {
  throw new Error('Missing required context: --context anthropicKey=<key>');
}

new OpenClawStack(app, `OpenClaw-${client}`, {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: app.node.tryGetContext('region') || 'us-east-1',
  },
  client,
  anthropicKey,
  gatewayToken: app.node.tryGetContext('gatewayToken'),
  modelTier: app.node.tryGetContext('modelTier') || 'mid',
});
