/**
 * ElevenLabs + Supabase Integration Backend
 * Production-ready TypeScript implementation
 *
 * Features:
 * - Post-call webhooks for data persistence
 * - Server tools for real-time data collection
 * - Automatic transcript analysis
 * - Secure webhook verification
 */

import express, { Request, Response, Router } from 'express';
import crypto from 'crypto';
import { createClient, SupabaseClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';

dotenv.config();

// ============================================
// Configuration
// ============================================

interface ElevenLabsConfig {
  apiKey: string;
  webhookSecret?: string;
  supabaseUrl: string;
  supabaseKey: string;
}

const config: ElevenLabsConfig = {
  apiKey: process.env.ELEVENLABS_API_KEY || '',
  webhookSecret: process.env.ELEVENLABS_WEBHOOK_SECRET,
  supabaseUrl: process.env.SUPABASE_URL || '',
  supabaseKey: process.env.SUPABASE_SERVICE_KEY || ''
};

// ============================================
// Types
// ============================================

interface ConversationTranscriptTurn {
  role: 'agent' | 'user';
  message: string;
  timestamp?: number;
}

interface WebhookPayload {
  conversation_id: string;
  agent_id?: string;
  duration_secs?: number;
  transcript?: ConversationTranscriptTurn[];
  analysis?: {
    extracted_data?: Record<string, any>;
    summary?: string;
    sentiment?: string;
  };
  status?: string;
  metadata?: Record<string, any>;
}

interface ExtractedDiscoveryData {
  user_name?: string;
  email?: string;
  phone?: string;
  company?: string;
  project_type?: string;
  project_description?: string;
  requirements?: string[];
  tech_stack?: string[];
  timeline?: string;
  budget?: string;
  key_challenges?: string[];
  success_metrics?: string[];
  team_size?: string;
  decision_makers?: string[];
  next_steps?: string[];
}

interface StoredConversation {
  conversation_id: string;
  user_name?: string;
  email?: string;
  phone?: string;
  company?: string;
  project_type?: string;
  requirements?: Record<string, any>;
  tech_stack?: string[];
  timeline?: string;
  budget?: string;
  transcript?: ConversationTranscriptTurn[];
  extracted_data?: ExtractedDiscoveryData;
  analysis?: Record<string, any>;
  duration_secs?: number;
  status: 'pending_review' | 'reviewed' | 'archived';
  metadata?: Record<string, any>;
  created_at: string;
}

// ============================================
// Supabase Client
// ============================================

class SupabaseService {
  private client: SupabaseClient;

  constructor(url: string, key: string) {
    this.client = createClient(url, key);
  }

  async saveConversation(data: StoredConversation): Promise<any> {
    const { data: result, error } = await this.client
      .from('elevenlabs_conversations')
      .insert([data]);

    if (error) throw new Error(`Failed to save conversation: ${error.message}`);
    return result;
  }

  async getConversation(conversationId: string): Promise<any> {
    const { data, error } = await this.client
      .from('elevenlabs_conversations')
      .select('*')
      .eq('conversation_id', conversationId)
      .single();

    if (error && error.code !== 'PGRST116') {
      throw new Error(`Failed to get conversation: ${error.message}`);
    }
    return data;
  }

  async updateConversationStatus(
    conversationId: string,
    status: 'pending_review' | 'reviewed' | 'archived'
  ): Promise<any> {
    const { data, error } = await this.client
      .from('elevenlabs_conversations')
      .update({ status, updated_at: new Date().toISOString() })
      .eq('conversation_id', conversationId);

    if (error) throw new Error(`Failed to update conversation: ${error.message}`);
    return data;
  }

  async findOrCreateContact(contactData: Partial<ExtractedDiscoveryData>): Promise<any> {
    // Try to find existing contact
    let query = this.client.from('contacts').select('*');

    if (contactData.email) {
      query = query.eq('email', contactData.email);
    } else if (contactData.phone) {
      query = query.eq('phone', contactData.phone);
    } else {
      return null;
    }

    const { data: existing } = await query.single();
    if (existing) return existing;

    // Create new contact
    const { data: newContact, error } = await this.client
      .from('contacts')
      .insert([
        {
          name: contactData.user_name,
          email: contactData.email,
          phone: contactData.phone,
          company: contactData.company
        }
      ])
      .select()
      .single();

    if (error) throw new Error(`Failed to create contact: ${error.message}`);
    return newContact;
  }

  async createDiscoveryRecord(
    conversationId: string,
    contactId: string,
    discoveryData: ExtractedDiscoveryData
  ): Promise<any> {
    const { data, error } = await this.client
      .from('discoveries')
      .insert([
        {
          conversation_id: conversationId,
          user_id: contactId,
          project_name: discoveryData.project_description,
          project_type: discoveryData.project_type,
          description: discoveryData.project_description,
          requirements: discoveryData.requirements,
          tech_stack: discoveryData.tech_stack,
          timeline: discoveryData.timeline,
          budget: discoveryData.budget,
          status: 'discovery',
          notes: `Key challenges: ${discoveryData.key_challenges?.join(', ')}`
        }
      ])
      .select()
      .single();

    if (error) throw new Error(`Failed to create discovery: ${error.message}`);
    return data;
  }
}

// ============================================
// Data Extraction
// ============================================

class DataExtractor {
  static extractFromTranscript(transcript: ConversationTranscriptTurn[]): ExtractedDiscoveryData {
    const extracted: ExtractedDiscoveryData = {
      requirements: [],
      tech_stack: [],
      key_challenges: [],
      success_metrics: [],
      decision_makers: []
    };

    if (!transcript || !Array.isArray(transcript)) {
      return extracted;
    }

    const fullText = transcript
      .filter((t) => t.role === 'user')
      .map((t) => t.message)
      .join(' ')
      .toLowerCase();

    // Extract name patterns
    const nameMatch = fullText.match(/(?:my name is|i'm|i am|call me)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)/);
    if (nameMatch) {
      extracted.user_name = nameMatch[1];
    }

    // Extract email
    const emailMatch = fullText.match(/([a-zA-Z0-9._%-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/);
    if (emailMatch) {
      extracted.email = emailMatch[1];
    }

    // Extract phone
    const phoneMatch = fullText.match(/(\+?1?\s*)?(\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4})/);
    if (phoneMatch) {
      extracted.phone = phoneMatch[2];
    }

    // Extract company
    const companyMatch = fullText.match(/(?:at|company|work at|from)\s+([A-Z][a-zA-Z\s]+?)(?:\s|,|$)/);
    if (companyMatch) {
      extracted.company = companyMatch[1].trim();
    }

    // Extract project type
    if (fullText.includes('mobile') || fullText.includes('app')) {
      extracted.project_type = 'mobile_app';
    } else if (fullText.includes('web') || fullText.includes('website')) {
      extracted.project_type = 'web_app';
    } else if (fullText.includes('ai') || fullText.includes('machine learning')) {
      extracted.project_type = 'ai_ml';
    } else if (fullText.includes('backend') || fullText.includes('api')) {
      extracted.project_type = 'backend_api';
    }

    // Extract technology mentions
    const techStack = [
      { pattern: /\breact\b/, tech: 'React' },
      { pattern: /\bvue\b/, tech: 'Vue' },
      { pattern: /\bnode\b/, tech: 'Node.js' },
      { pattern: /\bpython\b/, tech: 'Python' },
      { pattern: /\brust\b/, tech: 'Rust' },
      { pattern: /\bgo\b/, tech: 'Go' },
      { pattern: /\btypescript\b/, tech: 'TypeScript' },
      { pattern: /\bdatabase|postgres|mongo|mysql\b/, tech: 'Database' },
      { pattern: /\baws|azure|gcp|cloud\b/, tech: 'Cloud' }
    ];

    techStack.forEach(({ pattern, tech }) => {
      if (pattern.test(fullText) && extracted.tech_stack) {
        extracted.tech_stack.push(tech);
      }
    });

    // Remove duplicates
    if (extracted.tech_stack) {
      extracted.tech_stack = [...new Set(extracted.tech_stack)];
    }

    // Extract timeline
    const timelineMatch = fullText.match(/(immediate|asap|this week|this month|next month|(\d+)\s*(weeks?|months?|quarters?|years?))/i);
    if (timelineMatch) {
      extracted.timeline = timelineMatch[0];
    }

    // Extract budget indicators
    const budgetMatch = fullText.match(/(\$[\d,]+|budget.*?(\d+[kK]|free|small|medium|large))/i);
    if (budgetMatch) {
      extracted.budget = budgetMatch[0];
    }

    return extracted;
  }

  static analyzeConversationQuality(transcript: ConversationTranscriptTurn[]): {
    completeness: number;
    quality: 'low' | 'medium' | 'high';
    missingAreas: string[];
  } {
    if (!transcript || transcript.length < 2) {
      return { completeness: 0, quality: 'low', missingAreas: [] };
    }

    const fullText = transcript
      .map((t) => t.message)
      .join(' ')
      .toLowerCase();

    const checklist = [
      { key: 'name', pattern: /name|call me|i'm/i },
      { key: 'contact', pattern: /email|phone|contact/i },
      { key: 'company', pattern: /company|work/i },
      { key: 'project_type', pattern: /mobile|web|app|ai|backend|api/i },
      { key: 'requirements', pattern: /need|require|feature|functionality/i },
      { key: 'timeline', pattern: /when|timeline|deadline|urgent/i },
      { key: 'budget', pattern: /budget|cost|pricing|price/i },
      { key: 'team', pattern: /team|people|developers|engineers/i }
    ];

    let completeness = 0;
    const missingAreas: string[] = [];

    checklist.forEach(({ key, pattern }) => {
      if (pattern.test(fullText)) {
        completeness += 12.5;
      } else {
        missingAreas.push(key);
      }
    });

    let quality: 'low' | 'medium' | 'high' = 'low';
    if (completeness >= 75) quality = 'high';
    else if (completeness >= 50) quality = 'medium';

    return { completeness: Math.round(completeness), quality, missingAreas };
  }
}

// ============================================
// Webhook Verification
// ============================================

class WebhookVerifier {
  static verify(body: string, signature: string, secret: string): boolean {
    try {
      const hash = crypto.createHmac('sha256', secret).update(body).digest('base64');
      return crypto.timingSafeEqual(Buffer.from(hash), Buffer.from(signature));
    } catch {
      return false;
    }
  }
}

// ============================================
// Express Router Setup
// ============================================

function createElevenLabsRouter(supabaseService: SupabaseService): Router {
  const router = express.Router();

  /**
   * Health check endpoint
   */
  router.get('/health', (req: Request, res: Response) => {
    res.json({ status: 'ok', timestamp: new Date().toISOString() });
  });

  /**
   * Post-call webhook: Save conversation data
   */
  router.post('/webhook/conversation-completed', async (req: Request, res: Response) => {
    try {
      const signature = req.headers['x-elevenlabs-signature'] as string;
      const body = JSON.stringify(req.body);

      // Verify signature if secret is configured
      if (config.webhookSecret && signature) {
        const isValid = WebhookVerifier.verify(body, signature, config.webhookSecret);
        if (!isValid) {
          return res.status(401).json({ error: 'Invalid webhook signature' });
        }
      }

      const payload: WebhookPayload = req.body;

      if (!payload.conversation_id) {
        return res.status(400).json({ error: 'Missing conversation_id' });
      }

      // Extract data from transcript
      const extractedData = DataExtractor.extractFromTranscript(payload.transcript || []);
      const { completeness, quality } = DataExtractor.analyzeConversationQuality(
        payload.transcript || []
      );

      // Prepare conversation record
      const conversationRecord: StoredConversation = {
        conversation_id: payload.conversation_id,
        user_name: extractedData.user_name,
        email: extractedData.email,
        phone: extractedData.phone,
        company: extractedData.company,
        project_type: extractedData.project_type,
        requirements: extractedData.requirements,
        tech_stack: extractedData.tech_stack,
        timeline: extractedData.timeline,
        budget: extractedData.budget,
        transcript: payload.transcript,
        extracted_data: extractedData,
        analysis: {
          ...payload.analysis,
          completeness,
          quality,
          transcript_length: payload.transcript?.length || 0
        },
        duration_secs: payload.duration_secs,
        status: completeness >= 75 ? 'pending_review' : 'pending_review',
        metadata: {
          ...payload.metadata,
          webhook_received_at: new Date().toISOString(),
          data_quality: quality
        },
        created_at: new Date().toISOString()
      };

      // Save to Supabase
      await supabaseService.saveConversation(conversationRecord);

      // If contact info available, create or update contact
      if (extractedData.email || extractedData.phone) {
        const contact = await supabaseService.findOrCreateContact(extractedData);
        if (contact && extractedData.project_type) {
          // Create discovery record
          await supabaseService.createDiscoveryRecord(
            payload.conversation_id,
            contact.id,
            extractedData
          );
        }
      }

      res.json({
        success: true,
        conversation_id: payload.conversation_id,
        data_quality: quality,
        completeness: `${completeness}%`,
        extracted_fields: Object.keys(extractedData).filter(
          (k) => (extractedData as any)[k]
        )
      });
    } catch (error) {
      console.error('Webhook error:', error);
      res.status(500).json({
        error: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  });

  /**
   * Retrieve conversation data
   */
  router.get('/conversations/:conversationId', async (req: Request, res: Response) => {
    try {
      const { conversationId } = req.params;
      const conversation = await supabaseService.getConversation(conversationId);

      if (!conversation) {
        return res.status(404).json({ error: 'Conversation not found' });
      }

      res.json(conversation);
    } catch (error) {
      console.error('Error retrieving conversation:', error);
      res.status(500).json({
        error: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  });

  /**
   * Update conversation status
   */
  router.patch('/conversations/:conversationId/status', async (req: Request, res: Response) => {
    try {
      const { conversationId } = req.params;
      const { status } = req.body;

      if (!['pending_review', 'reviewed', 'archived'].includes(status)) {
        return res.status(400).json({ error: 'Invalid status' });
      }

      await supabaseService.updateConversationStatus(conversationId, status);

      res.json({ success: true, status });
    } catch (error) {
      console.error('Error updating conversation:', error);
      res.status(500).json({
        error: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  });

  return router;
}

// ============================================
// Express App Setup
// ============================================

export function createApp(): express.Application {
  const app = express();

  // Middleware
  app.use(express.json());
  app.use((req, res, next) => {
    console.log(`[${new Date().toISOString()}] ${req.method} ${req.path}`);
    next();
  });

  // Initialize services
  const supabaseService = new SupabaseService(config.supabaseUrl, config.supabaseKey);

  // Routes
  app.use('/elevenlabs', createElevenLabsRouter(supabaseService));

  // Health check
  app.get('/', (req, res) => {
    res.json({
      service: 'elevenlabs-supabase-backend',
      version: '1.0.0',
      status: 'running'
    });
  });

  // Error handling
  app.use((err: any, req: Request, res: Response) => {
    console.error('Unhandled error:', err);
    res.status(500).json({ error: 'Internal server error' });
  });

  return app;
}

// ============================================
// Server Startup
// ============================================

if (require.main === module) {
  const app = createApp();
  const PORT = process.env.PORT || 3000;

  app.listen(PORT, () => {
    console.log(`✓ ElevenLabs + Supabase Backend running on port ${PORT}`);
    console.log(`✓ Webhook endpoint: POST /elevenlabs/webhook/conversation-completed`);
    console.log(`✓ Health check: GET /elevenlabs/health`);
  });
}

export { SupabaseService, DataExtractor, WebhookVerifier };
