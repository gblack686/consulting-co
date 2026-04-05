# Testing Obsidian with Playwright

## Overview
Obsidian is an Electron-based desktop application. While Playwright is primarily for web apps, there are ways to test Electron apps if they expose debugging capabilities.

## Option 1: Electron Remote Debugging (If Available)

### Check if Obsidian supports remote debugging:
1. Launch Obsidian with remote debugging enabled:
   ```bash
   # Windows
   obsidian.exe --remote-debugging-port=9222
   
   # macOS
   /Applications/Obsidian.app/Contents/MacOS/Obsidian --remote-debugging-port=9222
   ```

2. Connect Playwright to the Electron instance:
   ```javascript
   const { chromium } = require('playwright');
   
   const browser = await chromium.connectOverCDP('http://localhost:9222');
   const pages = await browser.pages();
   const obsidianPage = pages[0]; // or find the correct page
   
   // Now you can interact with Obsidian's UI
   await obsidianPage.screenshot({ path: 'obsidian-ui.png' });
   ```

### Limitations:
- Obsidian may not expose remote debugging by default
- Plugin rendering might be in separate contexts
- Custom rendering may not be accessible via CDP

## Option 2: Screenshot-Based Visual Testing

Use Playwright to automate screenshot capture, then compare visually:

```javascript
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

async function captureObsidianScreenshot(obsidianWindow) {
  // Use Playwright to take screenshots of the desktop window
  // This requires additional tools like:
  // - Playwright's experimental desktop support
  // - Or screenshot tools that can capture specific windows
}
```

**Tools for desktop screenshot capture:**
- `screenshot-desktop` (Node.js)
- `robotjs` (for window manipulation)
- `spectron` (Electron-specific, deprecated but still works)

## Option 3: Hybrid Approach - Export & Test Web Version

1. **Export Obsidian content to HTML** (if plugin supports it)
2. **Test the exported HTML with Playwright**:

```javascript
const { test, expect } = require('@playwright/test');

test('Obsidian plugin renders correctly', async ({ page }) => {
  // Load exported HTML
  await page.goto('file:///path/to/exported-obsidian-note.html');
  
  // Validate plugin-specific elements
  await expect(page.locator('.plugin-custom-element')).toBeVisible();
  
  // Visual regression test
  await expect(page).toHaveScreenshot('obsidian-plugin-render.png');
});
```

## Option 4: Use Desktop-Specific Testing Tools

For true desktop app testing, consider:

### Windows:
- **WinAppDriver** - Microsoft's UI Automation
- **Appium** - Cross-platform with WinAppDriver backend
- **pywinauto** - Python-based Windows automation

### macOS:
- **XCUITest** - Apple's UI testing framework
- **Appium** - With XCUITest backend

### Cross-platform:
- **Spectron** (deprecated but functional) - Electron-specific
- **Playwright for Electron** (experimental) - Direct Electron support

## Option 5: Create a Test Web Interface

Build a minimal web version that renders Obsidian content:

```javascript
// test-obsidian-web.js
const { test, expect } = require('@playwright/test');
const fs = require('fs');

test('Obsidian markdown with plugins', async ({ page }) => {
  // Read Obsidian note
  const noteContent = fs.readFileSync('test-note.md', 'utf-8');
  
  // Create HTML wrapper with Obsidian's CSS/JS
  const html = `
    <!DOCTYPE html>
    <html>
      <head>
        <link rel="stylesheet" href="obsidian-theme.css">
        <script src="obsidian-plugins.js"></script>
      </head>
      <body>
        <div class="markdown-preview-view">
          ${renderMarkdown(noteContent)}
        </div>
      </body>
    </html>
  `;
  
  await page.setContent(html);
  await expect(page).toHaveScreenshot('obsidian-render.png');
});
```

## Recommended Approach for Obsidian

Given Obsidian's plugin architecture, I recommend:

1. **For plugin development**: Create a test harness that:
   - Exports plugin-rendered content to HTML
   - Tests the HTML with Playwright's visual regression
   - Validates plugin-specific DOM elements

2. **For full app testing**: Use desktop automation tools:
   ```javascript
   // Example with Appium (if configured)
   const { remote } = require('webdriverio');
   
   const client = await remote({
     capabilities: {
       platformName: 'Windows',
       app: 'C:\\Users\\...\\Obsidian.exe',
       automationName: 'Windows'
     }
   });
   ```

3. **For visual validation**: Use screenshot comparison tools:
   - **Percy** - Visual testing service
   - **Chromatic** - Component visual testing
   - **BackstopJS** - Visual regression testing

## Example: Playwright + Screenshot Comparison

```javascript
const { chromium } = require('playwright');
const { execSync } = require('child_process');
const fs = require('fs');

async function testObsidianNote(notePath) {
  // 1. Open Obsidian and navigate to note (using desktop automation)
  // 2. Take screenshot using system tools
  execSync(`screencapture -l${windowId} obsidian-current.png`);
  
  // 3. Compare with baseline using Playwright's image comparison
  const { compareImages } = require('playwright-core/lib/utils');
  const diff = await compareImages(
    fs.readFileSync('obsidian-baseline.png'),
    fs.readFileSync('obsidian-current.png')
  );
  
  if (diff.ratio > 0.01) { // 1% difference threshold
    throw new Error('Visual regression detected');
  }
}
```

## Conclusion

**Playwright alone cannot directly test Obsidian** because:
- It's designed for web browsers
- Obsidian is a native desktop app
- Plugins use custom rendering

**Best solutions:**
1. Export → Test HTML with Playwright (for plugin content)
2. Desktop automation tools (Appium/WinAppDriver) for full app
3. Screenshot comparison for visual regression
4. Hybrid: Desktop automation + Playwright for exported content
