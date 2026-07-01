// scripts/generate_ci_summary.js
// Parses CI reports and generates a Markdown summary for GitHub Actions.

const fs = require('fs');
const path = require('path');

console.log("Generating CI Run Summary...");

const summaryFile = process.env.GITHUB_STEP_SUMMARY;
if (!summaryFile) {
  console.warn("Warning: GITHUB_STEP_SUMMARY environment variable not set. Writing summary to stdout.");
}

const lines = [];

lines.push("# 🚀 AURA CI Run Summary");
lines.push("");

// 1. Parse Pytest Reports
let pytestResult = "⚠️ Not Run/Failed";
let pytestDetails = "";
const pytestXmlPath = path.join(__dirname, '../pytest-reports/pytest-report.xml');
if (fs.existsSync(pytestXmlPath)) {
  try {
    const content = fs.readFileSync(pytestXmlPath, 'utf8');
    // Extract test suite summary (errors="0" failures="0" skipped="0" tests="16" time="1.40")
    const match = content.match(/<testsuite.*?errors="(\d+)".*?failures="(\d+)".*?skipped="(\d+)".*?tests="(\d+)".*?time="(.*?)".*?>/i);
    if (match) {
      const [_, errors, failures, skipped, tests, time] = match;
      const failedCount = parseInt(errors) + parseInt(failures);
      if (failedCount === 0) {
        pytestResult = `✅ Passed (${tests} tests)`;
      } else {
        pytestResult = `❌ Failed (${failedCount} failed, ${tests} total)`;
      }
      pytestDetails = `- **Total Tests**: ${tests}\n- **Passed**: ${tests - failedCount - skipped}\n- **Failed**: ${failedCount}\n- **Skipped**: ${skipped}\n- **Duration**: ${time}s`;
    }
  } catch (err) {
    console.error("Failed to parse pytest XML:", err.message);
  }
}
lines.push(`## Backend API Tests: ${pytestResult}`);
if (pytestDetails) lines.push(pytestDetails);
lines.push("");

// 2. Parse Vitest Reports
let vitestResult = "⚠️ Not Run/Failed";
let vitestDetails = "";
const vitestXmlPath = path.join(__dirname, '../vitest-reports/vitest-report.xml');
if (fs.existsSync(vitestXmlPath)) {
  try {
    const content = fs.readFileSync(vitestXmlPath, 'utf8');
    // Extract test suite summary (tests="5" failures="0" errors="0" skipped="0" time="0.087")
    const match = content.match(/<testsuite.*?tests="(\d+)".*?failures="(\d+)".*?errors="(\d+)".*?skipped="(\d+)".*?time="(.*?)".*?>/i);
    if (match) {
      const [_, tests, failures, errors, skipped, time] = match;
      const failedCount = parseInt(errors) + parseInt(failures);
      if (failedCount === 0) {
        vitestResult = `✅ Passed (${tests} tests)`;
      } else {
        vitestResult = `❌ Failed (${failedCount} failed, ${tests} total)`;
      }
      vitestDetails = `- **Total Tests**: ${tests}\n- **Passed**: ${tests - failedCount - skipped}\n- **Failed**: ${failedCount}\n- **Skipped**: ${skipped}\n- **Duration**: ${time}s`;
    }
  } catch (err) {
    console.error("Failed to parse vitest XML:", err.message);
  }
}
lines.push(`## Frontend Web Tests: ${vitestResult}`);
if (vitestDetails) lines.push(vitestDetails);
lines.push("");

// 3. Parse Screenshot Validation
let screenshotsResult = "⚠️ Not Run/Failed";
let screenshotsDetails = "";
const screenshotsJsonPath = path.join(__dirname, '../validation-screenshots/validation_screenshots.json');
if (fs.existsSync(screenshotsJsonPath)) {
  try {
    const data = JSON.parse(fs.readFileSync(screenshotsJsonPath, 'utf8'));
    const files = Object.keys(data);
    screenshotsResult = `✅ Captured (${files.length} screenshots)`;
    screenshotsDetails = "- **Captured Files**:\n" + files.map(f => `  - \`${f}\` (validated >10KB)`).join('\n');
  } catch (err) {
    console.error("Failed to parse screenshots JSON:", err.message);
  }
}
lines.push(`## Playwright E2E Screenshots: ${screenshotsResult}`);
if (screenshotsDetails) lines.push(screenshotsDetails);
lines.push("");

// 4. Final summary block
lines.push("---");
lines.push(`*Run completed at: ${new Date().toUTCString()}*`);

const summaryContent = lines.join('\n');

if (summaryFile) {
  fs.writeFileSync(summaryFile, summaryContent);
  console.log("Summary written to GITHUB_STEP_SUMMARY.");
} else {
  console.log(summaryContent);
}
