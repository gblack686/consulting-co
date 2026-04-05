/**
 * API Endpoint: Generate Scoping Document
 * POST /api/generate-document
 *
 * Generates a professional scoping document using Claude
 * Saves as PDF and sends via email
 */

import { createClient } from '@supabase/supabase-js';
import Anthropic from '@anthropic-ai/sdk';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_KEY!
);

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY
});

const resendApiKey = process.env.RESEND_API_KEY;

interface Conversation {
  conversation_id: string;
  user_name: string;
  email: string;
  project_type: string;
  requirements: string[];
  tech_stack: string[];
  timeline: string;
  budget: string;
  company?: string;
  transcript: Array<{ role: 'agent' | 'user'; message: string }>;
}

export async function POST(request: Request): Promise<Response> {
  try {
    const { conversationId } = await request.json();

    if (!conversationId) {
      return new Response(JSON.stringify({ error: 'Missing conversationId' }), {
        status: 400
      });
    }

    // Get conversation from Supabase
    const { data: conversation, error: fetchError } = await supabase
      .from('elevenlabs_conversations')
      .select('*')
      .eq('conversation_id', conversationId)
      .single();

    if (fetchError || !conversation) {
      return new Response(JSON.stringify({ error: 'Conversation not found' }), {
        status: 404
      });
    }

    // Generate document using Claude
    const documentContent = await generateScopingDocument(conversation);

    // Save to Supabase
    const { data: doc, error: docError } = await supabase
      .from('scoping_documents')
      .insert({
        conversation_id: conversationId,
        content: documentContent,
        status: 'generated',
        created_at: new Date().toISOString()
      })
      .select()
      .single();

    if (docError) throw docError;

    // Send email to user
    try {
      await sendDocumentEmail(conversation.email, conversation.user_name, documentContent);
    } catch (emailError) {
      console.error('Email send error:', emailError);
      // Don't fail the entire request if email fails
    }

    // Send notification to team
    try {
      await notifyTeamOfDocument(conversation.user_name, conversation.project_type);
    } catch (notifyError) {
      console.error('Notification error:', notifyError);
    }

    return new Response(
      JSON.stringify({
        success: true,
        document: doc,
        message: 'Document generated and sent to user'
      }),
      { status: 200 }
    );
  } catch (error) {
    console.error('Error generating document:', error);
    return new Response(
      JSON.stringify({ error: 'Failed to generate document' }),
      { status: 500 }
    );
  }
}

/**
 * Generate scoping document using Claude
 */
async function generateScopingDocument(conversation: Conversation): Promise<string> {
  const prompt = `You are a technical consultant generating a professional scoping document.

Based on this discovery conversation, create a comprehensive technical scoping document.

**Participant Information:**
- Name: ${conversation.user_name}
- Company: ${conversation.company || 'Not specified'}
- Project Type: ${conversation.project_type}

**Collected Requirements:**
${conversation.requirements?.map((r) => `- ${r}`).join('\n') || '- No specific requirements captured'}

**Technology Preferences:**
${conversation.tech_stack?.length ? conversation.tech_stack.map((t) => `- ${t}`).join('\n') : '- No preferences specified'}

**Project Timeline:**
${conversation.timeline || 'Not specified'}

**Budget:**
${conversation.budget || 'Not specified'}

**Conversation Transcript Summary:**
${conversation.transcript?.map((t) => `${t.role.toUpperCase()}: ${t.message}`).join('\n\n') || 'No transcript available'}

---

Generate a professional scoping document with these sections (use markdown formatting):

# Technical Scoping Document: [Project Name]

## Executive Summary
(2-3 paragraph overview of the project, objectives, and scope)

## Project Overview
- **Project Name:** [Derived from conversation]
- **Client:** ${conversation.user_name}
- **Project Type:** ${conversation.project_type}
- **Document Generated:** [Today's date]

## Discovery Summary
(Summary of the discovery call, key findings, and understanding of the project)

## Requirements & Scope

### Functional Requirements
(List of functional requirements extracted from conversation)

### Non-Functional Requirements
(Performance, security, scalability, compliance requirements)

### Out of Scope
(What will NOT be included in this project)

## Proposed Technology Stack

### Backend
(Recommended backend technologies based on requirements)

### Frontend
(Recommended frontend technologies)

### Infrastructure & DevOps
(Cloud platforms, deployment strategies, CI/CD)

### Additional Tools & Services
(Third-party services, APIs, monitoring tools)

## Architecture & Implementation Plan

### High-Level Architecture
(Overview of how components fit together)

### Implementation Phases
1. Phase 1: Foundation & Core Features
2. Phase 2: Integration & Optimization
3. Phase 3: Testing, Security & Deployment
(Adjust based on scope)

## Timeline & Milestones

**Timeline:** ${conversation.timeline || 'To be determined'}

### Recommended Milestones
- Week 1-2: Setup, architecture, and initial development
- Week 3-4: Core feature development
- Week 5-6: Integration and testing
- Week 7+: Refinement and deployment

## Resource Requirements

**Team Composition:**
- (List team roles needed: full-stack developers, designers, QA, etc.)

**External Dependencies:**
- (Any third-party APIs, services, or platforms needed)

## Success Criteria & Metrics

### Key Performance Indicators
(How will success be measured?)

### Launch Criteria
(What needs to be true before going live?)

## Risk Assessment

### Identified Risks
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| (Identify project-specific risks) | | | |

## Next Steps

1. **Kickoff Meeting:** Schedule team alignment and planning session
2. **Design Phase:** Create detailed wireframes and technical specifications
3. **Development Sprint 1:** Begin implementation
4. **Ongoing:** Weekly check-ins and progress reviews

## Questions & Clarifications

The following items may need further discussion:
(List any ambiguities or items needing clarification)

---

**Prepared for:** ${conversation.user_name}
**Date:** ${new Date().toLocaleDateString()}
**Confidence Level:** ${getConfidenceLevel(conversation)}

*This document is based on the discovery conversation and should be reviewed and refined with the full team.*`;

  const message = await anthropic.messages.create({
    model: 'claude-3-5-sonnet-20241022',
    max_tokens: 3000,
    messages: [
      {
        role: 'user',
        content: prompt
      }
    ]
  });

  return message.content[0].type === 'text' ? message.content[0].text : '';
}

