---
name: Electron IPC Bridge
description: Implement a strongly-typed, secure Inter-Process Communication (IPC) bridge.
---

# Skill: Secure IPC Bridge

Use this skill to create the **Type-Safe Communication Layer** between the
sandboxed Renderer (UI) and the privileged Main process.

## 1. Define the API Contract (`src/preload.ts`)

ALWAYS use `contextBridge.exposeInMainWorld` to expose ONLY specific methods,
never the entire `ipcRenderer`.

```typescript
import { contextBridge, ipcRenderer } from 'electron';

// 1. Define the interface for the Renderer to consume
export interface IElectronAPI {
  // Command: Invoke a main process function and await result
  runTask: (taskName: string, args: any) => Promise<any>;
  
  // Event: Listen for updates from Main
  onUpdate: (callback: (event: any, value: any) => void) => void;
}

// 2. Expose the API securely
contextBridge.exposeInMainWorld('electronAPI', {
  runTask: (taskName: string, args: any) => ipcRenderer.invoke(
    'run-task', taskName, args
  ),
  onUpdate: (callback: any) => ipcRenderer.on('task-update', callback)
});
```

## 2. Implement Handler in Main (`src/main.ts`)

Handle the invoked commands securely. Validate inputs before executing.

```typescript
import { app, BrowserWindow, ipcMain } from 'electron';

// 1. Register IPC Handlers (Wait for app.whenReady())
app.whenReady().then(() => {
  ipcMain.handle('run-task', async (event, taskName, args) => {
    console.log(`[Main] Task Invoked: ${taskName}`, args);
    
    // SAFETY CHECK: Validate taskName against allowed list
    if (taskName === 'ping') return 'pong';
    
    // TODO: Spawn Sidecar process here (see sidecar_manager skill)
    return { status: 'error', message: 'Unknown task' };
  });

  createWindow();
});
```

## 3. Consume in Renderer (`src/renderer.ts`)

The renderer accesses the API via `window.electronAPI`, which is now type-safe
if augmented.

```typescript
// Add type definition to global window
declare global {
  interface Window {
    electronAPI: IElectronAPI;
  }
}

// Use it
async function execute() {
  const result = await window.electronAPI.runTask('ping', {});
  console.log(result); // 'pong'
}
```
