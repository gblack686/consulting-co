/**
 * Example: Testing Obsidian Content with Playwright
 * 
 * This demonstrates a hybrid approach:
 * 1. Export Obsidian content (or simulate it)
 * 2. Test the rendered output with Playwright
 * 3. Validate plugin-specific rendering
 */

const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

/**
 * Option A: Test exported HTML from Obsidian
 * If you can export Obsidian notes to HTML, test them here
 */
test.describe('Obsidian Exported Content', () => {
  test('validates plugin rendering in exported HTML', async ({ page }) => {
    // Load exported HTML file
    const htmlPath = path.join(__dirname, 'exports', 'test-note.html');
    
    if (!fs.existsSync(htmlPath)) {
      test.skip('Export HTML file not found. Export from Obsidian first.');
    }
    
    await page.goto(`file://${htmlPath}`);
    
    // Validate plugin-specific elements
    // Adjust selectors based on your plugins
    await expect(page.locator('.dataview')).toBeVisible();
    await expect(page.locator('.canvas-node')).toHaveCount(2);
    
    // Visual regression test
    await expect(page).toHaveScreenshot('obsidian-export.png', {
      maxDiffPixels: 100, // Allow small rendering differences
    });
  });
});

/**
 * Option B: Test markdown rendered with Obsidian's renderer
 * Simulate Obsidian's rendering in a web context
 */
test.describe('Obsidian Markdown Rendering', () => {
  test('renders markdown with plugin syntax', async ({ page }) => {
    const markdown = `
# Test Note

Regular markdown content.

\`\`\`dataview
TABLE file.name, file.mtime
FROM "Projects"
\`\`\`

\`\`\`canvas
- Node 1
- Node 2
\`\`\`
    `;
    
    // Create HTML that mimics Obsidian's rendering
    const html = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
    .markdown-preview-view { padding: 20px; max-width: 800px; margin: 0 auto; }
    .dataview { background: #f5f5f5; padding: 10px; border-radius: 4px; }
    .canvas-node { border: 1px solid #ccc; padding: 10px; margin: 10px 0; }
  </style>
</head>
<body>
  <div class="markdown-preview-view">
    ${renderMarkdownWithPlugins(markdown)}
  </div>
</body>
</html>
    `;
    
    await page.setContent(html);
    
    // Validate plugin blocks are rendered
    await expect(page.locator('.dataview')).toBeVisible();
    await expect(page.locator('.canvas-node')).toHaveCount(2);
    
    // Visual snapshot
    await expect(page).toHaveScreenshot('obsidian-render.png');
  });
});

/**
 * Option C: Test via Electron CDP (if remote debugging enabled)
 */
test.describe('Obsidian via Electron CDP', () => {
  test('connects to Obsidian via Chrome DevTools Protocol', async ({ browser }) => {
    // This requires Obsidian to be launched with --remote-debugging-port=9222
    const cdpBrowser = await browser.browserType().connectOverCDP('http://localhost:9222');
    
    if (!cdpBrowser) {
      test.skip('Obsidian remote debugging not available. Launch with --remote-debugging-port=9222');
    }
    
    const pages = await cdpBrowser.pages();
    const obsidianPage = pages.find(p => p.url().includes('obsidian'));
    
    if (!obsidianPage) {
      test.skip('Could not find Obsidian page in CDP connection');
    }
    
    // Take screenshot of Obsidian UI
    await obsidianPage.screenshot({ path: 'obsidian-ui.png' });
    
    // Validate UI elements
    await expect(obsidianPage.locator('.workspace')).toBeVisible();
  });
});

/**
 * Helper: Render markdown with plugin syntax
 * In real usage, you'd use Obsidian's actual renderer or a compatible library
 */
function renderMarkdownWithPlugins(markdown) {
  // This is a simplified example
  // In production, you'd use a markdown renderer that supports Obsidian plugins
  
  let html = markdown;
  
  // Convert dataview blocks
  html = html.replace(
    /```dataview\n([\s\S]*?)```/g,
    '<div class="dataview">$1</div>'
  );
  
  // Convert canvas blocks
  html = html.replace(
    /```canvas\n([\s\S]*?)```/g,
    (match, content) => {
      const nodes = content.split('\n').filter(line => line.trim().startsWith('-'));
      return nodes.map(node => `<div class="canvas-node">${node}</div>`).join('');
    }
  );
  
  // Basic markdown (you'd use a proper markdown parser)
  html = html.replace(/^# (.*$)/gm, '<h1>$1</h1>');
  
  return html;
}

/**
 * Option D: Desktop Automation Integration
 * Use this with Appium or WinAppDriver for full desktop testing
 */
async function testObsidianDesktop() {
  // This would require Appium or similar
  // Example structure:
  
  /*
  const { remote } = require('webdriverio');
  
  const client = await remote({
    capabilities: {
      platformName: 'Windows',
      app: 'C:\\Users\\...\\Obsidian.exe',
      automationName: 'Windows'
    }
  });
  
  // Find and interact with Obsidian UI elements
  const noteEditor = await client.$('//*[@Name="Editor"]');
  await noteEditor.setValue('# Test Note\n\nContent here');
  
  // Take screenshot
  await client.saveScreenshot('obsidian-desktop.png');
  */
}
