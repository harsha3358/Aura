const fs = require('fs');
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();
  await page.goto('http://localhost:5173');
  await page.fill('input[type="email"]', 'harsha@aura.run');
  await page.fill('input[type="password"]', 'password');
  await page.waitForSelector('button:has-text("Login"), button:has-text("Log In"), button[type="submit"], input[type="submit"]', { timeout: 5000 });
  await page.click('button:has-text("Login"), button:has-text("Log In"), button[type="submit"], input[type="submit"]');
  await page.waitForLoadState('networkidle');
  // Try to open Capture Session
  try {
    await page.click('button:has-text("Capture")');
    await page.waitForTimeout(2000);
    const html = await page.content();
    fs.writeFileSync('debug_capture.html', html);
    console.log('Saved debug_capture.html');
  } catch (e) {
    console.error('Capture click failed', e);
  }
  await browser.close();
})();
