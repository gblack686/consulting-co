/**
 * Google Meet + Voiceflow Scoping Agent Integration
 *
 * This example shows how to integrate the Voiceflow scoping agent
 * with Google Meet using the Google Meet API
 */

import { VoiceflowScoper, GoogleMeetScopingIntegration } from "./voiceflow-scoper";

/**
 * Google Meet Participant Information
 */
interface MeetParticipant {
  userId: string;
  displayName: string;
  participantId: string;
  joinTime: Date;
}

/**
 * Scoping Call Configuration
 */
interface ScopingCallConfig {
  meetingCode: string;
  meetingTitle: string;
  organizerId: string;
  organizerName: string;
  startTime: Date;
  maxDuration?: number; // minutes
}

/**
 * Google Meet Scoping Session Manager
 * Orchestrates Voiceflow integration with Google Meet
 */
export class GoogleMeetScopingSession {
  private scoper: VoiceflowScoper;
  private integration: GoogleMeetScopingIntegration;
  private config: ScopingCallConfig;
  private participants: Map<string, MeetParticipant> = new Map();
  private sessionStart: Date = new Date();
  private eventListeners: Map<string, Function[]> = new Map();

  constructor(
    voiceflowApiKey: string,
    voiceflowAgentId: string,
    meetingConfig: ScopingCallConfig
  ) {
    this.scoper = new VoiceflowScoper(voiceflowApiKey, voiceflowAgentId);
    this.integration = new GoogleMeetScopingIntegration(
      this.scoper,
      meetingConfig.meetingCode
    );
    this.config = meetingConfig;
  }

  /**
   * Initialize scoping session
   * Should be called when the meeting starts
   */
  async initialize(): Promise<void> {
    console.log(`Initializing scoping session for meeting: ${this.config.meetingTitle}`);
    // Setup any necessary infrastructure
    this.emit("session_initialized", {
      meetingCode: this.config.meetingCode,
      timestamp: new Date().toISOString()
    });
  }

