---
description: Deploy a new Electron B2B Automation Tool (Agent-in-a-Box)
---

# Workflow: Deploy Electron Automation Tool

Use this workflow to initialize, configure, and implement a robust, secure, and
production-ready Electron application tailored for B2B automation.

## Step 1: Initialize Project (Scaffold)

**Objective**: Create the base Electron structure with TypeScript and Webpack.

- **Action**: Run the scaffolding process using the `Electron Scaffold` skill.
- **Reference**: `view_file .antigravity/skills/electron/scaffold.md`
- **Output**: A running Electron app with `npm start`.
- **Verify**: Ensure `CONTEXT_ISOLATION` is enabled in `main.ts` by default.

## Step 2: Implement Secure IPC Bridge (Layer 2)

**Objective**: Establish type-safe communication between Renderer and Main process.

- **Action**: Implement `preload.ts` and update `main.ts` handlers using the
  `Electron IPC Bridge` skill.
- **Reference**: `view_file .antigravity/skills/electron/ipc_bridge.md`
- **Constraint**: Must use `contextBridge.exposeInMainWorld`. NEVER expose raw
  `ipcRenderer`.
- **Verify**: Frontend can call `window.electronAPI.ping()` and receive `'pong'`.

## Step 3: Implement Sidecar Manager (Layer 4)

**Objective**: Set up Python/Go child processes for heavy automation tasks.

- **Action**: Create `src/main/sidecar.ts` to manage spawn/kill lifecycles.
- **Reference**: [Future Skill: Sidecar Manager] (Use `child_process.spawn`)
- **Constraint**: Wrap spawn logic in `try/catch` block. Log stderr to
  `console.error`.

## Step 4: Configure Final Build (Layer 5)

**Objective**: Prepare the app for distribution (Windows/Mac/Linux).

- **Action**: Configure `electron-builder` or `electron-forge` settings in
  `package.json`.
- **Constraint**: Ensure `asar: true` is set for security.
- **Reference**: Refer to `Electron for UI Deployments_ Deep Research & Antig.md`
  for signing details.

## Step 5: Verification Phase

**Objective**: Ensure the app meets Antigravity standards.

- **Action 1**: Run `npm start` and verify window launch.
- **Action 2**: Check Developer Tools console for any CSP violations.
- **Action 3**: Verify no critical `EACCES` or dependency errors in terminal.
