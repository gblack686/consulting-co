"""
Test: Playwright options for Obsidian and desktop apps.
Uses Python playwright (pip install playwright).
"""

import subprocess
import time
import sys
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


def test_obsidian_publish():
    """Test Obsidian Publish — the actual web version of Obsidian."""
    print("=== Test 1: Obsidian Publish (Web Version) ===\n")
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto("https://publish.obsidian.md", wait_until="domcontentloaded", timeout=15000)
            title = page.title()
            url = page.url
            print(f"✅ Loaded: \"{title}\"")
            print(f"   Final URL: {url}")

            # Check Obsidian-specific elements
            count = page.locator("text=Obsidian").count()
            print(f"   'Obsidian' text elements: {count}")

            shot = os.path.join(OUTPUT_DIR, "obsidian-publish.png")
            page.screenshot(path=shot)
            print(f"✅ Screenshot saved: {shot}")
            return True
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False
        finally:
            browser.close()


def test_obsidian_cdp():
    """Try connecting to running Obsidian via CDP (Electron remote debugging)."""
    print("\n=== Test 2: Obsidian Local App via CDP ===\n")

    OBSIDIAN_EXE = r"C:\Users\gblac\AppData\Local\Programs\Obsidian\Obsidian.exe"
    DEBUG_PORT = 9229

    # Launch Obsidian with remote debugging
    print(f"[1] Starting Obsidian with --remote-debugging-port={DEBUG_PORT}...")
    proc = subprocess.Popen(
        [OBSIDIAN_EXE, f"--remote-debugging-port={DEBUG_PORT}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    print("[2] Waiting 6s for Obsidian to initialize...")
    time.sleep(6)

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(f"http://localhost:{DEBUG_PORT}")
            print("✅ Connected to Obsidian via CDP!")

            contexts = browser.contexts
            print(f"[3] Found {len(contexts)} context(s)")

            for i, ctx in enumerate(contexts):
                pages = ctx.pages
                print(f"    Context {i}: {len(pages)} page(s)")
                for pg in pages:
                    try:
                        print(f"      → Title: \"{pg.title()}\" | URL: {pg.url}")
                    except Exception:
                        print(f"      → (could not read page info)")

            # Screenshot first available page
            all_pages = [pg for ctx in contexts for pg in ctx.pages]
            if all_pages:
                try:
                    shot = os.path.join(OUTPUT_DIR, "obsidian-cdp.png")
                    all_pages[0].screenshot(path=shot)
                    print(f"✅ Screenshot saved: {shot}")
                except Exception as e:
                    print(f"   Screenshot failed: {e}")

            browser.close()
            result = True
        except Exception as e:
            print(f"❌ CDP connection failed: {e}")
            print("\n   This is expected — Electron apps often block CDP by default.")
            print("   Obsidian may need a special build flag to expose debugging.")
            result = False

    proc.terminate()
    return result


def test_playwright_capabilities():
    """Demonstrate what Playwright CAN test (Obsidian exported HTML)."""
    print("\n=== Test 3: Playwright on Local HTML (Obsidian Export Simulation) ===\n")

    # Create a minimal HTML that mimics Obsidian's rendered note
    html_path = os.path.join(OUTPUT_DIR, "obsidian-note-mock.html")
    with open(html_path, "w") as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
  <title>My Note - Obsidian Export</title>
  <style>
    body { font-family: -apple-system, sans-serif; padding: 2rem; }
    .dataview { background: #f0f0f0; padding: 1rem; border-radius: 4px; }
    h1 { color: #7c3aed; }
  </style>
</head>
<body>
  <h1>My Test Note</h1>
  <p>This simulates an Obsidian exported note.</p>
  <div class="dataview">
    <strong>Dataview Plugin</strong><br>
    - Task 1: Complete<br>
    - Task 2: In progress
  </div>
</body>
</html>""")

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(f"file:///{html_path.replace(os.sep, '/')}")
            title = page.title()
            h1 = page.locator("h1").text_content()
            dataview = page.locator(".dataview").is_visible()

            print(f"✅ Loaded: \"{title}\"")
            print(f"   H1 text: \"{h1}\"")
            print(f"   Dataview element visible: {dataview}")

            shot = os.path.join(OUTPUT_DIR, "obsidian-export-test.png")
            page.screenshot(path=shot)
            print(f"✅ Screenshot saved: {shot}")
            return True
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False
        finally:
            browser.close()


if __name__ == "__main__":
    results = {}
    results["obsidian_publish"] = test_obsidian_publish()
    results["local_html"] = test_playwright_capabilities()
    results["cdp_electron"] = test_obsidian_cdp()

    print("\n" + "=" * 50)
    print("RESULTS SUMMARY")
    print("=" * 50)
    for test, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}  {test}")

    print("\nConclusion:")
    if results["obsidian_publish"]:
        print("• Obsidian Publish IS testable with standard Playwright (it's a real web app)")
    if results["local_html"]:
        print("• Exported Obsidian HTML IS testable with Playwright")
    if not results["cdp_electron"]:
        print("• Local Obsidian app requires Electron-specific tooling (not standard Playwright)")
        print("  → Alternative: use 'electron-playwright-helpers' npm package")
        print("  → Alternative: WinAppDriver / Appium for UI-level testing")