  /**
   * Handle participant joining the meeting
   */
  async onParticipantJoined(
    participantId: string,
    displayName: string,
    userId?: string
  ): Promise<void> {
    const participant: MeetParticipant = {
      userId: userId || participantId,
      displayName,
      participantId,
      joinTime: new Date()
    };

    this.participants.set(participantId, participant);

    try {
      // Register with Voiceflow integration
      await this.integration.registerParticipant(participantId, displayName);

      console.log(`Participant joined: ${displayName} (${participantId})`);

      this.emit("participant_joined", {
        participantId,
        displayName,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.error(`Error registering participant ${displayName}:`, error);
      this.emit("error", {
        type: "participant_registration_failed",
        participantId,
        error: String(error)
      });
    }
  }

  /**
   * Handle participant leaving the meeting
   */
  async onParticipantLeft(participantId: string): Promise<void> {
    const participant = this.participants.get(participantId);
    if (!participant) return;

    try {
      // Unregister and collect final scoping data
      const scopingData = await this.integration.unregisterParticipant(participantId);

      console.log(`Participant left: ${participant.displayName} (${participantId})`);

      this.emit("participant_left", {
        participantId,
        displayName: participant.displayName,
        scopingData,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.error(`Error unregistering participant ${participantId}:`, error);
    }

    this.participants.delete(participantId);
  }

  /**
   * Handle user input from participant
   * In a real implementation, this would be triggered by:
   * - Text message in meeting chat
   * - Voice transcription from speech-to-text
   * - Button click on companion web interface
   */
  async onUserInput(participantId: string, userInput: string): Promise<void> {
    try {
      const response = await this.integration.processUserInput(participantId, userInput);

      // Extract agent response and send back to user
      const agentMessages = this.extractAgentMessages(response.trace);

      this.emit("agent_response", {
        participantId,
        userInput,
        agentMessages,
        timestamp: new Date().toISOString()
      });

      // Check completion status
      const isComplete = await this.scoper.isComplete(participantId);
      if (isComplete) {
        this.emit("participant_scoping_complete", {
          participantId,
          timestamp: new Date().toISOString()
        });
      }
    } catch (error) {
      console.error(`Error processing input for participant ${participantId}:`, error);
      this.emit("error", {
        type: "input_processing_failed",
        participantId,
        error: String(error)
      });
    }
  }

  /**
   * Get current status of all participants
   */
  async getSessionStatus(): Promise<{
    meetingCode: string;
    startTime: Date;
    elapsedMinutes: number;
    participants: any[];
    completion: {
      complete: boolean;
      completed: string[];
      pending: string[];
    };
  }> {
    const now = new Date();
    const elapsedMinutes = Math.round(
      (now.getTime() - this.sessionStart.getTime()) / 60000
    );

    const completion = await this.integration.checkMeetingCompletion();

    const participants = this.integration.getParticipants().map((p) => ({
      ...p,
      scopingComplete: completion.completed.includes(p.id)
    }));

    return {
      meetingCode: this.config.meetingCode,
      startTime: this.sessionStart,
      elapsedMinutes,
      participants,
      completion
    };
  }

  /**
   * End scoping session and export results
   */
  async endSession(): Promise<any> {
    try {
      const results = await this.integration.exportMeetingResults();

      console.log(`Ending scoping session: ${this.config.meetingTitle}`);

      this.emit("session_ended", {
        meetingCode: this.config.meetingCode,
        duration: new Date().getTime() - this.sessionStart.getTime(),
        results,
        timestamp: new Date().toISOString()
      });

      return results;
    } catch (error) {
      console.error("Error ending session:", error);
      throw error;
    }
  }

  /**
   * Event listener management
   */
  on(event: string, callback: Function): void {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, []);
    }
    this.eventListeners.get(event)!.push(callback);
  }

  private emit(event: string, data: any): void {
    const listeners = this.eventListeners.get(event);
    if (listeners) {
      listeners.forEach((callback) => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in event listener for ${event}:`, error);
        }
      });
    }
  }

  /**
   * Extract readable agent messages from Voiceflow trace
   */
  private extractAgentMessages(trace: any[]): string[] {
    const messages: string[] = [];

    for (const item of trace) {
      if (item.type === "text") {
        messages.push(item.payload.message);
      } else if (item.type === "speak") {
        messages.push(item.payload.message);
      }
    }

    return messages;
  }
}

/**
 * Example: Integrate with Google Meet via Chrome Extension
 * This would be injected into Google Meet page
 */
export class GoogleMeetChromeExtension {
  private session: GoogleMeetScopingSession | null = null;
  private messageInput: HTMLInputElement | null = null;
  private responseContainer: HTMLElement | null = null;

  async initialize(
    voiceflowApiKey: string,
    voiceflowAgentId: string
  ): Promise<void> {
    // Extract meeting info from Google Meet
    const meetingCode = this.extractMeetingCode();
    const meetingTitle = this.extractMeetingTitle();

    const config: ScopingCallConfig = {
      meetingCode,
      meetingTitle,
      organizerId: this.getCurrentUserId(),
      organizerName: this.getCurrentUserName(),
      startTime: new Date()
    };

    this.session = new GoogleMeetScopingSession(
      voiceflowApiKey,
      voiceflowAgentId,
      config
    );

    await this.session.initialize();

    // Create UI for scoping conversation
    this.createUI();

    // Listen for participant changes
    this.monitorParticipants();

    // Setup event listeners
    this.setupEventListeners();
  }

  /**
   * Create UI panel for scoping conversation
   */
  private createUI(): void {
    const container = document.createElement("div");
    container.id = "voiceflow-scoping-panel";
    container.style.cssText = `
      position: fixed;
      right: 20px;
      top: 70px;
      width: 400px;
      height: 600px;
      background: white;
      border-radius: 8px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.1);
      display: flex;
      flex-direction: column;
      z-index: 10000;
    `;

    const header = document.createElement("div");
    header.style.cssText = `
      background: #1f2937;
      color: white;
      padding: 16px;
      border-radius: 8px 8px 0 0;
      font-weight: 500;
    `;
    header.textContent = "Project Scoping Assistant";

    const messages = document.createElement("div");
    messages.id = "scoping-messages";
    messages.style.cssText = `
      flex: 1;
      overflow-y: auto;
      padding: 16px;
      border-bottom: 1px solid #e5e7eb;
    `;

    this.responseContainer = messages;

    const inputArea = document.createElement("div");
    inputArea.style.cssText = `
      padding: 12px;
      display: flex;
      gap: 8px;
    `;

    this.messageInput = document.createElement("input");
    this.messageInput.type = "text";
    this.messageInput.placeholder = "Your response...";
    this.messageInput.style.cssText = `
      flex: 1;
      padding: 8px 12px;
      border: 1px solid #d1d5db;
      border-radius: 4px;
      font-size: 14px;
    `;

    const sendButton = document.createElement("button");
    sendButton.textContent = "Send";
    sendButton.style.cssText = `
      padding: 8px 16px;
      background: #3b82f6;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-weight: 500;
    `;

    sendButton.addEventListener("click", () => this.handleSendMessage());
    this.messageInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter") this.handleSendMessage();
    });

    inputArea.appendChild(this.messageInput);
    inputArea.appendChild(sendButton);

    container.appendChild(header);
    container.appendChild(messages);
    container.appendChild(inputArea);

    document.body.appendChild(container);
  }

  /**
   * Handle sending message to Voiceflow agent
   */
  private async handleSendMessage(): Promise<void> {
    if (!this.messageInput || !this.session) return;

    const userMessage = this.messageInput.value.trim();
    if (!userMessage) return;

    const participantId = this.getCurrentUserId();
    this.messageInput.value = "";

    // Add user message to UI
    this.appendMessage("user", userMessage);

    try {
      // Send to agent
      await this.session.onUserInput(participantId, userMessage);
    } catch (error) {
      console.error("Error sending message:", error);
      this.appendMessage("error", "Failed to process your message");
    }
  }

  /**
   * Add message to conversation UI
   */
  private appendMessage(role: "user" | "agent" | "error", message: string): void {
    if (!this.responseContainer) return;

    const messageEl = document.createElement("div");
    messageEl.style.cssText = `
      margin-bottom: 12px;
      padding: 8px 12px;
      border-radius: 4px;
      font-size: 14px;
      ${
        role === "user"
          ? "background: #dbeafe; color: #1e40af; margin-left: 40px;"
          : role === "agent"
            ? "background: #f0fdf4; color: #15803d; margin-right: 40px;"
            : "background: #fee2e2; color: #991b1b;"
      }
    `;

    messageEl.textContent = message;
    this.responseContainer.appendChild(messageEl);
    this.responseContainer.scrollTop = this.responseContainer.scrollHeight;
  }

  /**
   * Monitor participant list for changes
   */
  private monitorParticipants(): void {
    // This would integrate with Google Meet's participant API
    // For now, this is a placeholder
    const observeParticipants = setInterval(async () => {
      if (!this.session) {
        clearInterval(observeParticipants);
        return;
      }

      // Get current participants from Meet UI
      const participants = this.getParticipantsFromDOM();
      // Track changes and call session.onParticipantJoined/Left
    }, 5000);
  }

  /**
   * Setup event listeners for session events
   */
  private setupEventListeners(): void {
    if (!this.session) return;

    this.session.on("agent_response", (data: any) => {
      data.agentMessages.forEach((msg: string) => {
        this.appendMessage("agent", msg);
      });
    });

    this.session.on("participant_scoping_complete", (data: any) => {
      this.appendMessage(
        "agent",
        "✓ Great! We've collected all the necessary information. Thanks for completing the scoping call!"
      );
    });

    this.session.on("error", (data: any) => {
      this.appendMessage("error", `Error: ${data.error}`);
    });
  }

  // Helper methods to extract info from Google Meet DOM
  private extractMeetingCode(): string {
    const url = window.location.href;
    const match = url.match(/meet\.google\.com\/([a-z-]+)/);
    return match ? match[1] : "unknown";
  }

  private extractMeetingTitle(): string {
    const titleEl = document.querySelector('[data-meeting-title]');
    return titleEl?.textContent || "Scoping Call";
  }

  private getCurrentUserId(): string {
    // Extract from Google Meet
    return "user_" + Math.random().toString(36).substr(2, 9);
  }

  private getCurrentUserName(): string {
    const nameEl = document.querySelector('[data-me-name]');
    return nameEl?.textContent || "Participant";
  }

  private getParticipantsFromDOM(): Array<{ id: string; name: string }> {
    // Parse participant list from Google Meet DOM
    return [];
  }
}

/**
 * Example: Use with backend API
 */
export async function startScopingSession(
  meetingCode: string,
  voiceflowApiKey: string,
  voiceflowAgentId: string
) {
  const session = new GoogleMeetScopingSession(
    voiceflowApiKey,
    voiceflowAgentId,
    {
      meetingCode,
      meetingTitle: "Technical Project Scoping",
      organizerId: "user_123",
      organizerName: "John Doe",
      startTime: new Date()
    }
  );

  // Setup event handlers
  session.on("session_ended", async (data) => {
    // Save results to database
    await fetch("/api/scoping/sessions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });
  });

  await session.initialize();
  return session;
}

export default {
  GoogleMeetScopingSession,
  GoogleMeetChromeExtension,
  startScopingSession
};
