# Contributing to Antigravity Playground

Welcome! This repository is the "Ground Zero" for agentic software builds. We follow a strict **Deterministic State Machine** protocol.

## Agent Collaboration Rules

Agents contributing to this repository MUST:

1.  **Read the Kernel**: Always load `AGENTS.md` first.
2.  **Follow the OS**: Execute sequences in `AGENT_OS.md` without skipping steps.
3.  **Respect Truth**: All logic must be verified via `npm test`.
4.  **Log Heartbeats**: Record every state transition in `.antigravity/context/execution.log`.

## Human Collaboration

Humans should:

1.  **Provide Vision**: Define the macro-goal in `AGENTS.md`.
2.  **Audit Governance**: Review `PLAN.md` for high-risk operations.
3.  **Crystallize Skills**: Once a complex task is completed, approve the conversion of local logic into a global skill in `.antigravity/skills/`.

## PR Process

1.  Create a feature branch using Skill 5.
2.  Pass all Automated Verification Gates in CI.
3.  Ensure documentation (v2.3+) is updated to reflect new changes.
