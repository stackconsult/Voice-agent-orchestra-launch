# docs/ARCHITECTURE.md - System Boundaries

## 1. DESIGN PHILOSOPHY

The Antigravity Framework is a **Deterministic State Machine** designed for high-stakes automation. This "Ground Zero" playground acts as the immutable root template, providing the ontological structure (memory, kernel, truth) required for agents to operate with 100% reliability. Reliability is prioritized over speed; verification is mandatory at every state transition.

## 2. COMPONENT BOUNDARIES

- **Kernel (`AGENTS.md`):** Fixed rules and environment definitions.
- **Memory (`.antigravity/`):** Short-term context and long-term skill crystallization.
- **Application (`src/`):** The logic being developed.
- **Truth (`tests/`):** The final authority on code correctness.

## 3. ASDLC WORKFLOW

1.  **Explore:** Identify files and context.
2.  **Plan:** Draft `PLAN.md` with atomic steps.
3.  **Execute:** Implementation with immediate verification (lint/build).
4.  **Reflect:** Post-mortem on failures and skill crystallization.

## 4. DATA FLOW & IPC LOGIC

The framework uses a **Uni-directional Data Flow** for state changes:

1.  **Request**: User or Agent triggers an action.
2.  **Kernel Intercept**: checks `AGENTS.md` for permissions.
3.  **Skill Execution**: Deterministic logic from `.antigravity/skills/` is invoked.
4.  **Truth Verification**: Output is validated against `tests/`.
5.  **State Commit**: Success is logged to `execution.log` and `summary.md`.

## 5. MCP TOOLS INTEGRATION

Tools are accessed via the `mcp_registry.json`. Any new tool must be vetted and registered before use in automated workflows.
