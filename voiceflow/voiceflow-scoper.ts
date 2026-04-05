/**
 * Voiceflow Scoping Agent SDK
 * Integrates Voiceflow agents with Google Meet for technical project scoping
 */

import axios, { AxiosInstance } from "axios";

interface ScopingData {
  projectName?: string;
  client?: string;
  timeline?: string;
  budget?: string;
  techStack?: string[];
  integrations?: string[];
  mvpFeatures?: string[];
  niceToHaveFeatures?: string[];
  constraints?: string[];
  successMetrics?: string[];
  [key: string]: any;
}

interface VoiceflowState {
  variables: Record<string, any>;
  stack: any[];
}

interface DialogResponse {
  state: VoiceflowState;
  trace: any[];
}

/**
 * VoiceflowScoper
 * Manages conversations with Voiceflow scoping agents
 */
export class VoiceflowScoper {
  private apiKey: string;
  private agentId: string;
  private baseURL: string = "https://general-runtime.voiceflow.com";
  private client: AxiosInstance;
  private sessionData: Map<string, VoiceflowState> = new Map();

  constructor(apiKey: string, agentId: string, baseURL?: string) {
    if (!apiKey || !agentId) {
      throw new Error("API Key and Agent ID are required");
    }

    this.apiKey = apiKey;
    this.agentId = agentId;
    if (baseURL) this.baseURL = baseURL;

    this.client = axios.create({
      baseURL: this.baseURL,
      headers: {
        Authorization: this.apiKey,
        "Content-Type": "application/json"
      }
    });
  }

  /**
   * Initialize a new scoping session
   * @param userId - Unique identifier for the user/meeting participant
   * @param metadata - Optional metadata (meeting ID, participant name, etc.)
   */
  async initializeSession(
    userId: string,
    metadata?: Record<string, any>
  ): Promise<DialogResponse> {
    try {
      const response = await this.client.post<DialogResponse>(
        `/state/user/${userId}/interact`,
        {
          action: { type: "launch" },
          ...(metadata && { metadata })
        },
        {
          params: { projectID: this.agentId }
        }
      );

      this.sessionData.set(userId, response.data.state);
      return response.data;
    } catch (error) {
      throw new Error(
        `Failed to initialize session for user ${userId}: ${error}`
      );
    }
  }

