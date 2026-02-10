/**
 * Antigravity Framework - Setup Test
 *
 * This test validates the integrity of the framework structure.
 * It runs during Phase 0 (Bootloader) to ensure the agent's "brain" is intact.
 */

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');

// Required directories
const REQUIRED_DIRS = [
  '.antigravity',
  '.antigravity/context',
  '.antigravity/skills',
  '.github/workflows',
  'docs',
  'src',
  'tests',
];

// Required files
const REQUIRED_FILES = [
  'AGENTS.md',
  'README.md',
  '.antigravity/AGENT_OS.md',
  '.antigravity/TRAINING_MANUAL.md',
  '.antigravity/config.json',
  '.antigravity/mcp_registry.json',
  '.github/workflows/agentic-verify.yml',
  'docs/ARCHITECTURE.md',
  'docs/CONSTITUTION.md',
  'src/index.js',
];

let passed = 0;
let failed = 0;

console.log('╔════════════════════════════════════════════════════╗');
console.log('║  ANTIGRAVITY FRAMEWORK - INTEGRITY CHECK           ║');
console.log('╚════════════════════════════════════════════════════╝\n');

// Check directories
console.log('📁 Checking directories...');
for (const dir of REQUIRED_DIRS) {
  const fullPath = path.join(ROOT, dir);
  if (fs.existsSync(fullPath) && fs.statSync(fullPath).isDirectory()) {
    console.log(`  ✅ ${dir}`);
    passed++;
  } else {
    console.log(`  ❌ ${dir} - MISSING`);
    failed++;
  }
}

console.log('\n📄 Checking files...');
for (const file of REQUIRED_FILES) {
  const fullPath = path.join(ROOT, file);
  if (fs.existsSync(fullPath) && fs.statSync(fullPath).isFile()) {
    console.log(`  ✅ ${file}`);
    passed++;
  } else {
    console.log(`  ❌ ${file} - MISSING`);
    failed++;
  }
}

// Check Product Vision status
console.log('\n🎯 Checking Product Vision...');
const agentsPath = path.join(ROOT, 'AGENTS.md');
if (fs.existsSync(agentsPath)) {
  const content = fs.readFileSync(agentsPath, 'utf8');
  if (content.includes('PENDING INPUT...')) {
    console.log('  ⚠️  Product Vision: PENDING (Agent should ask user)');
  } else if (content.includes('## 5. PRODUCT VISION')) {
    console.log('  ✅ Product Vision: DEFINED');
    passed++;
  }
} else {
  console.log('  ❌ Cannot check - AGENTS.md missing');
  failed++;
}

// Summary
console.log('\n════════════════════════════════════════════════════');
console.log(`  PASSED: ${passed}  |  FAILED: ${failed}`);
console.log('════════════════════════════════════════════════════\n');

if (failed > 0) {
  console.log('❌ INTEGRITY CHECK FAILED');
  console.log('   Run Skill 1 (scaffold_production_repo) to fix.\n');
  process.exit(1);
} else {
  console.log('✅ INTEGRITY CHECK PASSED');
  console.log('   Framework is ready for operation.\n');
  process.exit(0);
}
