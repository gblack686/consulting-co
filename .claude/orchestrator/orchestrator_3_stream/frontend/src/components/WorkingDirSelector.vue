<template>
  <div class="working-dir-selector">
    <label class="setting-label">Working Directory</label>
    <p class="setting-description">
      The directory where agents will operate. Changing this creates a new orchestrator session.
    </p>
    <div class="input-group">
      <input
        type="text"
        class="dir-input"
        v-model="inputPath"
        placeholder="Enter path to working directory..."
        :disabled="isLoading || isBrowsing"
        @keydown.enter="applyChange"
      />
      <button
        class="browse-btn"
        @click="openFolderPicker"
        :disabled="isLoading || isBrowsing"
        title="Browse for folder"
      >
        {{ isBrowsing ? '...' : 'Browse' }}
      </button>
      <button
        class="apply-btn"
        @click="applyChange"
        :disabled="isLoading || !hasChanged"
        :class="{ loading: isLoading }"
      >
        {{ isLoading ? 'Applying...' : 'Apply' }}
      </button>
    </div>
    <div v-if="error" class="error-message">{{ error }}</div>
    <div v-if="successMessage" class="success-message">{{ successMessage }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useOrchestratorStore } from '../stores/orchestratorStore'
import { browseFolder } from '../services/chatService'

const store = useOrchestratorStore()

const inputPath = ref('')
const originalPath = ref('')
const isLoading = ref(false)
const isBrowsing = ref(false)
const error = ref('')
const successMessage = ref('')

const hasChanged = computed(() => {
  return inputPath.value !== originalPath.value && inputPath.value.trim() !== ''
})

// Initialize with current working directory
onMounted(() => {
  if (store.orchestratorAgent?.working_dir) {
    inputPath.value = store.orchestratorAgent.working_dir
    originalPath.value = store.orchestratorAgent.working_dir
  }
})

// Watch for orchestrator changes to update the displayed path
watch(() => store.orchestratorAgent?.working_dir, (newDir) => {
  if (newDir) {
    inputPath.value = newDir
    originalPath.value = newDir
  }
})

async function applyChange() {
  if (!hasChanged.value || isLoading.value) return

  error.value = ''
  successMessage.value = ''
  isLoading.value = true

  try {
    await store.changeWorkingDir(inputPath.value)
    originalPath.value = inputPath.value
    successMessage.value = 'Working directory changed successfully!'

    // Clear success message after 3 seconds
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  } catch (err: any) {
    error.value = err.message || 'Failed to change working directory'
  } finally {
    isLoading.value = false
  }
}

async function openFolderPicker() {
  if (isBrowsing.value) return

  error.value = ''
  isBrowsing.value = true

  try {
    const result = await browseFolder()

    if (result.status === 'success' && result.path) {
      inputPath.value = result.path
    } else if (result.status === 'error') {
      error.value = result.error || 'Failed to open folder picker'
    }
    // If cancelled, do nothing
  } catch (err: any) {
    error.value = err.message || 'Failed to open folder picker'
  } finally {
    isBrowsing.value = false
  }
}
</script>

<style scoped>
.working-dir-selector {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.setting-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0;
}

.setting-description {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin: 0 0 var(--spacing-xs) 0;
}

.input-group {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.dir-input {
  flex: 1;
  padding: 0.5rem 0.75rem;
  font-size: 0.8125rem;
  font-family: var(--font-mono);
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  outline: none;
  transition: all 0.2s ease;
}

.dir-input:focus {
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 2px rgba(6, 182, 212, 0.1);
}

.dir-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.dir-input::placeholder {
  color: var(--text-muted);
}

.browse-btn {
  padding: 0.5rem 0.75rem;
  font-size: 0.8125rem;
  font-weight: 600;
  border-radius: 6px;
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.browse-btn:hover:not(:disabled) {
  background: var(--bg-quaternary);
  color: var(--text-primary);
  border-color: var(--accent-primary);
}

.browse-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.apply-btn {
  padding: 0.5rem 1rem;
  font-size: 0.8125rem;
  font-weight: 600;
  border-radius: 6px;
  background: var(--accent-primary);
  color: white;
  border: 1px solid var(--accent-primary);
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.apply-btn:hover:not(:disabled) {
  background: var(--accent-secondary);
  border-color: var(--accent-secondary);
}

.apply-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.apply-btn.loading {
  background: var(--bg-tertiary);
  color: var(--text-muted);
  border-color: var(--border-color);
}

.error-message {
  font-size: 0.75rem;
  color: var(--status-error);
  padding: 0.25rem 0;
}

.success-message {
  font-size: 0.75rem;
  color: var(--status-success);
  padding: 0.25rem 0;
}
</style>