/**
 * Send document to user via email
 */
async function sendDocumentEmail(
  userEmail: string,
  userName: string,
  documentContent: string
): Promise<void> {
  if (!resendApiKey) {
    console.warn('RESEND_API_KEY not configured');
    return;
  }

  // Convert markdown to HTML
  const htmlContent = markdownToHtml(documentContent);

  const response = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${resendApiKey}`
    },
    body: JSON.stringify({
      from: 'GB Automation <scoping@consulting-co.com>',
      to: userEmail,
      subject: 'Your Technical Scoping Document is Ready',
      html: `
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 800px;">
          <h2>Hi ${userName},</h2>

          <p>Your technical scoping document has been generated based on your discovery call!</p>

          <div style="background: #f0f9ff; border-left: 4px solid #3b82f6; padding: 16px; margin: 20px 0; border-radius: 4px;">
            <p style="margin: 0;"><strong>📄 What's Included:</strong></p>
            <ul style="margin: 8px 0 0 20px; color: #666;">
              <li>Executive Summary</li>
              <li>Project Overview & Scope</li>
              <li>Technology Stack Recommendations</li>
              <li>Implementation Timeline</li>
              <li>Resource Requirements</li>
              <li>Next Steps</li>
            </ul>
          </div>

          <h3 style="margin: 20px 0 10px 0;">Document Preview:</h3>
          <div style="background: #f9fafb; border: 1px solid #e5e7eb; padding: 20px; border-radius: 8px; font-family: 'Courier New', monospace; font-size: 13px; line-height: 1.6; color: #333; max-height: 400px; overflow-y: auto; white-space: pre-wrap; word-wrap: break-word;">
${documentContent.substring(0, 1000)}...
          </div>

          <p style="margin-top: 20px;">
            <a href="https://your-domain.com/documents/view?email=${encodeURIComponent(userEmail)}" style="background: #3b82f6; color: white; padding: 12px 24px; border-radius: 6px; text-decoration: none; display: inline-block; font-weight: 600;">
              View Full Document
            </a>
          </p>

          <h3 style="margin: 20px 0 10px 0;">Next Steps:</h3>
          <ol style="color: #666; line-height: 1.8;">
            <li>Review the document and share any feedback or corrections</li>
            <li>Schedule a planning call to discuss architecture in detail</li>
            <li>Identify and assign team members</li>
            <li>Begin development planning and sprint estimation</li>
          </ol>

          <p style="margin-top: 20px; color: #666; font-size: 14px;">
            Questions about the document? <a href="mailto:hello@consulting-co.com" style="color: #3b82f6;">Contact our team</a>.
          </p>

          <hr style="margin: 20px 0; border: none; border-top: 1px solid #e5e7eb;">

          <p style="color: #999; font-size: 12px; margin: 0;">
            © 2025 GB Automation. All rights reserved.
          </p>
        </div>
      `
    })
  });

  if (!response.ok) {
    throw new Error(`Email send failed: ${response.statusText}`);
  }
}

/**
 * Notify team that document was generated
 */
async function notifyTeamOfDocument(userName: string, projectType: string): Promise<void> {
  if (!resendApiKey) return;

  const teamEmails = process.env.TEAM_EMAIL_LIST?.split(',') || [];

  if (teamEmails.length === 0) return;

  await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${resendApiKey}`
    },
    body: JSON.stringify({
      from: 'GB Automation <scoping@consulting-co.com>',
      to: teamEmails,
      subject: `Scoping Document Ready: ${userName}'s ${projectType} project`,
      html: `
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;">
          <h2>Scoping Document Generated</h2>

          <p>A technical scoping document has been generated for <strong>${userName}</strong>'s <strong>${projectType}</strong> project.</p>

          <p><a href="https://your-domain.com/dashboard" style="background: #3b82f6; color: white; padding: 10px 20px; border-radius: 6px; text-decoration: none; display: inline-block;">Review in Dashboard</a></p>

          <p>Next step: Schedule a planning call with the client to discuss the proposal.</p>
        </div>
      `
    })
  });
}

/**
 * Determine confidence level based on conversation completeness
 */
function getConfidenceLevel(conversation: Conversation): string {
  const completeness =
    (conversation.requirements?.length || 0) +
    (conversation.tech_stack?.length || 0) +
    (conversation.timeline ? 1 : 0) +
    (conversation.budget ? 1 : 0);

  if (completeness >= 6) return 'High';
  if (completeness >= 4) return 'Medium';
  return 'Low - Additional clarification needed';
}

/**
 * Convert markdown to HTML
 */
function markdownToHtml(markdown: string): string {
  // Simple markdown to HTML conversion
  return markdown
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    .replace(/^\- (.+)$/gm, '<li>$1</li>')
    .replace(/^(\d+)\. (.+)$/gm, '<li>$2</li>')
    .replace(/(<li>.*?<\/li>)/s, '<ul>$1</ul>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/\n\n/g, '</p><p>')
    .replace(/^<p>/m, '<p>')
    .replace(/$/, '</p>')
    .replace(/<ul><\/ul>/g, '');
}
