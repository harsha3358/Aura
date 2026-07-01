// scripts/check_architecture.js
// Verifies if ARCHITECTURE.md is updated when architectural files are changed.

const { execSync } = require('child_process');

console.log("Running architecture compliance check...");

// 1. Gather modified files
let modifiedFiles = [];
try {
  // In CI, base branch is origin/main. Fallback to HEAD~1 or status locally.
  let diffCommand = 'git diff --name-only origin/main';
  try {
    execSync('git rev-parse --verify origin/main', { stdio: 'ignore' });
  } catch (e) {
    diffCommand = 'git diff --name-only HEAD~1';
  }
  
  const output = execSync(diffCommand, { encoding: 'utf8' });
  modifiedFiles = output.split('\n').map(f => f.trim()).filter(Boolean);
  
  // Also include uncommitted changes
  const localOutput = execSync('git status --porcelain', { encoding: 'utf8' });
  const localFiles = localOutput.split('\n')
    .map(l => l.trim())
    .filter(Boolean)
    .map(l => l.substring(3).trim());
    
  modifiedFiles = [...new Set([...modifiedFiles, ...localFiles])];
} catch (err) {
  console.warn("Warning: Failed to gather git diff, using git status only:", err.message);
  try {
    const localOutput = execSync('git status --porcelain', { encoding: 'utf8' });
    modifiedFiles = localOutput.split('\n')
      .map(l => l.trim())
      .filter(Boolean)
      .map(l => l.substring(3).trim());
  } catch (e) {
    console.error("ERROR: Failed to run git status.", e.message);
    process.exit(1);
  }
}

// 2. Define architectural patterns
const archPatterns = [
  /^apps\/api\/app\/models\//,
  /^apps\/api\/app\/routers\//,
  /^apps\/api\/app\/extraction\//,
  /^apps\/web\/src\/store\//,
  /^apps\/web\/src\/components\/[A-Z]/,
  /docker-compose\.yml$/,
  /package\.json$/,
  /requirements\.txt$/
];

const changedArchFiles = modifiedFiles.filter(file => {
  const normalized = file.replace(/\\/g, '/');
  return archPatterns.some(pattern => pattern.test(normalized));
});

const isArchitectureMdChanged = modifiedFiles.some(file => 
  file.replace(/\\/g, '/').endsWith('ARCHITECTURE.md')
);

console.log(`Detected ${changedArchFiles.length} changed architectural file(s).`);

if (changedArchFiles.length > 0 && !isArchitectureMdChanged) {
  console.warn("\n⚠️  WARNING: Architectural files were modified, but ARCHITECTURE.md was NOT updated!");
  console.warn("Changed architectural files:");
  changedArchFiles.forEach(f => console.warn(`  - ${f}`));
  console.warn("\nPlease review and ensure ARCHITECTURE.md matches any system or database schema changes.");
  
  // For strict PR compliance, fail the build, or pass with warning.
  // The user requested a "lightweight check that reminds contributors". 
  // Let's print a warning but not fail the CI run to keep it lightweight, 
  // unless we specify a strict flag.
  if (process.argv.includes('--strict')) {
    console.error("\nERROR: Architecture compliance check failed (strict mode). ARCHITECTURE.md must be updated.");
    process.exit(1);
  }
} else {
  console.log("\nSuccess: Architecture compliance checks passed!");
}

process.exit(0);
