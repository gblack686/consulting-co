#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { ZeroClawStack } from '../lib/zeroclaw-stack';

const app = new cdk.App();

const client = app.node.tryGetContext('client');
if (!client) {
  throw new Error('Missing required context: --context client=<client-name>');
}

const openrouterKey = app.node.tryGetContext('openrouterKey');
if (!openrouterKey) {
  throw new Error('Missing required context: --context openrouterKey=<key>');
}

new ZeroClawStack(app, `ZeroClaw-${client}`, {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: app.node.tryGetContext('region') || 'us-east-1',
  },
  client,
  openrouterKey,
  gatewayToken: app.node.tryGetContext('gatewayToken'),
  modelTier: app.node.tryGetContext('modelTier') || 'cheap',
});
