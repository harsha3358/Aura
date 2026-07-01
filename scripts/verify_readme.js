// scripts/verify_readme.js
// Validates images and links in README.md case-sensitively.

const fs = require('fs');
const path = require('path');

const README_PATH = path.join(__dirname, '../README.md');

if (!fs.existsSync(README_PATH)) {
  console.error("ERROR: README.md not found!");
  process.exit(1);
}

const content = fs.readFileSync(README_PATH, 'utf8');

// Regex patterns to find links and images
const mdImageRegex = /!\[.*?\]\((.*?)\)/g;
const mdLinkRegex = /\[.*?\]\((.*?)\)/g;
const htmlImageRegex = /<img\s+[^>]*src=["'](.*?)["']/gi;

const localPaths = new Set();

function extractPaths(regex, text) {
  let match;
  while ((match = regex.exec(text)) !== null) {
    const url = match[1].split('#')[0].split('?')[0]; // Remove hash or query params
    // Only check local relative paths (not starting with http://, https://, or mailto:)
    if (url && !url.match(/^(https?:\/\/|mailto:)/i)) {
      localPaths.add(url);
    }
  }
}

extractPaths(mdImageRegex, content);
extractPaths(mdLinkRegex, content);
extractPaths(htmlImageRegex, content);

console.log(`Found ${localPaths.size} local references in README.md to verify.`);

let errorsCount = 0;

function checkCaseSensitiveExists(targetPath) {
  let currentDir = path.join(__dirname, '..');
  const normalized = path.normalize(targetPath);
  const parts = normalized.split(path.sep);
  
  for (const part of parts) {
    if (!part || part === '.' || part === '..') {
      if (part === '..') {
        currentDir = path.dirname(currentDir);
      }
      continue;
    }
    
    if (!fs.existsSync(currentDir)) return false;
    const files = fs.readdirSync(currentDir);
    if (!files.includes(part)) {
      return false; // Name mismatch (case or non-existent)
    }
    currentDir = path.join(currentDir, part);
  }
  return true;
}

for (const rawPath of localPaths) {
  // Ignore purely internal anchor links like "#features"
  if (rawPath.startsWith('#')) {
    continue;
  }
  
  // Resolve relative to repo root
  const relativePath = rawPath.replace(/^\.\//, '');
  const absolutePath = path.resolve(__dirname, '..', relativePath);
  
  if (!fs.existsSync(absolutePath)) {
    console.error(`❌ BROKEN REFERENCE: "${rawPath}" resolves to non-existent path: "${relativePath}"`);
    errorsCount++;
  } else {
    // Check case sensitivity
    const caseMatch = checkCaseSensitiveExists(relativePath);
    if (!caseMatch) {
      console.error(`❌ CASE MISMATCH: "${rawPath}" exists on disk but file casing does not match exactly.`);
      errorsCount++;
    } else {
      console.log(`✅ OK: "${rawPath}"`);
    }
  }
}

if (errorsCount > 0) {
  console.error(`\nFailure: README verification failed with ${errorsCount} error(s).`);
  process.exit(1);
} else {
  console.log("\nSuccess: All local README references verified successfully!");
  process.exit(0);
}
