// capture_screenshots.js
// Node script using Playwright to capture AURA product screenshots with validation.
// Run with: `node scripts/capture_screenshots.js`
// Prerequisite: npm install playwright

const fs = require('fs');
const { chromium, expect } = require('playwright');

// Ensure Screenshots directory exists
if (!fs.existsSync('Screenshots')) {
  fs.mkdirSync('Screenshots');
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1524, height: 788 } });
  const page = await context.newPage();
  const baseUrl = 'http://localhost:5173';
  const results = {};
  const errorLog = [];

  // Helper: capture + size validation
  async function captureAndValidate(name, selector) {
    try {
      await page.waitForSelector(selector, { timeout: 5000 });
    } catch (e) {
      const msg = `FAILURE: selector ${selector} not found for ${name}`;
      console.error(msg);
      errorLog.push(msg);
      fs.writeFileSync('error.log', errorLog.join('\n'));
      process.exit(1);
    }
    const path = `Screenshots/${name}.png`;
    await page.screenshot({ path, fullPage: true });
    const stat = fs.statSync(path);
    if (stat.size <= 10 * 1024) {
      const msg = `FAILURE: ${name}.png size ${stat.size} bytes <= 10KB`;
      console.error(msg);
      errorLog.push(msg);
      fs.writeFileSync('error.log', errorLog.join('\n'));
      process.exit(1);
    }
    console.log(`Captured ${name}.png (size ${stat.size} bytes)`);
    results[`${name}.png`] = true;
  }

  // 1. Login page
  await page.goto(baseUrl);
  await captureAndValidate('Login', 'body');

  // 2. Perform login (adjust password if needed)
  await page.fill('input[type="email"]', 'harsha@aura.run');
  await page.fill('input[type="password"]', 'password');
  await page.waitForSelector('button:has-text("Login"), button:has-text("Log In"), button[type="submit"], input[type="submit"]', { timeout: 5000 });
await page.click('button:has-text("Login"), button:has-text("Log In"), button[type="submit"], input[type="submit"]');
  await page.waitForLoadState('networkidle');

  // 3. Onboarding wizard
  await captureAndValidate('Onboarding', 'body');

  // 4. Dashboard – ensure greeting visible
  await captureAndValidate('Dashboard', 'text=Good Morning');

  // 5. Knowledge Explorer – verify "Facts" label
  await page.click('text=Knowledge Explorer').catch(() => {});
  await page.waitForLoadState('networkidle');
  await captureAndValidate('KnowledgeExplorer', 'text=Facts');

  // 6. Capture Session – open modal
  await page.click('button:has-text("Capture")').catch(() => {});
  await captureAndValidate('CaptureSession', '.capture-modal');

  // 7. Extraction Chips – open after extraction
  await page.click('button:has-text("Extract")').catch(() => {});
  await captureAndValidate('ExtractionChips', '.extraction-chips');

  // 8. Edit Workflow – open edit modal for first chip
  await page.click('.extraction-chips .chip:first-child button.edit').catch(() => {});
  await captureAndValidate('EditWorkflow', '.edit-modal');

  // 9. Reject Workflow – open reject modal for first chip
  await page.click('.extraction-chips .chip:first-child button.reject').catch(() => {});
  await captureAndValidate('RejectWorkflow', '.reject-modal');

  // 10. Executive Brief – verify top priorities visible
  await page.click('text=Executive Brief').catch(() => {});
  await page.waitForLoadState('networkidle');
  await captureAndValidate('ExecutiveBrief', 'text=Top Priorities');

  // 11. Mobile view – resize and recapture Dashboard
  await page.setViewportSize({ width: 375, height: 667 });
  await page.goto(baseUrl);
  await captureAndValidate('MobileView', 'text=Good Morning');

  // 12. Desktop view – restore size and recapture Dashboard
  await page.setViewportSize({ width: 1524, height: 788 });
  await page.goto(baseUrl);
  await captureAndValidate('DesktopView', 'text=Good Morning');

  // Write validation JSON report
  fs.writeFileSync('validation_screenshots.json', JSON.stringify(results, null, 2));

  // Generate Screenshots/index.md with embedded images
  const indexLines = ['# Validation Evidence', ''];
  for (const file of Object.keys(results)) {
    const name = file.replace('.png', '');
    indexLines.push(`- ${name}`);
    indexLines.push(`  ![${name}](./${file})`);
    indexLines.push('');
  }
  fs.writeFileSync('Screenshots/index.md', indexLines.join('\n'));

  await browser.close();
})();
