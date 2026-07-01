// scripts/verify_commit_msg.js
// Enforces Conventional Commits formatting and character rules.

const fs = require('fs');
const path = require('path');

const msgPath = process.argv[2];
if (!msgPath) {
  console.error("❌ Error: Path to commit message file is missing.");
  process.exit(1);
}

const commitMsg = fs.readFileSync(msgPath, 'utf8').trim();

// Skip empty messages or branch merges/reverts automatically handled by git
if (!commitMsg || commitMsg.startsWith('Merge branch') || commitMsg.startsWith('Revert ')) {
  process.exit(0);
}

// Conventional commit pattern: type(scope)?: description
// Type: feat, fix, docs, style, refactor, test, chore, ci, build, perf
const commitPattern = /^(feat|fix|docs|style|refactor|test|chore|ci|build|perf|revert)(\([a-zA-Z0-9_\-\/ ]+\))?: (.*)$/;

const match = commitMsg.split('\n')[0].match(commitPattern);

if (!match) {
  console.error("\n❌ INVALID COMMIT MESSAGE FORMAT");
  console.error("Your commit message does not match the Conventional Commits specification.");
  console.error("Expected Format: <type>(<scope>)?: <description>");
  console.error("Example: feat(capture): add extraction chip approve workflow\n");
  console.error("Allowed types: feat, fix, docs, style, refactor, test, chore, ci, build, perf, revert");
  process.exit(1);
}

const [_, type, scope, description] = match;

// Check length (subject line should be <= 72 characters)
const firstLine = commitMsg.split('\n')[0];
if (firstLine.length > 72) {
  console.error(`\n❌ COMMIT MESSAGE TOO LONG`);
  console.error(`Subject line length is ${firstLine.length} characters (max allowed is 72).`);
  console.error(`Message: "${firstLine}"`);
  process.exit(1);
}

// Check trailing period
if (description.endsWith('.')) {
  console.error(`\n❌ INVALID TRAILING CHARACTER`);
  console.error(`Subject line must not end with a period.`);
  console.error(`Message: "${firstLine}"`);
  process.exit(1);
}

// Imperative mood guidance heuristic (warn or block if starts with past tense or third person)
const words = description.split(' ');
const firstWord = words[0].toLowerCase();
const invalidVerbs = ['added', 'fixed', 'removed', 'created', 'changed', 'updated', 'adds', 'fixes', 'removes', 'creates', 'changes', 'updates'];

if (invalidVerbs.includes(firstWord)) {
  console.warn(`\n⚠️  IMPERATIVE MOOD WARNING: "${firstWord}" detected.`);
  console.warn("Commit descriptions should use the imperative, present-tense mood.");
  console.warn("Example: Use 'add' instead of 'added'/'adds', or 'fix' instead of 'fixed'/'fixes'.");
  console.warn("This describes what the commit *does*, not what it *did*.\n");
  
  // Let's block it in strict validator mode
  console.error("❌ Commit blocked due to non-imperative mood verb usage.");
  process.exit(1);
}

console.log("✅ Commit message format verified successfully.");
process.exit(0);
