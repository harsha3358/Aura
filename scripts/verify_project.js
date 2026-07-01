// scripts/verify_project.js
// Canonical local quality verification command runner. Supports verify and verify:release modes.

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const isReleaseMode = process.argv.includes('--release');
console.log(`Starting AURA local verification (Mode: ${isReleaseMode ? 'RELEASE' : 'STANDARD'})...\n`);

const isWindows = process.platform === 'win32';
const venvBin = isWindows
  ? path.resolve(__dirname, '../apps/api/venv/Scripts')
  : path.resolve(__dirname, '../apps/api/venv/bin');

// Resolve local tool path with global system fallback
function getToolPath(toolName) {
  const binaryName = isWindows ? `${toolName}.exe` : toolName;
  const localPath = path.join(venvBin, binaryName);
  if (fs.existsSync(localPath)) {
    return localPath;
  }
  return toolName; // Fallback to global/system PATH
}

const python = getToolPath('python');
const pytest = getToolPath('pytest');
const ruff = getToolPath('ruff');

let hasFailed = false;

function runStep(name, command, cwd = '.') {
  console.log(`[STEP] Running: ${name}...`);
  try {
    execSync(command, { cwd: path.resolve(__dirname, '..', cwd), stdio: 'inherit' });
    console.log(`✅ [SUCCESS] ${name}\n`);
    return true;
  } catch (err) {
    console.error(`❌ [FAILURE] ${name} failed!\n`);
    hasFailed = true;
    return false;
  }
}

// 1. Verify Documentation presence & size
console.log("[STEP] Verifying documentation presence...");
const docsToVerify = ['README.md', 'ARCHITECTURE.md', 'docs/CI_CD.md'];
let docsOk = true;
for (const doc of docsToVerify) {
  const docPath = path.resolve(__dirname, '..', doc);
  if (!fs.existsSync(docPath)) {
    console.error(`❌ FAILURE: Required doc "${doc}" is missing!`);
    docsOk = false;
    hasFailed = true;
  } else {
    const stats = fs.statSync(docPath);
    if (stats.size < 100) {
      console.error(`❌ FAILURE: Required doc "${doc}" is virtually empty (size: ${stats.size} bytes)!`);
      docsOk = false;
      hasFailed = true;
    }
  }
}
if (docsOk) {
  console.log("✅ [SUCCESS] Documentation presence verified.\n");
}

// 2. Repository Hygiene
runStep("Repository Hygiene Checker", "node scripts/check_hygiene.js");

// 3. README Links Validation
runStep("README Image & Link Checker", "node scripts/verify_readme.js");

// 4. Architecture Compliance
runStep("Architecture Compliance Warning", "node scripts/check_architecture.js");

// 5. Python Ruff check
runStep("Python Ruff Linter Check", `"${ruff}" check apps/api`);

// 6. Python Ruff format check
runStep("Python Ruff Formatter Check", `"${ruff}" format --check apps/api`);

// 7. Python Backend Tests (pytest)
// Generate coverage XML locally as well
runStep("Python Pytest Suite", `"${python}" -m pytest --cov=app --cov-report=xml --cov-report=term`, "apps/api");

// 8. TypeScript compilation check
runStep("TypeScript Compiler check", "npx tsc --project apps/web/tsconfig.json --noEmit");

// 9. Frontend ESLint Check
runStep("Frontend ESLint Linter", "npm run lint --if-present || npx eslint src", "apps/web");

// 10. Frontend Prettier Formatting Check
runStep("Frontend Prettier Formatter Check", 'npx prettier --check "src/**/*.{ts,tsx,css,json}"', "apps/web");

// 11. Frontend Vitest unit tests
runStep("Frontend Vitest Tests", "npm run test", "apps/web");

// 12. Frontend Production Build compilation
runStep("Frontend Production Compilation", "npm run build", "apps/web");

// 13. Security Audits (Only in Release Mode)
if (isReleaseMode) {
  runStep("Python Dependency Vulnerability Scan (pip-audit)", "pip-audit -r apps/api/requirements.txt || pip-audit -r requirements.txt", "apps/api");
  runStep("Frontend Dependency Security Audit (npm audit)", "npm audit --audit-level=high", "apps/web");
}

if (hasFailed) {
  console.error("❌ VERIFICATION FAILED: Please fix errors before pushing!");
  process.exit(1);
} else {
  console.log("🚀 ALL LOCAL VERIFICATIONS PASSED SUCCESSFULLY!");
  process.exit(0);
}
