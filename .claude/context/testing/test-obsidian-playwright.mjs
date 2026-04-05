/**
 * Test: Can Playwright connect to Obsidian (Electron app)?
 *
 * Approach: Launch Obsidian with --remote-debugging-port=9222
 * then connect via CDP (Chrome DevTools Protocol).
 */

import { chromium } from 'playwright';
import { exec, spawn } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);
const OBSIDIAN_PATH = 'C:\\Users\\gblac\\AppData\\Local\\Programs\\Obsidian\\Obsidian.exe';
const DEBUG_PORT = 9229;

async function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

async function testObsidianCDP() {
  console.log('=== Playwright + Obsidian (Electron/CDP) Test ===\n');

  // Step 1: Launch Obsidian with remote debugging
  console.log(`[1] Launching Obsidian with --remote-debugging-port=${DEBUG_PORT}...`);
  const obsidian = spawn(OBSIDIAN_PATH, [`--remote-debugging-port=${DEBUG_PORT}`], {
    detached: true,
    stdio: 'ignore',
  });
  obsidian.unref();

  // Give it time to start
  console.log('[2] Waiting 5s for Obsidian to start...');
  await sleep(5000);

  // Step 2: Try connecting via CDP
  console.log(`[3] Connecting Playwright via CDP to localhost:${DEBUG_PORT}...`);
  let browser;
  try {
    browser = await chromium.connectOverCDP(`http://localhost:${DEBUG_PORT}`);
    console.log('✅ Connected to Obsidian via CDP!');

    const contexts = browser.contexts();
    console.log(`[4] Found ${contexts.length} browser context(s)`);

    for (const ctx of contexts) {
      const pages = ctx.pages();
      console.log(`    Context has ${pages.length} page(s)`);
      for (const page of pages) {
        const url = page.url();
        const title = await page.title().catch(() => '(error)');
        console.log(`    → Page: "${title}" | URL: ${url}`);
      }
    }

    // Try taking a screenshot of first page
    const allPages = contexts.flatMap(c => c.pages());
    if (allPages.length > 0) {
      const screenshot = await allPages[0].screenshot({ path: '.claude/context/testing/obsidian-screenshot.png' }).catch(e => e);
      if (screenshot instanceof Error) {
        console.log(`[5] Screenshot failed: ${screenshot.message}`);
      } else {
        console.log('[5] ✅ Screenshot saved: obsidian-screenshot.png');
      }
    }

    await browser.close();
  } catch (err) {
    console.log(`❌ CDP connection failed: ${err.message}`);
    console.log('\nThis is expected — Obsidian may not expose CDP without special flags.');
    console.log('See fallback options below.');
  }
}

async function testObsidianPublish() {
  console.log('\n=== Testing Obsidian Publish (Web Version) ===\n');

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  try {
    // Obsidian Publish is the closest to a "web version"
    await page.goto('https://publish.obsidian.md', { waitUntil: 'domcontentloaded', timeout: 10000 });
    const title = await page.title();
    const url = page.url();
    console.log(`✅ Obsidian Publish loaded: "${title}"`);
    console.log(`   Final URL: ${url}`);

    // Check for Obsidian-specific elements
    const hasObsidianBranding = await page.locator('text=Obsidian').count();
    console.log(`   Obsidian branding elements found: ${hasObsidianBranding}`);

    await page.screenshot({ path: '.claude/context/testing/obsidian-publish-screenshot.png' });
    console.log('✅ Screenshot saved: obsidian-publish-screenshot.png');

  } catch (err) {
    console.log(`❌ Failed: ${err.message}`);
  } finally {
    await browser.close();
  }
}

// Main
(async () => {
  await testObsidianPublish();  // Test web version first (no Obsidian needed)
  await testObsidianCDP();      // Then try connecting to running Obsidian

  console.log('\n=== Summary ===');
  console.log('• Obsidian Publish = testable web UI (standard Playwright)');
  console.log('• Local Obsidian   = needs CDP or Electron testing tools');
  console.log('• Best bet for local: Export notes → test HTML with Playwright');
})();
