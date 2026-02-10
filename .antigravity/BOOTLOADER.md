# AGENT BOOTLOADER PROTOCOL

_Strict Mechanical Checklist. Execute sequentially upon first wake-up._

## 1. Environment Diagnostics

- [ ] **Run:** `node -v` (Verify Runtime).
- [ ] **Run:** `npm install` (Hydrate dependencies if `package.json` exists).
- [ ] **Run:** `npm test` (Verify Architecture Integrity).
- [ ] **Check:** Does `.github/workflows/agentic-verify.yml` exist?

## 2. Kernel Check

- [ ] **Read:** `AGENTS.md`.
- [ ] **Verify:** Is `## 5. PRODUCT VISION` populated?

## 3. THE GOLDEN GATE (STOP POINT)

> **IF PRODUCT VISION IS EMPTY:**

1.  **STOP.** Do not create plans or write code.
2.  **Output:** _"System Checks Green. Ready to Build. What is your Product Vision?"_
3.  **Wait** for user input.
4.  **Action:** Write user input to `AGENTS.md` -> `PRODUCT VISION`.
5.  **Proceed:** Only _after_ this step is complete, enter **Phase 1: Planning**.
