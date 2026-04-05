/**
 * Theme Composable
 *
 * Manages theme state with localStorage persistence.
 * Supports two themes: dark (default) and gb-automation (light)
 */

import { ref, computed, onMounted } from 'vue'

export type ThemeId = 'dark' | 'gb-automation'

export interface ThemeConfig {
  id: ThemeId
  name: string
  icon: string
  metaColor: string
}

const STORAGE_KEY = 'orchestrator_theme'

// Theme configurations
const themes: Record<ThemeId, ThemeConfig> = {
  dark: {
    id: 'dark',
    name: 'Dark',
    icon: '🌙',
    metaColor: '#1a1a2e'
  },
  'gb-automation': {
    id: 'gb-automation',
    name: 'GB Automation',
    icon: '☀️',
    metaColor: '#F3F1E7'
  }
}

// Available theme IDs for cycling
const themeOrder: ThemeId[] = ['dark', 'gb-automation']

// Global theme state (shared across components)
const currentThemeId = ref<ThemeId>('dark')
let initialized = false

/**
 * Apply theme to document
 */
function applyTheme(themeId: ThemeId) {
  // Add transitioning class to prevent flash
  document.documentElement.classList.add('theme-transitioning')

  // Apply theme
  if (themeId === 'dark') {
    document.documentElement.removeAttribute('data-theme')
  } else {
    document.documentElement.setAttribute('data-theme', themeId)
  }

  // Update meta theme-color for mobile browsers
  const metaThemeColor = document.querySelector('meta[name="theme-color"]')
  if (metaThemeColor) {
    metaThemeColor.setAttribute('content', themes[themeId].metaColor)
  }

  // Remove transitioning class after animation
  setTimeout(() => {
    document.documentElement.classList.remove('theme-transitioning')
  }, 300)
}

/**
 * Save theme to localStorage
 */
function saveTheme(themeId: ThemeId) {
  try {
    localStorage.setItem(STORAGE_KEY, themeId)
  } catch (e) {
    console.warn('Failed to save theme to localStorage:', e)
  }
}

/**
 * Load theme from localStorage
 */
function loadTheme(): ThemeId {
  try {
    const saved = localStorage.getItem(STORAGE_KEY) as ThemeId | null
    if (saved && themes[saved]) {
      return saved
    }
  } catch (e) {
    console.warn('Failed to load theme from localStorage:', e)
  }
  return 'dark'
}

/**
 * Composable for theme management
 */
export function useTheme() {
  /**
   * Set specific theme
   */
  const setTheme = (themeId: ThemeId) => {
    if (!themes[themeId]) {
      console.warn(`Unknown theme: ${themeId}`)
      return
    }
    currentThemeId.value = themeId
    applyTheme(themeId)
    saveTheme(themeId)
  }

  /**
   * Toggle between themes
   */
  const toggleTheme = () => {
    const currentIndex = themeOrder.indexOf(currentThemeId.value)
    const nextIndex = (currentIndex + 1) % themeOrder.length
    setTheme(themeOrder[nextIndex])
  }

  /**
   * Current theme configuration
   */
  const currentThemeConfig = computed(() => themes[currentThemeId.value])

  /**
   * Check if current theme is dark
   */
  const isDark = computed(() => currentThemeId.value === 'dark')

  /**
   * Check if current theme is light (gb-automation)
   */
  const isLight = computed(() => currentThemeId.value === 'gb-automation')

  // Initialize theme on first mount (singleton pattern)
  onMounted(() => {
    if (!initialized) {
      initialized = true
      const savedTheme = loadTheme()
      currentThemeId.value = savedTheme
      applyTheme(savedTheme)
    }
  })

  return {
    currentTheme: currentThemeId,
    currentThemeConfig,
    themes,
    themeOrder,
    setTheme,
    toggleTheme,
    isDark,
    isLight
  }
}
