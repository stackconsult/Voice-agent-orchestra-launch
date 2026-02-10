# Core Skills Library

_Crystallized knowledge for recurring agent tasks._

---

## Skill 1: `scaffold_production_repo`

**Trigger:** "Initialize project" or missing directory structure.

```bash
#!/bin/bash
mkdir -p .antigravity/context .antigravity/skills
mkdir -p .github/workflows docs src tests
touch AGENTS.md README.md
touch .antigravity/config.json .antigravity/mcp_registry.json
echo '{"autonomy_level": 1, "cost_budget": 5.00}' > .antigravity/config.json

# Tooling Basics
npm init -y
npm install --save-dev eslint prettier globals @eslint/js
# Force lockfile generation
npm install --package-lock-only
# Create ESLint Config (v9)
echo 'module.exports = [];' > eslint.config.js
```

---

## Skill 2: `context_compaction`

**Trigger:** Token usage > 20,000 or context confusion detected.

```bash
#!/bin/bash
# 1. Read execution log
cat .antigravity/context/execution.log

# 2. Agent generates summary (use LLM)

# 3. Write to summary.md
echo "[GENERATED SUMMARY]" > .antigravity/context/summary.md

# 4. Clear log
> .antigravity/context/execution.log

# 5. Reload only: summary.md + AGENTS.md
```

---

## Skill 3: `autonomous_fix_loop`

**Trigger:** CI failure or test failure.

```bash
#!/bin/bash
# 1. Capture error
npm test 2>&1 | tail -50 > /tmp/error.log

# 2. Agent reads error, generates hypothesis

# 3. Apply minimal patch

# 4. Verify
npm test

# 5. Amend if successful
git commit --amend --no-edit
```

---

## Skill 4: `skill_crystallization`

**Trigger:** Successfully completed a novel, complex task.

1. Abstract the specific steps into a generic template
2. Create new file: `.antigravity/skills/[skill_name].md`
3. Register in `config.json`
4. Notify: "I have learned a new skill: `[skill_name]`"

---

## Skill 5: `git_feature_workflow`

**Trigger:** Starting new feature development.

```bash
#!/bin/bash
FEATURE_NAME=$1

# 1. Create branch
git checkout -b feature/$FEATURE_NAME

# 2. Initialize plan (v2.3 Template)
cat <<EOF > .antigravity/context/PLAN.md
# PLAN: $FEATURE_NAME
## User Requirement
- [ ] Describe the goal...

## Atomic Steps
1. [ ] Step 1
2. [ ] Step 2

## Risk Assessment
- Risk Level: LOW/MEDIUM/HIGH
EOF

# 3. Log start
echo "[$(date)] START: $FEATURE_NAME" >> .antigravity/context/execution.log
```

---

## Skill 6: `integrity_check` (v2.3)

**Trigger:** Phase 0 of bootloader or periodic health check.

```bash
#!/bin/bash
echo "=== Antigravity Integrity Suite v2.3 ==="

# 1. Directory Diagnostics
for dir in .antigravity .antigravity/context .antigravity/skills .github/workflows docs src tests; do
  [ -d "$dir" ] && echo "✅ DIR: $dir" || (echo "❌ DIR: $dir MISSING"; exit 1)
done

# 2. File Governance
for file in AGENTS.md README.md LICENSE CONTRIBUTING.md CHANGELOG.md .gitignore .env.example .antigravity/AGENT_OS.md .antigravity/TRAINING_MANUAL.md .antigravity/config.json .antigravity/mcp_registry.json .github/workflows/agentic-verify.yml docs/ARCHITECTURE.md docs/CONSTITUTION.md src/index.js package-lock.json eslint.config.js; do
  [ -f "$file" ] && echo "✅ FILE: $file" || (echo "❌ FILE: $file MISSING"; exit 1)
done

# 3. Vision Check
grep -q "Vision: DEFINED" AGENTS.md && echo "✅ VISION: DEFINED" || echo "⚠️ VISION: PENDING"

echo "=== System 100% Operational ==="
```
