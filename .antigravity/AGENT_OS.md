# THE ANTIGRAVITY AGENT OPERATING SYSTEM

**Version:** 2.3 (Executable Production Master)
**Classification:** Fully Self-Contained Executable Protocol
**Usage:** Read this document. Execute it sequentially. Do not skip steps.

---

# PHASE 0: BOOT SEQUENCE

_Execute immediately upon initialization._

## Step 0.1: Environment Check

```bash
# Run these commands to verify your environment
node -v          # Expected: v20.x or higher
npm -v           # Expected: v10.x or higher
git --version    # Expected: git version 2.x
```

## Step 0.2: Directory Integrity Scan

```bash
# Verify the Golden Tree exists
ls -la .antigravity/
ls -la AGENTS.md
ls -la docs/
```

**IF ANY OF THESE FAIL:** Execute `SKILL 1: SCAFFOLD` below.

## Step 0.3: The Golden Question

**Read `AGENTS.md` Section 5: PRODUCT VISION.**

| IF Vision Status   | THEN Action                                                       |
| ------------------ | ----------------------------------------------------------------- |
| `PENDING INPUT...` | **STOP. ASK USER:** _"System Ready. What are we building today?"_ |
| Populated          | **PROCEED** to Phase 1.                                           |

---

# PHASE 1: PLANNING

_Execute after Phase 0 is complete._

## Step 1.1: Create Task Plan

```bash
# Create or update the active plan
touch .antigravity/context/PLAN.md
```

**Template for PLAN.md:**

```markdown
# PLAN.md

## User Requirement

[Verbatim what was asked]

## Dependencies

- [ ] [What must exist first?]

## Atomic Steps

1. [ ] [Single-file or single-function change]
2. [ ] [Next atomic step]

## Risk Assessment

- **Risk Level:** [HIGH/MEDIUM/LOW]
```

## Step 1.2: Risk Gate

| Risk Level                              | Action                                    |
| --------------------------------------- | ----------------------------------------- |
| **HIGH** (Deletion, Auth, API Keys, DB) | **STOP.** Request `human_approval_token`. |
| **MEDIUM/LOW**                          | **PROCEED** to Phase 2.                   |

---

# PHASE 2: ATOMIC EXECUTION

_Execute for EACH step in PLAN.md._

## The Execution Loop

```python
for step in PLAN.md.atomic_steps:
    # 1. Write Code
    edit_file(step.target_file)

    # 2. Verify Syntax
    run("npm run lint")

    # 3. Verify Build
    run("npm run build")

    # 4. Stop Hook
    if build_fails_twice():
        STOP()
        enter_phase_3_reflection()

    # 5. Commit
    run(f"git commit -m 'feat: {step.name}'")

    # 6. Log
    append_to(".antigravity/context/execution.log", step.summary)
```

---

# PHASE 3: VERIFICATION

_Execute after all PLAN.md steps are complete._

## Step 3.1: Run Tests

```bash
npm test
```

## Step 3.2: Reflection Loop (If Tests Fail)

```python
for attempt in range(1, 4):  # Max 3 attempts
    error = read_error_stack_trace()
    hypothesis = f"The error is caused by {error.cause} because {error.reason}"
    patch = generate_fix(hypothesis)
    apply_patch(patch)

    if run("npm test").passes:
        break

    if attempt == 3:
        run("git checkout .")  # Restore state
        notify_human("I am stuck. Please help.")
```

## Step 3.3: Publication

```bash
git push origin feature/[name]
```

---

# SKILL LIBRARY

_Executable sub-routines._

## SKILL 1: SCAFFOLD

_Use when directory structure is missing._

```bash
#!/bin/bash
# Antigravity Scaffolder

mkdir -p .antigravity/context .antigravity/skills
mkdir -p .github/workflows
mkdir -p docs src tests

touch AGENTS.md README.md
touch .antigravity/config.json
touch .antigravity/mcp_registry.json

echo '{"autonomy_level": 1, "cost_budget": 5.00}' > .antigravity/config.json

echo "# AGENTS.md - The System Kernel

## 1. TECH STACK
- **Runtime:** [FILL IN]

## 2. ALLOWED COMMANDS
- npm run build
- npm test

## 3. FORBIDDEN ACTIONS
- rm -rf /
- Editing AGENTS.md without approval

## 4. AGENT LOGIC
- **Autonomy Mode:** Interactive (Level 1)

## 5. PRODUCT VISION (USER INPUT)
> **STATUS:** PENDING INPUT...
" > AGENTS.md

echo "Scaffold complete."
```

## SKILL 2: CONTEXT COMPACTION

_Use when token usage is high._

```bash
#!/bin/bash
# Compact context to prevent hallucination

# Read execution log
cat .antigravity/context/execution.log

# Summarize (Agent generates this)
# Write summary
echo "[SUMMARY OF COMPLETED STEPS]" > .antigravity/context/summary.md

# Clear working memory
rm .antigravity/context/execution.log
touch .antigravity/context/execution.log

echo "Context compacted."
```

## SKILL 3: AUTONOMOUS FIX

_Use when CI or tests fail._

```bash
#!/bin/bash
# Isolate and fix

# 1. Get failing test
npm test 2>&1 | tail -50 > /tmp/error.log

# 2. Agent reads error.log and generates patch

# 3. Apply minimal fix

# 4. Verify
npm test

# 5. Amend commit
git commit --amend --no-edit
```

---

# GOVERNANCE GATES

_Hard-coded safety checks._

## The Lethal Trifecta Check

```python
def is_lethal_action(action):
    has_private_data = "creds" in action or "PII" in action
    is_untrusted_input = action.source == "external"
    is_external_send = "POST" in action or "curl" in action

    if has_private_data and is_untrusted_input and is_external_send:
        return True  # BLOCK THIS ACTION
    return False
```

## Circuit Breakers (ALWAYS BLOCKED)

- `rm -rf /`
- `curl` to unknown domains
- Editing `AGENTS.md` or `TRAINING_MANUAL.md`
- Installing packages without approval

---

# RUNBOOKS

_Troubleshooting protocols._

## Runbook: Stuck in Loop

**Symptom:** Repeating the same step 3+ times.

```
1. STOP.
2. Run SKILL 2: CONTEXT COMPACTION.
3. Re-read AGENTS.md.
4. Ask human: "I am stuck on [X]. I tried [A, B, C]. Please advise."
```

## Runbook: Hallucinating Paths

**Symptom:** Inventing file paths.

```
1. STOP reading large files.
2. Use `ls` and `grep` only.
3. Run SKILL 2: CONTEXT COMPACTION.
```

---

# INITIALIZATION REPORT

_Output this after completing Phase 0._

```
═══════════════════════════════════════════════════
  ANTIGRAVITY AGENT ONLINE
═══════════════════════════════════════════════════
  Autonomy Level: [1/2/3]
  Product Vision: [Status]
  Environment:    [Verified/Failed]
  CI Pipeline:    [Present/Missing]
═══════════════════════════════════════════════════
  STATUS: READY FOR TASKING
═══════════════════════════════════════════════════
```

---

# END OF DOCUMENT

**This document is self-contained. An Agent reading this can bootstrap, plan, execute, and verify autonomously.**
