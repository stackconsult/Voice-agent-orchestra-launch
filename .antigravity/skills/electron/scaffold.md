---
name: Electron Scaffold
description: Initialize a production-grade Electron app with TypeScript, Webpack, and Antigravity security controls.
---

# Skill: Electron Scaffolding

This skill initializes a new Electron project calibrated for "Agent-in-a-Box"
deployments. It enforces TypeScript, Webpack, and strict security defaults.

## Usage

Use this skill when starting a NEW Electron project.

### 1. Initialize Project Structure

Wait for the `npx` command to complete fully.

```bash
# Initialize with TypeScript + Webpack template
npx -y create-electron-app@latest . --template=typescript-webpack

# Install critical dependencies for Sidecars & Rebuilding
npm install --save-dev @electron/rebuild @electron/fuses cross-env
npm install uuid better-sqlite3
```

### 2. Configure Build Scripts

Update `package.json` scripts to support cross-platform building and sidecar
management.

```json
"scripts": {
  "start": "electron-forge start",
  "package": "electron-forge package",
  "make": "electron-forge make",
  "rebuild": "electron-rebuild",
  "lint": "eslint --ext .ts ."
}
```

### 3. Establish Security Constitution

Creates `CONSTITUTION.md` in the root to enforce security rules on future
agents.

```markdown
# CONSTITUTION.md - Electron Security

## 1. The Lethal Trifecta (PREVENTION)

### NEVER allow these three conditions simultaneously:
1. **Remote Content**: Loading external URLs (e.g.,
   `win.loadURL('https://...')`)
2. **Node Integration**: `webPreferences: { nodeIntegration: true }`
3. **Context Isolation Disabled**: `webPreferences: { contextIsolation: false }`

## 2. Default Security Settings
ALWAYS use these settings for `BrowserWindow`:

```javascript
webPreferences: {
  contextIsolation: true,  // MUST be true
  nodeIntegration: false,  // MUST be false
  sandbox: true,           // Enforce sandbox
  preload: path.join(__dirname, 'preload.js')
}
```

## 3. Network Policy

- **Offline First**: App must function without internet.
- **CSP**: Content Security Policy must mimic `default-src 'self'`.

```markdown

### 4. Define Architecture

Creates `ARCHITECTURE.md` to guide future agents on the 5-Layer pattern.

```markdown
# ARCHITECTURE.md - 5-Layer Electron Pattern

1. **Presentation (Renderer)**: Angular/React UI. SANDBOXED. No Node access.
2. **Bridge (Preload)**: `contextBridge`. The ONLY secure path. Typed APIs.
3. **Application (Main)**: Window management, auto-updates. Thin layer.
4. **Sidecar (Child Process)**: Python/Go scripts for AI/Automation logic.
5. **Memory (Storage)**: SQLite (local) + Docker (databases).
```
