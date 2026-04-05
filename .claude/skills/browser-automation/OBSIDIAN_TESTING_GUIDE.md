# Testing Obsidian UI with Playwright - Quick Guide

## TL;DR

**Playwright cannot directly test Obsidian** (it's a desktop app), but you have these options:

1. ✅ **Export → Test HTML** - Export Obsidian notes to HTML, test with Playwright
2. ✅ **Electron CDP** - Connect via Chrome DevTools Protocol (if enabled)
3. ✅ **Desktop Automation** - Use Appium/WinAppDriver for full app testing
4. ✅ **Screenshot Comparison** - Capture screenshots, compare with Playwright's image tools

## Quick Start: Export & Test Approach

This is the most practical approach for validating plugin rendering:

### Step 1: Export from Obsidian
```bash
# In Obsidian, export your note to HTML
# File → Export → HTML
```

### Step 2: Test with Playwright
```javascript
const { test, expect } = require('@playwright/test');

test('Obsidian plugin renders', async ({ page }) => {
  await page.goto('file:///path/to/exported-note.html');
  
  // Validate plugin elements
  await expect(page.locator('.dataview')).toBeVisible();
  
  // Visual regression
  await expect(page).toHaveScreenshot('obsidian-plugin.png');
});
```

## Alternative: Electron Remote Debugging

If Obsidian supports it (may require custom build):

```bash
# Launch Obsidian with remote debugging
obsidian.exe --remote-debugging-port=9222
```

```javascript
const { chromium } = require('playwright');
const browser = await chromium.connectOverCDP('http://localhost:9222');
const pages = await browser.pages();
// Interact with Obsidian pages...
```

## Desktop App Testing Tools

For full desktop automation (not Playwright):

| Tool | Platform | Best For |
|------|----------|----------|
| **Appium** | Cross-platform | Full desktop automation |
| **WinAppDriver** | Windows | Native Windows apps |
| **XCUITest** | macOS | Native macOS apps |
| **Spectron** | Electron | Electron apps (deprecated) |

## Recommended Workflow

1. **For Plugin Development:**
   - Export test notes to HTML
   - Use Playwright to validate HTML rendering
   - Visual regression testing with `toHaveScreenshot()`

2. **For Full App Testing:**
   - Use Appium or WinAppDriver
   - Screenshot comparison for visual validation
   - Hybrid: Desktop automation + Playwright for exported content

3. **For CI/CD:**
   - Export → Test HTML (fastest, most reliable)
   - Screenshot comparison as regression tests

## Example Files

- `obsidian-playwright-test.md` - Detailed guide
- `test-obsidian-example.js` - Working code examples

## Key Insight

**The problem:** Obsidian plugins use custom rendering that won't show in standard markdown viewers.

**The solution:** Export the rendered output (HTML) and test that with Playwright. This validates what users actually see, including plugin rendering.
