# Antigravity Comprehensive Workflow

This document defines the end-to-end lifecycle for professional automation projects built with the Antigravity framework, spanning from ideation to multi-platform deployment.

---

## Phase 0: The Boot Sequence (Agent Initialization)

- **Goal**: Establish the "Golden Gate" safety and awareness baseline.
- **Workflow**:
  1.  **Environment Sync**: Run `node -v` and `npm install`.
  2.  **Kernel Load**: Read `AGENTS.md` and check **Product Vision**.
  3.  **Integrity Verification**: Execute `Skill 6: integrity_check`.
- **Exit Condition**: 100% Green check; non-empty Product Vision.

## Phase 0.5: Tooling Verification (Pre-CI Check)

- **Goal**: Prevent avoidable CI failures (The "Lockfile Law").
- **Workflow**:
  1.  **Lockfile**: Ensure `package-lock.json` exists and is synced (`npm install --package-lock-only`).
  2.  **Linter**: Verify `eslint.config.js` is V9 compliant.
  3.  **Local Test**: Run `npm run lint` && `npm run format` locally before ANY push.

## 1. Ideation & Planning (Agent/Human Loop)

- **Goal**: Define the macro-architecture and atomic task plan.
- **Workflow**:
  - **Human**: Populates Product Vision in `AGENTS.md`.
  - **Agent**: Generates `PLAN.md` using the v2.3 template (Skill 5).
  - **Human**: Reviews/Approves `PLAN.md` in `.antigravity/context/`.

## 2. Structure & Implementation (Deep Agent Execution)

- **Goal**: Deterministic build out of logic and UI.
- **Workflow**:
  - **Agent**: Follows the `PLAN.md` loop (edit → test → verify).
  - **Governance**: Every commit must pass the `Agentic Verification` CI pipeline.
  - **Skill Application**: Repeated patterns are pulled from/pushed to `.antigravity/skills/`.

## 3. Integration & Electron Transition

- **Goal**: Convert the web/node project into a native desktop application.
- **Workflow**:
  - Trigger `SKILL: scaffold_electron_app`.
  - Implement `ipc_secure_bridge` for UI-Main communication.
  - Add native filesystem and system integration features.

## 4. Distribution & Deployment

- **Goal**: Package and sign the application for client delivery.
- **Workflow**:
  - Trigger `SKILL: package_electron_app`.
  - Configure `forge.config.js` for Code Signing (Apple Developer / Windows EV).
  - Deploy distributables to S3/CDN for auto-updates.

## 5. Maintenance & Updates

- **Goal**: Push new features and bug fixes to existing installations.
- **Workflow**:
  - Bump version in `package.json`.
  - Regenerate distributables and update `RELEASES` / `releases.json`.
  - Clients receive background updates via the auto-update infrastructure.
