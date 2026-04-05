<template>
  <header class="app-header">
    <div class="header-content">
      <div class="header-title">
        <h1>MULTI-AGENT ORCHESTRATION</h1>
        <div class="header-subtitle-group">
          <span class="header-subtitle">LIVE LOG STREAM</span>
          <div
            class="connection-status"
            :class="{ clickable: !store.isConnected }"
            @click="!store.isConnected && store.reconnectWebSocket()"
            :title="store.isConnected ? 'WebSocket connected' : 'Click to reconnect'"
          >
            <span class="status-indicator" :class="{ online: store.isConnected }"></span>
            <span class="status-text">{{
              store.isConnected ? "Connected" : "Disconnected"
            }}</span>
            <button
              v-if="!store.isConnected"
              class="btn-reconnect"
              @click.stop="store.reconnectWebSocket()"
            >
              Reconnect
            </button>
          </div>
        </div>
      </div>
      <div class="header-right">
        <div class="header-stats">
          <div class="stat-item stat-pill">
            <span class="stat-label">Active:</span>
            <span class="stat-value">{{ headerBar.activeAgentCount }}</span>
          </div>
          <div class="stat-item stat-pill">
            <span class="stat-label">Running:</span>
            <span class="stat-value">{{ headerBar.runningAgentCount }}</span>
          </div>
          <div class="stat-item stat-pill">
            <span class="stat-label">Logs:</span>
            <span class="stat-value">{{ headerBar.logCount }}</span>
          </div>
          <div class="stat-item stat-pill">
            <span class="stat-label">Cost:</span>
            <span class="stat-value">${{ headerBar.formattedCost }}</span>
          </div>
        </div>

        <div class="header-actions">
          <button class="btn-settings" @click="showSettings = true" title="Settings">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="3"></circle>
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
            </svg>
          </button>
          <ThemeToggle />
          <button class="btn-export" @click="headerBar.exportEventStream" title="Export event stream">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="7,10 12,15 17,10"></polyline>
              <line x1="12" y1="15" x2="12" y2="3"></line>
            </svg>
          </button>
          <button class="btn-clear" @click="headerBar.clearEventStream">
            CLEAR ALL
          </button>
          <button
            class="btn-prompt"
            :class="{ active: store.commandInputVisible }"
            @click="store.toggleCommandInput"
            title="Toggle command input (Cmd+K / Ctrl+K)"
          >
            PROMPT <span class="btn-hint">(Cmd+K)</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Settings Modal -->
    <SettingsModal :visible="showSettings" @close="showSettings = false" />
  </header>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useHeaderBar } from "../composables/useHeaderBar";
import { useOrchestratorStore } from '../stores/orchestratorStore';
import SettingsModal from './SettingsModal.vue';
import ThemeToggle from './ThemeToggle.vue';

// Use header bar composable for state management
const headerBar = useHeaderBar();

// Use store for command input visibility
const store = useOrchestratorStore();

// Settings modal visibility
const showSettings = ref(false);
</script>

<style scoped>
/* Header */
.app-header {
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  padding: var(--spacing-md) var(--spacing-lg);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 100%;
}

.header-title {
  display: flex;
  align-items: baseline;
  gap: var(--spacing-md);
  flex-wrap: wrap;
}

.header-subtitle-group {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.header-title h1 {
  font-size: 1rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: var(--text-primary);
  margin: 0;
}

.header-subtitle {
  font-size: 0.875rem;
  color: var(--accent-primary);
  font-weight: 600;
  letter-spacing: 0.025em;
}

.connection-status {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  font-size: 0.75rem;
  color: var(--text-muted);
  padding-left: var(--spacing-md);
  border-left: 1px solid var(--border-color);
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--text-muted);
}

.status-indicator.online {
  background: var(--status-success);
  box-shadow: 0 0 8px rgba(16, 185, 129, 0.5);
}

.status-text {
  font-weight: 500;
}

.connection-status.clickable {
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  margin-left: calc(var(--spacing-md) * -1);
  padding-left: var(--spacing-md);
  transition: background 0.2s ease;
}

.connection-status.clickable:hover {
  background: var(--bg-tertiary);
}

.btn-reconnect {
  margin-left: var(--spacing-sm);
  padding: 0.25rem 0.5rem;
  font-size: 0.65rem;
  font-weight: 600;
  letter-spacing: 0.025em;
  border-radius: 4px;
  background: var(--accent-primary);
  color: white;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-reconnect:hover {
  background: var(--accent-secondary);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(6, 182, 212, 0.3);
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--spacing-xl);
}

.header-stats {
  display: flex;
  gap: var(--spacing-xl);
}

.header-actions {
  display: flex;
  gap: var(--spacing-sm);
  padding-left: var(--spacing-xl);
  border-left: 1px solid var(--border-color);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  font-size: 0.875rem;
}

.stat-label {
  color: var(--text-muted);
  font-weight: 500;
}

.stat-value {
  color: var(--text-primary);
  font-weight: 700;
  font-family: var(--font-mono);
}

/* Stat Pills - Flat Gray Badge Style */
.stat-pill {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-xs);
  padding: 0.375rem 0.75rem;
  background: var(--bg-tertiary);
  border-radius: 12px;
  font-size: 0.875rem;
  border: 1px solid var(--border-light);
  transition: all 0.2s ease;
  white-space: nowrap;
}

.stat-pill:hover {
  background: var(--bg-quaternary);
  border-color: var(--border-color);
}

.stat-pill .stat-label {
  color: var(--text-muted);
  font-weight: 500;
  font-size: 0.8125rem;
}

.stat-pill .stat-value {
  color: var(--text-primary);
  font-weight: 700;
  font-family: var(--font-mono);
  font-size: 0.875rem;
}

/* Action Buttons */
.btn-prompt,
.btn-clear {
  padding: 0.375rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.025em;
  border-radius: 4px;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-hint {
  font-size: 0.65rem;
  font-weight: 500;
  opacity: 0.7;
  margin-left: 0.25rem;
}

.btn-prompt:hover,
.btn-clear:hover {
  background: var(--bg-quaternary);
  color: var(--text-primary);
  border-color: var(--accent-primary);
  transform: translateY(-1px);
}

.btn-prompt.active {
  background: var(--accent-primary);
  color: white;
  border-color: var(--accent-primary);
  box-shadow: 0 0 10px rgba(6, 182, 212, 0.3);
}

.btn-settings {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.375rem;
  border-radius: 4px;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-settings:hover,
.btn-export:hover {
  background: var(--bg-quaternary);
  color: var(--text-primary);
  border-color: var(--accent-primary);
}

.btn-settings svg,
.btn-export svg {
  display: block;
}

.btn-export {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.375rem;
  border-radius: 4px;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
  cursor: pointer;
  transition: all 0.2s ease;
}

/* Responsive */
@media (max-width: 1200px) {
  .header-stats {
    gap: var(--spacing-md);
  }
}

@media (max-width: 1024px) {
  .header-title h1 {
    font-size: 0.875rem;
  }

  .header-subtitle {
    font-size: 0.75rem;
  }
}
</style>
