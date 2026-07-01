// scripts/check_hygiene.js
// Enforces repository hygiene checks. Checks that no unwanted files are tracked or unignored.

const { execSync } = require('child_process');

console.log("Running repository hygiene check...");

let trackedFiles = [];
try {
  const output = execSync('git ls-files', { encoding: 'utf8' });
  trackedFiles = output.split('\n').map(f => f.trim()).filter(Boolean);
} catch (err) {
  console.error("ERROR: Failed to run git ls-files. Is git installed?", err.message);
  process.exit(1);
}

const forbiddenPatterns = [
  /\/node_modules\//,
  /\/venv\//,
  /\.env$/,
  /\.log$/,
  /__pycache__/,
  /\.pyc$/,
  /\.pytest_cache/,
  /\.vscode\//,
  /\.idea\//,
  /scratch\//
];

let errors = 0;

// 1. Check tracked files
console.log("Checking tracked files for forbidden patterns...");
for (const file of trackedFiles) {
  const normalized = file.replace(/\\/g, '/');
  for (const pattern of forbiddenPatterns) {
    if (pattern.test(normalized)) {
      console.error(`❌ FORBIDDEN FILE TRACKED: "${file}" matches pattern ${pattern}`);
      errors++;
    }
  }
}

// 2. Check git status for unignored dirty files that shouldn't be there
console.log("Checking git status for unignored files matching forbidden patterns...");
try {
  const statusOutput = execSync('git status --porcelain', { encoding: 'utf8' });
  const lines = statusOutput.split('\n').map(l => l.trim()).filter(Boolean);
  
  for (const line of lines) {
    const status = line.substring(0, 2);
    const filePath = line.substring(3).trim();
    const normalized = filePath.replace(/\\/g, '/');
    
    // Ignore files that are deleted (status contains 'D')
    if (status.includes('D')) {
      continue;
    }
    
    for (const pattern of forbiddenPatterns) {
      if (pattern.test(normalized)) {
        console.error(`❌ FORBIDDEN FILE UNIGNORED/DIRTY: "${filePath}" (status: ${status}) matches pattern ${pattern}`);
        errors++;
      }
    }
  }
} catch (err) {
  console.warn("Warning: Failed to check git status --porcelain:", err.message);
}

if (errors > 0) {
  console.error(`\nFailure: Repository hygiene check failed with ${errors} error(s).`);
  process.exit(1);
} else {
  console.log("\nSuccess: Repository hygiene checks passed!");
  process.exit(0);
}