  /**
   * Send a message to the scoping agent
   * @param userId - Session user ID
   * @param userMessage - User's message/answer
   */
  async sendMessage(userId: string, userMessage: string): Promise<DialogResponse> {
    try {
      const response = await this.client.post<DialogResponse>(
        `/state/user/${userId}/interact`,
        {
          action: {
            type: "text",
            payload: userMessage
          }
        },
        {
          params: { projectID: this.agentId }
        }
      );

      this.sessionData.set(userId, response.data.state);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to send message for user ${userId}: ${error}`);
    }
  }

  /**
   * Get current scoping data collected so far
   * @param userId - Session user ID
   */
  async getScopingData(userId: string): Promise<ScopingData> {
    try {
      const response = await this.client.get<VoiceflowState>(
        `/state/user/${userId}`,
        {
          params: { projectID: this.agentId }
        }
      );

      const variables = response.data.variables || {};
      this.sessionData.set(userId, response.data);

      return this.extractScopingData(variables);
    } catch (error) {
      throw new Error(`Failed to get scoping data for user ${userId}: ${error}`);
    }
  }

  /**
   * Check if scoping conversation is complete
   * @param userId - Session user ID
   */
  async isComplete(userId: string): Promise<boolean> {
    try {
      const data = await this.getScopingData(userId);
      return this.validateScopingData(data);
    } catch (error) {
      console.error(`Failed to check completion for user ${userId}:`, error);
      return false;
    }
  }

  /**
   * Get agent state for session
   * @param userId - Session user ID
   */
  async getSessionState(userId: string): Promise<VoiceflowState | undefined> {
    return this.sessionData.get(userId);
  }

  /**
   * Clear session data (e.g., on meeting end)
   * @param userId - Session user ID
   */
  clearSession(userId: string): void {
    this.sessionData.delete(userId);
  }

  /**
   * Extract and normalize scoping data from Voiceflow variables
   */
  private extractScopingData(variables: Record<string, any>): ScopingData {
    const data: ScopingData = {};

    // Map Voiceflow variables to ScopingData
    const mapping: Record<string, string> = {
      project_name: "projectName",
      client_name: "client",
      timeline: "timeline",
      budget: "budget",
      tech_stack: "techStack",
      integrations: "integrations",
      mvp_features: "mvpFeatures",
      nice_to_have: "niceToHaveFeatures",
      constraints: "constraints",
      success_metrics: "successMetrics"
    };

    for (const [voiceflowKey, dataKey] of Object.entries(mapping)) {
      if (variables[voiceflowKey] !== undefined) {
        data[dataKey] = variables[voiceflowKey];
      }
    }

    // Include any additional variables
    for (const [key, value] of Object.entries(variables)) {
      if (!Object.keys(mapping).includes(key) && !key.startsWith("_")) {
        data[key] = value;
      }
    }

    return data;
  }

  /**
   * Validate scoping data completeness
   */
  private validateScopingData(data: ScopingData): boolean {
    const requiredFields = [
      "projectName",
      "client",
      "timeline",
      "budget",
      "techStack",
      "mvpFeatures",
      "constraints",
      "successMetrics"
    ];

    return requiredFields.every(
      (field) => data[field] !== undefined && data[field] !== null && data[field] !== ""
    );
  }
}

/**
 * Google Meet Integration Helper
 * Manages Voiceflow agent integration with Google Meet
 */
export class GoogleMeetScopingIntegration {
  private scoper: VoiceflowScoper;
  private meetingId: string;
  private participants: Map<string, { name: string; joinTime: Date }> = new Map();

  constructor(scoper: VoiceflowScoper, meetingId: string) {
    this.scoper = scoper;
    this.meetingId = meetingId;
  }

  /**
   * Register a participant in the meeting
   * @param participantId - Google Meet participant ID
   * @param participantName - Display name
   */
  async registerParticipant(participantId: string, participantName: string): Promise<void> {
    this.participants.set(participantId, {
      name: participantName,
      joinTime: new Date()
    });

    // Initialize scoping session for this participant
    await this.scoper.initializeSession(participantId, {
      meetingId: this.meetingId,
      participantName,
      joinTime: new Date().toISOString()
    });
  }

  /**
   * Unregister participant (e.g., on meeting leave)
   * @param participantId - Google Meet participant ID
   */
  async unregisterParticipant(participantId: string): Promise<ScopingData | null> {
    try {
      const data = await this.scoper.getScopingData(participantId);
      this.participants.delete(participantId);
      this.scoper.clearSession(participantId);
      return data;
    } catch (error) {
      console.error(`Error unregistering participant ${participantId}:`, error);
      return null;
    }
  }

  /**
   * Process user input during meeting
   * @param participantId - Google Meet participant ID
   * @param userInput - User's message/answer
   */
  async processUserInput(participantId: string, userInput: string): Promise<DialogResponse> {
    return this.scoper.sendMessage(participantId, userInput);
  }

  /**
   * Get scoping results for a participant
   * @param participantId - Google Meet participant ID
   */
  async getParticipantScopingData(participantId: string): Promise<ScopingData> {
    return this.scoper.getScopingData(participantId);
  }

  /**
   * Check if all participants have completed scoping
   */
  async checkMeetingCompletion(): Promise<{
    complete: boolean;
    completed: string[];
    pending: string[];
  }> {
    const results = await Promise.all(
      Array.from(this.participants.keys()).map(async (participantId) => ({
        participantId,
        complete: await this.scoper.isComplete(participantId)
      }))
    );

    const completed = results.filter((r) => r.complete).map((r) => r.participantId);
    const pending = results.filter((r) => !r.complete).map((r) => r.participantId);

    return {
      complete: pending.length === 0 && completed.length > 0,
      completed,
      pending
    };
  }

  /**
   * Export meeting scoping results
   */
  async exportMeetingResults(): Promise<{
    meetingId: string;
    timestamp: string;
    participants: Array<{
      id: string;
      name: string;
      scopingData: ScopingData;
    }>;
  }> {
    const results = [];

    for (const [participantId, participantInfo] of this.participants) {
      try {
        const scopingData = await this.scoper.getScopingData(participantId);
        results.push({
          id: participantId,
          name: participantInfo.name,
          scopingData
        });
      } catch (error) {
        console.error(`Failed to export data for participant ${participantId}:`, error);
      }
    }

    return {
      meetingId: this.meetingId,
      timestamp: new Date().toISOString(),
      participants: results
    };
  }

  /**
   * Get list of registered participants
   */
  getParticipants(): Array<{ id: string; name: string; joinTime: Date }> {
    return Array.from(this.participants).map(([id, info]) => ({
      id,
      ...info
    }));
  }
}

/**
 * Scoping Document Generator
 * Creates structured documents from collected scoping data
 */
export class ScopingDocumentGenerator {
  /**
   * Generate markdown scoping document
   */
  static generateMarkdown(data: ScopingData): string {
    return `# Technical Scoping Document

## Project Information
- **Project Name**: ${data.projectName || "N/A"}
- **Client**: ${data.client || "N/A"}
- **Timeline**: ${data.timeline || "N/A"}
- **Budget**: ${data.budget || "N/A"}

## Technical Requirements
- **Technology Stack**: ${Array.isArray(data.techStack) ? data.techStack.join(", ") : "N/A"}
- **Integrations**: ${Array.isArray(data.integrations) ? data.integrations.join(", ") : "N/A"}

## Scope

### MVP Features
${Array.isArray(data.mvpFeatures) ? data.mvpFeatures.map((f) => `- ${f}`).join("\n") : "- N/A"}

### Nice-to-Have Features
${Array.isArray(data.niceToHaveFeatures) ? data.niceToHaveFeatures.map((f) => `- ${f}`).join("\n") : "- N/A"}

## Constraints & Dependencies
${Array.isArray(data.constraints) ? data.constraints.map((c) => `- ${c}`).join("\n") : "- N/A"}

## Success Metrics
${Array.isArray(data.successMetrics) ? data.successMetrics.map((m) => `- ${m}`).join("\n") : "- N/A"}

---
Generated: ${new Date().toISOString()}
`;
  }

  /**
   * Generate JSON scoping report
   */
  static generateJSON(data: ScopingData): string {
    return JSON.stringify(
      {
        projectName: data.projectName,
        client: data.client,
        timeline: data.timeline,
        budget: data.budget,
        technical: {
          stack: data.techStack,
          integrations: data.integrations
        },
        scope: {
          mvpFeatures: data.mvpFeatures,
          niceToHaveFeatures: data.niceToHaveFeatures
        },
        constraints: data.constraints,
        successMetrics: data.successMetrics,
        generatedAt: new Date().toISOString()
      },
      null,
      2
    );
  }
}

export default {
  VoiceflowScoper,
  GoogleMeetScopingIntegration,
  ScopingDocumentGenerator
};
