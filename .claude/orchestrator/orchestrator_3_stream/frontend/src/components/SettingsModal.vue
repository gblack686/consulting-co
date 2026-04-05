<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="visible" class="modal-overlay" @click.self="$emit('close')">
        <div class="modal-container">
          <div class="modal-header">
            <h2>Settings</h2>
            <button class="close-btn" @click="$emit('close')" title="Close">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </button>
          </div>

          <div class="modal-body">
            <!-- Working Directory Section -->
            <section class="settings-section">
              <WorkingDirSelector />
            </section>

            <!-- Divider -->
            <hr class="settings-divider" />

            <!-- Connection Status Section -->
            <section class="settings-section">
              <label class="setting-label">WebSocket Connection</label>
              <div class="connection-row">
                <div
                  class="connection-status"
                  :class="{
                    connected: store.isConnected && !isReconnecting,
                    reconnecting: isReconnecting,
                    disconnected: !store.isConnected && !isReconnecting
                  }"
                >
                  <span class="status-dot"></span>
                  {{ isReconnecting ? 'Reconnecting...' : (store.isConnected ? 'Connected' : 'Disconnected') }}
                </div>
                <button
                  class="reconnect-btn"
                  :class="{ spinning: isReconnecting }"
                  @click="handleReconnect"
                  :disabled="isReconnecting"
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="23 4 23 10 17 10"></polyline>
                    <polyline points="1 20 1 14 7 14"></polyline>
                    <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
                  </svg>
                  {{ isReconnecting ? 'Reconnecting...' : 'Reconnect' }}
                </button>
              </div>
            </section>

            <!-- Divider -->
            <hr class="settings-divider" />

            <!-- Session Info Section -->
            <section class="settings-section">
              <label class="setting-label">Session Information</label>
              <div class="info-grid">
                <div class="info-item">
                  <span class="info-label">Orchestrator ID</span>
                  <code class="info-value">{{ store.orchestratorAgent?.id || 'N/A' }}</code>
                </div>
                <div class="info-item">
                  <span class="info-label">Session ID</span>
                  <code class="info-value">{{ store.orchestratorAgent?.session_id || 'Not set' }}</code>
                </div>
                <div class="info-item">
                  <span class="info-label">Status</span>
                  <span class="info-value status-badge" :class="store.orchestratorAgent?.status">
                    {{ store.orchestratorAgent?.status || 'Unknown' }}
                  </span>
                </div>
              </div>
            </section>
          </div>

          <div class="modal-footer">
            <button class="btn-secondary" @click="$emit('close')">Close</button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useOrchestratorStore } from '../stores/orchestratorStore';
import WorkingDirSelector from './WorkingDirSelector.vue';

defineProps<{
  visible: boolean;
}>();

defineEmits<{
  (e: 'close'): void;
}>();

const store = useOrchestratorStore();

// Reconnecting state for visual feedback
const isReconnecting = ref(false);

// Handle reconnect with visual feedback
const handleReconnect = async () => {
  if (isReconnecting.value) return;

  // Start reconnecting - shows red status
  isReconnecting.value = true;

  // Force disconnect first
  store.disconnectWebSocket();

  // Brief delay to show disconnected state
  await new Promise(resolve => setTimeout(resolve, 500));

  // Reconnect
  store.connectWebSocket();

  // Wait for connection to establish, then clear reconnecting state
  await new Promise(resolve => setTimeout(resolve, 1000));
  isReconnecting.value = false;
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-container {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  width: 90%;
  max-width: 560px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-lg);
  border-bottom: 1px solid var(--border-color);
}

.modal-header h2 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
}

.close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.25rem;
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-lg);
}

.settings-section {
  margin-bottom: var(--spacing-lg);
}

.settings-section:last-child {
  margin-bottom: 0;
}

.setting-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--spacing-sm);
}

.settings-divider {
  border: none;
  border-top: 1px solid var(--border-color);
  margin: var(--spacing-lg) 0;
}

.info-grid {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.info-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--bg-tertiary);
  border-radius: 6px;
}

.info-label {
  font-size: 0.8125rem;
  color: var(--text-muted);
}

.info-value {
  font-size: 0.8125rem;
  font-family: var(--font-mono);
  color: var(--text-primary);
  max-width: 280px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.status-badge {
  padding: 0.125rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  font-family: var(--font-sans);
}

.status-badge.idle {
  background: rgba(6, 182, 212, 0.15);
  color: var(--accent-primary);
}

.status-badge.executing {
  background: rgba(16, 185, 129, 0.15);
  color: var(--status-success);
}

.status-badge.blocked {
  background: rgba(245, 158, 11, 0.15);
  color: var(--status-warning);
}

/* Connection Section */
.connection-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--bg-tertiary);
  border-radius: 6px;
}

.connection-status {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  font-size: 0.8125rem;
  color: var(--text-muted);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--text-muted);
  transition: all 0.3s ease;
}

.connection-status.connected .status-dot {
  background: var(--status-success, #10b981);
  box-shadow: 0 0 8px rgba(16, 185, 129, 0.5);
}

.connection-status.connected {
  color: var(--status-success, #10b981);
}

.connection-status.disconnected .status-dot {
  background: var(--status-error, #ef4444);
}

.connection-status.disconnected {
  color: var(--status-error, #ef4444);
}

.connection-status.reconnecting .status-dot {
  background: var(--status-warning, #f59e0b);
  box-shadow: 0 0 8px rgba(245, 158, 11, 0.5);
  animation: pulse-dot 0.8s ease-in-out infinite;
}

.connection-status.reconnecting {
  color: var(--status-warning, #f59e0b);
}

@keyframes pulse-dot {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.5;
    transform: scale(1.2);
  }
}

/* Reconnect Button */
.reconnect-btn {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-xs) var(--spacing-sm);
  background: var(--bg-quaternary, var(--bg-secondary));
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--text-secondary);
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.reconnect-btn:hover:not(:disabled) {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border-color: var(--accent-primary);
}

.reconnect-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.reconnect-btn.spinning {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.reconnect-btn.spinning svg {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  padding: var(--spacing-md) var(--spacing-lg);
  border-top: 1px solid var(--border-color);
}

.btn-secondary {
  padding: 0.5rem 1rem;
  font-size: 0.8125rem;
  font-weight: 600;
  border-radius: 6px;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: var(--bg-quaternary);
  color: var(--text-primary);
}

/* Modal Transitions */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-active .modal-container,
.modal-leave-active .modal-container {
  transition: transform 0.2s ease, opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.95);
  opacity: 0;
}
</style>
