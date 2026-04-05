<template>
  <button
    class="theme-toggle"
    @click="toggleTheme"
    :title="`Switch to ${currentThemeConfig.id === 'dark' ? 'GB Automation' : 'Dark'} theme`"
    :aria-label="`Current theme: ${currentThemeConfig.name}. Click to switch.`"
  >
    <span class="theme-icon">{{ currentThemeConfig.icon }}</span>
    <span class="theme-label">{{ currentThemeConfig.name }}</span>
  </button>
</template>

<script setup lang="ts">
import { useTheme } from '../composables/useTheme'

const { currentThemeConfig, toggleTheme } = useTheme()
</script>

<style scoped>
.theme-toggle {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
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

.theme-toggle:hover {
  background: var(--bg-quaternary);
  color: var(--text-primary);
  border-color: var(--accent-primary);
  transform: translateY(-1px);
}

.theme-toggle:active {
  transform: translateY(0);
}

.theme-icon {
  font-size: 1rem;
  line-height: 1;
}

.theme-label {
  white-space: nowrap;
}

/* Hide label on smaller screens */
@media (max-width: 1024px) {
  .theme-label {
    display: none;
  }

  .theme-toggle {
    padding: 0.375rem;
  }
}
</style>
