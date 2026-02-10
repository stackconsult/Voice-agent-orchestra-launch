# Electron Deployment Skills

_Crystallized knowledge for Electron-specific deployment and security._

---

## Skill: `scaffold_electron_app`

**Trigger:** "Setup electron" or "Initialize desktop app".

```bash
#!/bin/bash
# 1. Initialize Electron Forge
npm install --save-dev @electron-forge/cli
npx electron-forge import

# 2. Add security dependencies
npm install --save-dev @electron/fuses

# 3. Create basic structure if missing
mkdir -p src
touch src/main.js src/preload.js src/index.html
```

---

## Skill: `ipc_secure_bridge`

**Trigger:** "Create IPC channel" or "Connect renderer to main".

**Implementation Template:**

1. **Main Process (`src/main.js`):**

```javascript
const { ipcMain } = require('electron');
ipcMain.handle('channel-name', async (event, arg) => {
  // logic here
  return result;
});
```

2. **Preload Script (`src/preload.js`):**

```javascript
const { contextBridge, ipcRenderer } = require('electron');
contextBridge.exposeInMainWorld('electronAPI', {
  invokeChannel: (data) => ipcRenderer.invoke('channel-name', data),
});
```

---

## Skill: `package_electron_app`

**Trigger:** "Build for production" or "Create installers".

```bash
#!/bin/bash
# 1. Run forge make
npm run make

# 2. Check output
ls -R out/make
```

---

## Skill: `electron_security_audit`

**Trigger:** Before production deployment.

1. Verify `contextIsolation: true` in `BrowserWindow`
2. Verify `nodeIntegration: false`
3. Verify `sandbox: true`
4. Check for `ASAR` integrity validation
