# AGENTS.md - The System Kernel

## 1. TECH STACK

- **OS:** Mac OS
- **Runtime:** Node.js v24+, Electron Forge
- **Environment:** Antigravity IDE / Desktop Engineering Environment
- **Automation Framework:** Antigravity Protocol v2.3

## 2. OPERATIONAL COMMANDS (ALLOWED)

- **Scaffolding:** `mkdir`, `touch`
- **Maintenance:** `rm` (Targeted), `cp`, `mv`
- **Analysis:** `ls`, `grep`, `find`, `cat`
- **Development:** `npm install`, `npm test`, `npm run build`

## 3. FORBIDDEN ACTIONS (CIRCUIT BREAKERS)

- **Lethal Deletion:** `rm -rf /` or recursive destruction of root framework directories.
- **Unauthorized Exfiltration:** Sending `.env`, `mcp_registry.json`, or proprietary docs to untrusted domains.
- **Self-Mutation:** Modifying `AGENTS.md` or `TRAINING_MANUAL.md` without `human_authorization_token` (except during framework bootstrapping).
- **Credential Access:** Reading `~/.ssh`, system-level keychains, or un-whitelisted secret managers.

## 4. AGENT LOGIC

- **Autonomy Mode:** Interactive (Level 1)
- **CI Enforcement:** Required for all PRs.

## 5. PRODUCT VISION (USER INPUT)

> **STATUS:** ACTIVE
> **VISION:** The `antigravity-playground` is the "Ground Zero" foundation for all future agent-driven GitHub builds. It integrates all core workflows, agent-specific skills, and deterministic engineering protocols to enable a robust, scalable path from ideation to production deployment. This repository serves as the master template for all new Antigravity project setups.
