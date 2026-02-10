# Electron for UI Deployments: Deep Research & Antigravity IDE Integration Analysis

Based on comprehensive research of Electron's official documentation and your
Antigravity IDE framework, I've analyzed Electron as a universally versatile
deployment option for your automation consulting builds.

## Executive Summary: Electron Fit Assessment

**A) Is Electron a Fit for You?** ✅ **YES - Highly Recommended**

Electron aligns exceptionally well with your profile as an automation consultant
building agents and MCP databases. It provides:

- **Cross-platform deployment** (Windows, macOS, Linux) from single codebase
- **Native desktop capabilities** with familiar web technologies
- **Enterprise-grade stability** used by VSCode, Slack, Discord, ChatGPT, Claude
- **Full Node.js integration** for automation workflows and backend logic
- **Offline-first architecture** perfect for client tools

**B) Is Electron Better Than Everything Else?** ⚖️ **Context-Dependent**

### Choose Electron When

- Building B2B automation tools requiring desktop presence
- Need filesystem access, system integrations, native APIs
- Want to leverage existing web development skills (HTML/CSS/JS)
- Clients need offline functionality or data privacy
- Building cross-platform with single codebase priority

#### Choose Alternatives When

- Pure web apps (use standard web stack)
- Small disk footprint critical (<80MB is hard requirement)
- Building games or real-time 3D graphics
- OS-native UI frameworks required (SwiftUI/WinUI)
- Resource-constrained IoT devices

**C) Seamless Antigravity + Electron Integration** 🚀 **Highly Compatible**

---

## Electron Architecture Deep Dive

### Process Model

Electron inherits Chromium's multi-process architecture:[^1_1]

#### Main Process (Node.js environment)

- Single process per app - application entry point
- Controls lifecycle via `app` module
- Window management with `BrowserWindow`
- Native API access (menus, dialogs, system tray)
- Privileged operations coordinator

#### Renderer Processes (Web environment)

- One per `BrowserWindow` - isolated sandboxed processes
- Runs HTML/CSS/JavaScript like web pages
- No direct Node.js/Electron API access (security)
- Communicates with main via IPC

#### Preload Scripts (Bridge layer)

- Executes before renderer content loads
- Has Node.js API access + renderer context
- Uses `contextBridge` to safely expose APIs[^1_2]
- Enables secure main ↔ renderer communication

#### Utility Processes (Node.js environment)

- Optional child processes from main[^1_1]
- For CPU-intensive tasks, crash-prone components
- Can communicate with renderers via MessagePort

### Security Architecture

Electron implements **defense-in-depth security**:[^1_3]

**Context Isolation** (Default since v12)

- Separates preload scripts from renderer website code
- Prevents malicious sites accessing Electron internals
- Uses `contextBridge.exposeInMainWorld()` for safe API exposure

**Process Sandboxing** (Default since v20)

- Limits renderer access to system resources[^1_4]
- Only CPU/memory freely accessible
- Privileged operations delegated to main via IPC
- Preload scripts get polyfilled Node.js subset

**Security Checklist** (20 recommendations):[^1_3]

1. Only load secure content (HTTPS)
2. Disable Node.js integration for remote content
3. Enable context isolation
4. Enable process sandboxing
5. Validate IPC message senders
6. Use custom protocols vs `file://`
7. Content Security Policy enforcement
8. Keep Electron version current

---

## Inter-Process Communication (IPC)

IPC is critical for feature-rich desktop apps:[^1_5]

### Pattern 1: Renderer → Main (One-Way)

```javascript
// Preload: Expose API
contextBridge.exposeInMainWorld('electronAPI', {
  setTitle: (title) => ipcRenderer.send('set-title', title),
});

// Main: Listen
ipcMain.on('set-title', (event, title) => {
  const win = BrowserWindow.fromWebContents(event.sender);
  win.setTitle(title);
});
```

### Pattern 2: Renderer → Main (Two-Way)

```javascript
// Preload: Expose invoke
contextBridge.exposeInMainWorld('electronAPI', {
  openFile: () => ipcRenderer.invoke('dialog:openFile')
})

// Main: Handle with return
ipcMain.handle('dialog:openFile', async () => {
  const { filePaths } = await dialog.showOpenDialog()
  return filePaths[0]
})

// Renderer: Await response
const path = await window.electronAPI.openFile()
```

### Pattern 3: Main → Renderer

```javascript
// Main: Send to specific window
mainWindow.webContents.send('update-counter', 1);

// Preload: Expose listener
contextBridge.exposeInMainWorld('electronAPI', {
  onUpdateCounter: (callback) =>
    ipcRenderer.on('update-counter', (_event, value) => callback(value)),
});
```

---

## Packaging & Distribution

### Electron Forge (Recommended Tool)[^1_6]

#### Setup

```bash
npm install --save-dev @electron-forge/cli
npx electron-forge import
```

#### Build Process

```bash
npm run make  # Creates distributables
```

#### Output Structure

```text
out/
├── make/zip/darwin/x64/app-darwin-x64-1.0.0.zip
└── app-darwin-x64/app.app/Contents/MacOS/app
```

#### Platform-Specific Formats

- **Windows**: MSI installers, Squirrel (auto-update)
- **macOS**: DMG, .app bundles (requires code signing)
- **Linux**: deb, rpm, AppImage

**Code Signing** (Mandatory for production):

- **macOS**: Requires Apple Developer certificate + notarization[^1_6]
- **Windows**: Authenticode certificate for SmartScreen trust
- **Critical for**: Auto-updates, user trust, enterprise deployment

---

## Performance Optimization

### Key Recommendations:[^1_7]

#### 1. Lazy Module Loading

```javascript
// Bad: Load upfront
const heavyModule = require('heavy-module')

// Good: Load on-demand
async getParsedFiles() {
  const parser = require('heavy-module') // Only when needed
  return parser.parse(await this.getFiles())
}
```

#### 2. Bundle Your Code

- Use webpack/rollup/parcel
- Single file reduces `require()` overhead
- 50-200ms savings on startup

#### 3. Avoid Blocking Main Process

- Use worker threads for CPU-heavy tasks
- Async I/O operations only
- Never `ipcRenderer.sendSync()`[^1_7]

#### 4. Remove Unnecessary Polyfills

- Electron bundles latest Chromium
- No need for jQuery, babel-polyfill for modern features
- Check caniuse.com for Chromium version

#### 5. Bundle Static Resources

- Include fonts/images locally vs CDN
- Faster load, offline support
- Example: Download Google Fonts vs linking

**6. Disable Default Menu** (if custom/frameless)

```javascript
Menu.setApplicationMenu(null); // Before app.ready
```

**Typical App Size**: 80-100MB zipped (includes Chromium + Node.js runtime)[^1_8]

---

## Antigravity IDE Integration Strategy

### Perfect Synergy Points

**1. Agent-First Development Model**[^1_1] [^1_3]

Antigravity's agent orchestration maps beautifully to Electron:

- **Planning Agent** → Defines Electron app architecture
- **Frontend Agent** → Builds renderer process UI (Angular/React/Vue)
- **Backend Agent** → Develops main process logic + IPC handlers
- **Testing Agent** → Creates E2E tests with Electron's test tools
- **Browser Agent** → Validates UI through Electron's browser integration

**2. Multi-Surface Control**[^1_1]

Antigravity operates across:

- **Code Editor** → Electron main/renderer/preload files
- **Terminal** → `npm run make`, Forge commands
- **Integrated Browser** → Test renderer processes in real-time

**3. Artifact-Based Verification**[^1_3]

Antigravity's artifact system complements Electron development:

- **Screenshots** → Capture BrowserWindow renders
- **Browser Recordings** → Document IPC flows, window interactions
- **Implementation Plans** → Architecture decisions (process model, IPC patterns)
- **Test Results** → Renderer + main process test suites

**4. Tech Stack Whitelisting**[^1_1]

Configure `.antigravity/config.json`:

```json
{
  "techStack": {
    "runtime": ["node", "electron"],
    "frontend": ["react", "angular", "vue"],
    "packageManager": ["npm", "yarn"],
    "bundler": ["webpack", "vite"]
  }
}
```

---

## Electron + Antigravity Workflow Template

### Phase 1: Project Initialization (ASDLC Explore)

#### Prompt to Planning Agent

```text
Create an Electron desktop app for [your automation tool]:
- Main process: Handle file operations, system integration
- Renderer: Angular dashboard with Material UI
- IPC: Secure channel for file operations
- Package: Cross-platform with Electron Forge
- Tech stack: Electron 32+, Angular 17, TypeScript
```

#### Agent Produces

- `PLAN.md` with architecture decisions
- Directory structure matching Electron conventions
- Security checklist (context isolation, sandboxing)

### Phase 2: Implementation (ASDLC Plan → Execute)

#### AGENTS.md Kernel Configuration

```markdown
## Product Vision

B2B automation tool as Electron desktop app

## Allowed Operations

- npm install/run
- electron-forge commands
- File system operations (main process only)
- IPC channel creation

## Forbidden Actions

- Disabling context isolation
- Disabling sandbox without justification
- Loading untrusted remote content
```

### Multi-Agent Execution

1. **Coding Agent** → Generates main.js, preload.js, renderer code
2. **UI Agent** → Creates Angular components in renderer
3. **Browser Agent** → Tests IPC patterns, validates security

### Phase 3: Verification (ASDLC Reflect)

#### Artifacts Generated

- Screenshots of packaged app on each platform
- Browser recordings of IPC communication flows
- Security audit checklist completion
- Performance profiling results

### Phase 4: Skill Crystallization

#### Store in `.antigravity/skills/electron-ipc-pattern.md`

```markdown
# Skill: Secure Electron IPC Pattern

## Metadata

- **Reusability**: High
- **Category**: Desktop Development
- **Tech**: Electron, IPC

## Context

Safe pattern for renderer ↔ main communication

## Implementation

[Preload + contextBridge + ipcMain.handle template]

## Testing

[Security validation checklist]
```

---

## CONSTITUTION.md Alignment for Electron

**Lethal Trifecta Prevention**:[^1_5]

```markdown
## Electron-Specific Constraints

### NEVER combine:

1. Remote content loading (untrusted input)
2. Node integration enabled (private data access)
3. Context isolation disabled (exfiltration channel)

### Circuit Breakers:

- `webPreferences.nodeIntegration: true` → Require approval + justification
- `webPreferences.contextIsolation: false` → Block execution
- Remote URL loading → Validate domain whitelist

### Transparency Logging:

- Log all IPC channel registrations
- Document security-sensitive `webPreferences`
- Track `shell.openExternal()` calls with user content
```

---

## Recommended Tech Stack for Your Builds

### Frontend (Renderer Process)

- **Angular** (your Antigravity expertise)[^1_1]
- **React + TypeScript** (Antigravity-compatible)
- **Tailwind CSS** (rapid styling)
- **Material UI / Bootstrap** (component libraries)

### Main Process

- **Node.js 20+ APIs** (bundled with Electron)
- **Better-sqlite3** (local database for automation data)
- **Node-pty** (terminal automation integration)
- **@electron/remote** (use sparingly, security risk)

### Build & Deployment

- **Electron Forge** (packaging/distribution)
- **electron-builder** (alternative packager)
- **electron-updater** (auto-update infrastructure)
- **GitHub Actions** (CI/CD for multi-platform builds)

### Testing

- **Spectron** (E2E Electron testing - deprecated, use WebdriverIO)
- **Playwright Electron** (modern E2E testing)
- **Jest** (unit tests for main/renderer)

---

## Decision Matrix: When to Use Electron

| **Scenario**                                      | **Use Electron?** | **Rationale**                                             |
| :------------------------------------------------ | :---------------- | :-------------------------------------------------------- |
| B2B automation dashboard for client installations | ✅ **YES**        | Offline-first, filesystem access, system integration      |
| Agent orchestration control panel                 | ✅ **YES**        | Native feel, always-available, terminal integration       |
| MCP database management tool                      | ✅ **YES**        | Local data security, SQL tooling, multi-window            |
| Social media scheduling tool                      | ⚠️ **MAYBE**      | Consider PWA first; Electron if notifications/tray needed |
| Public-facing SaaS web app                        | ❌ **NO**         | Standard web stack better (no 100MB downloads)            |
| Mobile-first application                          | ❌ **NO**         | Use React Native or Flutter                               |
| Real-time collaboration tool                      | ⚠️ **MAYBE**      | Hybrid: Web primary, Electron for power users             |
| Document generation pipeline                      | ✅ **YES**        | Headless Chromium rendering, PDF generation               |

---

## Actionable Next Steps

### Immediate (This Week)

1. **Create Electron Skill** in
   `.antigravity/skills/electron-scaffold.md`

2. **Update AGENTS.md** with Electron as allowed tech stack
3. **Whitelist commands** in CONSTITUTION.md: `electron`, `electron-forge`,
   `npm run make`

4. **Build POC**: Simple automation tool with Antigravity → Electron workflow

### Short-Term (This Month)

1. **Standardize template**: Create Antigravity-compatible Electron boilerplate
2. **Document IPC patterns**: Store 3-4 common patterns as reusable skills
3. **CI/CD pipeline**: GitHub Actions for multi-platform Electron builds
4. **Security audit**: Validate all builds against 20-point checklist[^1_3]

### Long-Term (This Quarter)

1. **Portfolio migration**: Convert 2-3 web tools to Electron desktop apps
2. **Client offering**: "Desktop Automation Tool Development" service
3. **Content creation**: YouTube tutorials on Antigravity + Electron workflows
4. **Community leadership**: Share Electron + AI agent patterns on LinkedIn

---

## Conclusion & Recommendation

**Electron is an EXCELLENT fit for your automation consulting business** because:

✅ **Aligns with your expertise**: Web tech (Angular/React) you know
✅ **Enables offline B2B tools**: Critical for enterprise clients
✅ **Integrates seamlessly with Antigravity**: Agent-first development perfect
for Electron's complexity
✅ **Cross-platform efficiency**: Single codebase = 3 platforms
✅ **Enterprise credibility**: VSCode/Slack validation
✅ **Node.js ecosystem**: Full access to automation libraries

### Make Electron your default for

- Desktop automation dashboards
- Agent orchestration interfaces
- Local-first data tools
- System integration utilities

#### Avoid Electron for

- Public web apps (use web stack)
- Mobile-first experiences (use RN/Flutter)
- Ultra-lightweight tools (<10MB requirement)

**Your competitive advantage**: Combining Antigravity's agent-orchestration with
Electron's desktop capabilities creates a unique offering — "AI-Built,
Enterprise-Grade Desktop Automation Tools" that competitors can't easily
replicate.

---

## Electron Phase 2: Development, Node Modules, Distribution, Testing & Debugging

Based on comprehensive research of Electron's advanced documentation, I've
analyzed the critical components for production deployment, native module
integration, testing infrastructure, and debugging workflows—all calibrated for
Antigravity IDE integration.

---

## Native Node Modules Integration

### The ABI Challenge

Electron uses **Chromium's BoringSSL** instead of OpenSSL, creating a different
Application Binary Interface (ABI) from standard Node.js. Native modules must be
recompiled for Electron or you'll encounter version mismatch errors.[^2_1]

### Solution: `@electron/rebuild`

**Automatic Rebuilding** (Recommended):

```bash
npm install --save-dev @electron/rebuild

# After every npm install:
./node_modules/.bin/electron-rebuild
```

**Electron Forge Integration**: If using Forge, rebuilding happens automatically
in development and during packaging.[^2_1]

**Manual Rebuilding** (Advanced):

```bash
HOME=~/.electron-gyp node-gyp rebuild \
  --target=32.0.0 \
  --arch=x64 \
  --dist-url=https://electronjs.org/headers
```

## Windows-Specific: `win_delay_load_hook`

Critical for Electron 4+: Native modules must include delay-load hooks in
`binding.gyp`:[^2_1]

```python
'win_delay_load_hook': 'true'
```

This redirects `node.dll` references to `electron.exe`. Without it, modules fail
with "Module did not self-register" errors.

### Prebuild Support

Modules using **`prebuild`** or **`node-pre-gyp`** can provide pre-compiled
Electron binaries. Use `@electron/rebuild` as fallback when Electron-specific
binaries aren't available.[^2_1]

---

## Application Distribution

### Distribution Strategy Matrix

| **Method**                       | **Use Case**       | **Complexity** | **Antigravity Fit**                 |
| :------------------------------- | :----------------- | :------------- | :---------------------------------- |
| **Electron Forge** (Recommended) | Complete toolchain | Low            | ✅ **Excellent** - Agent automation |
| **Electron Packager**            | Manual control     | Medium         | ⚠️ Moderate - More scripting        |
| **Electron Builder**             | Community favorite | Medium         | ⚠️ Moderate - Different ecosystem   |
| **Manual Packaging**             | Learning/debugging | High           | ❌ Not recommended                  |

### Packaging with Electron Forge

**Complete Workflow**:[^2_2]

```bash
# Package app for distribution
npm run package  # Creates platform-specific builds

# Generate installers/executables
npm run make     # macOS: DMG, Windows: MSI/Squirrel, Linux: deb/rpm

# Output structure:
out/
├── make/
│   ├── zip/darwin/x64/app-1.0.0.zip
│   └── squirrel.windows/x64/app-1.0.0-setup.exe
└── app-darwin-x64/
    └── MyApp.app
```

## ASAR Archives (Application Packaging)

**What is ASAR?** A simple extensive archive format that bundles source code:[^2_3]

- **Performance**: Faster `require()` on Windows (reduces file I/O)
- **Obfuscation**: Basic protection from cursory inspection
- **Path length**: Mitigates Windows long path issues

**Creating ASAR**:

```bash
npm install -g @electron/asar
asar pack app app.asar
```

**Automatic in Forge**: Packaging creates `app.asar` by default, placed in:

- macOS: `MyApp.app/Contents/Resources/app.asar`
- Windows: `resources/app.asar`
- Linux: `resources/app.asar`

**Working with ASAR**:[^2_3]

```javascript
// Node APIs work transparently
require('/path/to/app.asar/module.js');
fs.readFileSync('/path/to/app.asar/file.txt');

// Web APIs use file:// protocol
win.loadURL('file:///path/to/app.asar/index.html');
```

**Unpacking Native Modules**:

```bash
asar pack app app.asar --unpack "*.node"
# Creates app.asar.unpacked/ folder - ship both together
```

## ASAR Integrity Validation

**Enable via Fuse**:[^2_4]

```javascript
const { flipFuses, FuseV1Options } = require('@electron/fuses');

flipFuses(require('electron'), {
  [FuseV1Options.EnableEmbeddedAsarIntegrityValidation]: true,
  [FuseV1Options.OnlyLoadAppFromAsar]: true, // Security hardening
});
```

This validates `app.asar` content on every load, preventing tampering—critical
for B2B security posture.

---

## Code Signing (Production Requirement)

### macOS Code Signing

**Prerequisites**:[^2_5]

1. Apple Developer Program membership (\$99/year)
2. Xcode installed (requires macOS)
3. Developer certificate downloaded

**Electron Forge Auto-Signing**:

```javascript
// forge.config.js
module.exports = {
  packagerConfig: {
    osxSign: {},
    osxNotarize: {
      appleId: process.env.APPLE_ID,
      appleIdPassword: process.env.APPLE_ID_PASSWORD,
      teamId: process.env.APPLE_TEAM_ID,
    },
  },
};
```

**Notarization**: Required for macOS 10.15+. Apple scans your app for malware;
without it, users see "unidentified developer" warnings.[^2_5]

### Windows Code Signing

**2023+ Requirement**: **Extended Validation (EV) certificates** mandatory:[^2_5]

- Traditional "authenticode" certificates no longer remove SmartScreen warnings
- EV certificates stored on FIPS 140 Level 2 hardware (USB tokens)
- **Cloud-based signing** services (DigiCert KeyLocker, SSL.com) solve CI/CD challenges

**Azure Trusted Signing** (New, Cheapest Option):

- Microsoft's cloud alternative to EV certificates
- \$9.99/month base pricing
- Available to US/Canada businesses (3+ years) or individual developers
- Eliminates SmartScreen warnings

**Forge Integration**:[^2_5]

```javascript
// forge.config.js
module.exports = {
  packagerConfig: {
    windowsSign: {
      signWithParams:
        '--azure-key-vault-url=... --azure-key-vault-certificate=...',
    },
  },
};
```

### Why Code Signing Matters for B2B

**Without Code Signing**:

- Windows: "Windows protected your PC" full-screen warning
- macOS: "cannot be opened because it is from an unidentified developer"
- Enterprise IT blocks installation via Group Policy

**With Code Signing**:

- ✅ Silent installation
- ✅ Enterprise trust
- ✅ Professional credibility
- ✅ Required for auto-updates

---

## Auto-Update Infrastructure

### Update Strategy Decision Tree

| **Option**                         | **Best For**                 | **Cost**  | **Complexity** |
| :--------------------------------- | :--------------------------- | :-------- | :------------- |
| **Static Storage (S3/CloudFlare)** | Private apps, custom control | ~\$1-5/mo | Low            |
| **update.electronjs.org**          | Open source GitHub projects  | Free      | Minimal        |
| **Hazel (Vercel)**                 | Quick deployment             | Free tier | Low            |
| **Nuts/Nucleus**                   | Enterprise, private repos    | Self-host | Medium         |

### Serverless Updates (Recommended for Automation Tools)

**Architecture**:[^2_6]

1. Upload release + metadata to S3/CloudFlare R2
2. App checks metadata URL on startup
3. Downloads update in background
4. Prompts user to restart

**Metadata Structure**:

**macOS** (`releases.json`):

```json
{
  "currentRelease": "1.2.3",
  "releases": [
    {
      "version": "1.2.3",
      "updateTo": {
        "url": "https://cdn.example.com/MyApp-1.2.3-darwin-x64.zip",
        "pub_date": "2026-02-09T12:00:00+00:00",
        "notes": "Bug fixes and performance improvements"
      }
    }
  ]
}
```

**Windows** (`RELEASES` file):

```text
B0892F3C7AC91D72A6271FF36905FEF8FE993520 MyApp-1.2.3-full.nupkg 103298365
```

**Implementation**:[^2_6]

```javascript
// main.js
const { updateElectronApp, UpdateSourceType } = require('update-electron-app');

updateElectronApp({
  updateSource: {
    type: UpdateSourceType.StaticStorage,
    baseUrl: `https://my-cdn.com/releases/${process.platform}/${process.arch}`,
  },
});
```

### Update Events (User Experience)

```javascript
const { autoUpdater } = require('electron');

autoUpdater.on('update-downloaded', (event, releaseNotes, releaseName) => {
  dialog
    .showMessageBox({
      type: 'info',
      title: 'Update Available',
      message: 'A new version has been downloaded. Restart to apply?',
      buttons: ['Restart', 'Later'],
    })
    .then((result) => {
      if (result.response === 0) autoUpdater.quitAndInstall();
    });
});

autoUpdater.on('error', (err) => {
  console.error('Update error:', err);
});
```

---

## Automated Testing

### Testing Framework Comparison

| **Framework**   | **Type**         | **Electron Support** | **Antigravity Integration**      |
| :-------------- | :--------------- | :------------------- | :------------------------------- |
| **Playwright**  | E2E              | Experimental CDP     | ✅ **Best** - Modern, maintained |
| **WebdriverIO** | E2E              | Native Electron      | ✅ **Excellent** - Specialized   |
| **Selenium**    | E2E              | Via ChromeDriver     | ⚠️ Legacy approach               |
| **Custom IPC**  | Unit/Integration | Full control         | ✅ **Advanced** - Lightweight    |

### Playwright (Modern E2E Testing)

**Why Playwright?**:[^2_7]

- Built on Chrome DevTools Protocol
- Access to main process modules
- Screenshot/video recording
- TypeScript native

**Setup**:

```bash
npm install --save-dev @playwright/test
```

**Example Test**:[^2_7]

```javascript
import { test, expect, _electron as electron } from '@playwright/test';

test('automation tool launches', async () => {
  const electronApp = await electron.launch({ args: ['.'] });

  // Test main process
  const isPackaged = await electronApp.evaluate(async ({ app }) => {
    return app.isPackaged;
  });
  expect(isPackaged).toBe(false);

  // Test renderer
  const window = await electronApp.firstWindow();
  await window.screenshot({ path: 'test-screenshot.png' });

  // Validate UI elements
  await expect(window.locator('#dashboard')).toBeVisible();

  await electronApp.close();
});
```

**Run Tests**:

```bash
npx playwright test  # Matches *.spec.js, *.test.js
```

### WebdriverIO (Electron-Specific)

**Advantages**:[^2_7]

- Official Electron service plugin
- Auto-detects packaged apps (Forge/Builder)
- Direct Electron API access

**Setup**:

```bash
npm init wdio@latest ./
# Select "Desktop Testing - Electron Applications"
```

**Configuration** (`wdio.conf.js`):

```javascript
export const config = {
  services: ['electron'],
  capabilities: [
    {
      browserName: 'electron',
      'wdio:electronServiceOptions': {
        appBinaryPath: './out/MyApp-darwin-x64/MyApp.app',
        appArgs: ['foo', 'bar=baz'],
      },
    },
  ],
};
```

**Test Example**:[^2_7]

```javascript
import { browser, $, expect } from '@wdio/globals';

describe('IPC communication', () => {
  it('sends data to main process', async () => {
    await browser.electron.execute((electron) => {
      const win = electron.BrowserWindow.getFocusedWindow();
      electron.dialog.showMessageBox(win, {
        message: 'Test dialog from automation',
      });
    });
  });
});
```

## Custom Test Driver (Lightweight)

**For Antigravity Agents**:[^2_7]

```javascript
// testDriver.js
class TestDriver {
  constructor({ path, args, env }) {
    env.APP_TEST_DRIVER = 1;
    this.process = childProcess.spawn(path, args, {
      stdio: ['inherit', 'inherit', 'inherit', 'ipc'],
      env,
    });

    this.process.on('message', (message) => {
      const rpcCall = this.rpcCalls[message.msgId];
      if (message.reject) rpcCall.reject(message.reject);
      else rpcCall.resolve(message.resolve);
    });
  }

  async rpc(cmd, ...args) {
    const msgId = this.rpcCalls.length;
    this.process.send({ msgId, cmd, args });
    return new Promise((resolve, reject) =>
      this.rpcCalls.push({ resolve, reject }),
    );
  }
}

// Usage with Ava/Jest/Mocha
const app = new TestDriver({
  path: electronPath,
  args: ['./app'],
  env: { NODE_ENV: 'test' },
});

test('validates automation workflow', async (t) => {
  await app.rpc('runAutomation', 'test-data.csv');
  const result = await app.rpc('getResults');
  expect(result.success).toBe(true);
});
```

---

## Debugging Workflows

### VSCode Debugging (Primary Method)

**Main Process Debugging**:[^2_8]

**`.vscode/launch.json`**:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug Main Process",
      "type": "node",
      "request": "launch",
      "cwd": "${workspaceFolder}",
      "runtimeExecutable": "${workspaceFolder}/node_modules/.bin/electron",
      "windows": {
        "runtimeExecutable": "${workspaceFolder}/node_modules/.bin/electron.cmd"
      },
      "args": ["."],
      "outputCapture": "std"
    }
  ]
}
```

**Features**:

- Breakpoints in main.js, preload.js
- Variable inspection
- Call stack navigation
- Console output

**Renderer Process Debugging**:

- Open DevTools: `Ctrl+Shift+I` (Windows/Linux) or `Cmd+Option+I` (macOS)
- Sources tab for breakpoints
- Console for logging
- Network tab for IPC monitoring

### REPL (Interactive Debugging)

**Access Main Process REPL**:[^2_7]

```bash
electron --inspect=5858 .
```

Then connect Chrome DevTools to `chrome://inspect`.

**Context Inspection**:

```javascript
// In DevTools Console (main process context)
const { app, BrowserWindow } = require('electron');
app.getName(); // Check app details
BrowserWindow.getAllWindows(); // Inspect windows
```

### Headless CI Testing

**GitHub Actions Example**:[^2_7]

```yaml
name: Test Electron App
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 20

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: xvfb-run --auto-servernum npm test
        env:
          CI: true
```

**`xvfb-run`**: Provides virtual display for Linux CI environments where GUI
apps can't render.

---

## Electron Fuses (Security Hardening)

### What Are Fuses

**"Magic bits"** in the Electron binary flipped at package time to disable
unused features. OS code signing prevents tampering.[^2_4]

### Critical Fuses for B2B Automation Tools

| **Fuse**                           | **Default** | **Recommendation** | **Rationale**                          |
| :--------------------------------- | :---------- | :----------------- | :------------------------------------- |
| `runAsNode`                        | Enabled     | ❌ **Disable**     | Prevents "living off the land" attacks |
| `cookieEncryption`                 | Disabled    | ✅ **Enable**      | Encrypts cookies with OS keychain      |
| `nodeOptions`                      | Enabled     | ❌ **Disable**     | Blocks NODE_OPTIONS injection          |
| `nodeCliInspect`                   | Enabled     | ❌ **Disable**     | Prevents debug mode exploitation       |
| `embeddedAsarIntegrityValidation`  | Disabled    | ✅ **Enable**      | Validates app.asar integrity           |
| `onlyLoadAppFromAsar`              | Disabled    | ✅ **Enable**      | Blocks loading unvalidated code        |
| `grantFileProtocolExtraPrivileges` | Enabled     | ❌ **Disable**     | Removes unnecessary file:// privileges |

### Flipping Fuses

**Using `@electron/fuses`**:[^2_4]

```javascript
const { flipFuses, FuseVersion, FuseV1Options } = require('@electron/fuses');

flipFuses(
  require('electron'), // Path to electron binary
  {
    version: FuseVersion.V1,
    [FuseV1Options.RunAsNode]: false,
    [FuseV1Options.EnableCookieEncryption]: true,
    [FuseV1Options.EnableNodeOptionsEnvironmentVariable]: false,
    [FuseV1Options.EnableNodeCliInspectArguments]: false,
    [FuseV1Options.EnableEmbeddedAsarIntegrityValidation]: true,
    [FuseV1Options.OnlyLoadAppFromAsar]: true,
    [FuseV1Options.GrantFileProtocolExtraPrivileges]: false,
  },
);
```

**Forge Integration**:

```javascript
// forge.config.js
plugins: [
  [
    '@electron-forge/plugin-fuses',
    {
      version: FuseVersion.V1,
      [FuseV1Options.RunAsNode]: false,
      [FuseV1Options.EnableCookieEncryption]: true,
      // ... other fuses
    },
  ],
];
```

**Verify Fuses**:

```bash
npx @electron/fuses read --app /Applications/MyApp.app
```

---

## ES Modules (ESM) Support

### ESM Support Matrix[^2_9]

| **Context**            | **ESM Loader** | **Notes**                             |
| :--------------------- | :------------- | :------------------------------------ |
| Main Process           | Node.js        | Requires `.mjs` or `"type": "module"` |
| Renderer (Sandboxed)   | Chromium       | No Node.js APIs, no npm modules       |
| Renderer (Unsandboxed) | Chromium       | Still no Node.js in imports           |
| Preload Scripts        | Node.js        | Must use `.mjs` extension             |

### Main Process ESM[^2_9]

**Enable ESM**:

```json
// package.json
{
  "type": "module",
  "main": "main.js"
}
```

**Critical Caveat**: Use `await` liberally before `app.ready`:

```javascript
// ❌ BAD: Dynamic import may resolve after app is ready
import('./setup-paths.js');
app.whenReady().then(() => console.log('Ready!'));

// ✅ GOOD: Await ensures setup completes first
await import('./setup-paths.js');
app.whenReady().then(() => console.log('Ready!'));
```

### Preload Scripts ESM[^2_9]

**Requirements**:

1. Must use `.mjs` extension (ignores `"type": "module"`)
2. Context isolation required for dynamic imports
3. Sandboxed renderers cannot use ESM preloads

```javascript
// preload.mjs
import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('electronAPI', {
  sendData: (data) => ipcRenderer.invoke('process-data', data),
});
```

---

## Antigravity IDE Integration Strategy (2)

### Phase 2 Skill Crystallization

**Store in `.antigravity/skills/electron-production.md`**:

````markdown
# Skill: Electron Production Deployment Pipeline

## Metadata

- **Category**: Desktop Development
- **Complexity**: Advanced
- **Reusability**: High

## Context

Complete workflow for packaging, signing, and distributing Electron apps with auto-updates.

## Prerequisites

- Electron Forge configured
- Code signing certificates (macOS: Developer ID, Windows: EV/Azure)
- Cloud storage for updates (S3/CloudFlare R2)

## Implementation

### 1. Native Module Handling

```bash
npm install --save-dev @electron/rebuild
## Automatic rebuild in Forge
```text
````

### 2. Security Fuses

```javascript
// forge.config.js plugins
[
  '@electron-forge/plugin-fuses',
  {
    [FuseV1Options.RunAsNode]: false,
    [FuseV1Options.EnableEmbeddedAsarIntegrityValidation]: true,
    [FuseV1Options.OnlyLoadAppFromAsar]: true,
  },
];
```

### 3. Code Signing

```javascript
// forge.config.js packagerConfig
osxSign: {},
osxNotarize: { appleId: process.env.APPLE_ID, ... },
windowsSign: { signWithParams: '...' }
```

### 4. Auto-Updates

```javascript
// main.js
const { updateElectronApp } = require('update-electron-app');
updateElectronApp({
  updateSource: {
    type: 'StaticStorage',
    baseUrl: 'https://cdn.example.com/releases/...',
  },
});
```

### 5. Testing

```javascript
// playwright.config.js
import { test, _electron } from '@playwright/test';
test('app launches', async () => {
  const app = await _electron.launch({ args: ['.'] });
  // ... assertions
  await app.close();
});
```

## Testing Checklist

- [ ] Native modules rebuilt for Electron
- [ ] ASAR integrity validation enabled
- [ ] Code signed for target platforms
- [ ] Auto-update tested on staging server
- [ ] E2E tests pass in headless CI
- [ ] Fuses flipped and verified

## Circuit Breakers

- Block packaging if code signing fails
- Require manual approval for fuse changes
- Validate update server accessibility before release

```text`

### AGENTS.md Electron Configuration

```markdown
## Tech Stack
- Runtime: Node.js 20+, Electron 32+
- Frontend: Angular 17 / React 18
- Packaging: Electron Forge
- Testing: Playwright

## Allowed Operations
- `npm run package` / `npm run make`
- `@electron/rebuild` execution
- `@electron/fuses` configuration
- Cloud storage uploads (S3/R2)
- Code signing with environment credentials

## Forbidden Actions
- Manual binary patching
- Disabling security fuses without justification
- Skipping code signing in production builds
- Loading remote content without HTTPS + CSP

## Verification Artifacts
- Screenshots of packaged app on macOS/Windows/Linux
- Code signing validation output
- Fuse configuration readout
- Playwright test results with coverage
- Update server response validation
```text`

### CI/CD Pipeline for Agents

**GitHub Actions Workflow**:

```yaml
name: Build & Release Electron App

on:
  push:
    tags: ['v*']

jobs:
  build:
    strategy:
      matrix:
        os: [macos-latest, windows-latest, ubuntu-latest]

    runs-on: ${{ matrix.os }}

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: 20

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm test

      - name: Build & Package
        run: npm run make
        env:
          APPLE_ID: ${{ secrets.APPLE_ID }}
          APPLE_ID_PASSWORD: ${{ secrets.APPLE_ID_PASSWORD }}
          WINDOWS_SIGN_PARAMS: ${{ secrets.WINDOWS_SIGN_PARAMS }}

      - name: Upload to S3
        run: |
          aws s3 sync out/make/ s3://my-app-updates/${{ runner.os }}/
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_KEY }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET }}
```text

---

## Decision Framework: Production Readiness Checklist

### Before First Client Deployment

| **Component**       | **Status** | **Action**                                |
| :------------------ | :--------- | :---------------------------------------- |
| **Native Modules**  | ⬜         | Verify all modules rebuild successfully   |
| **Code Signing**    | ⬜         | Obtain certificates (macOS + Windows)     |
| **Security Fuses**  | ⬜         | Flip production-recommended fuses         |
| **ASAR Integrity**  | ⬜         | Enable validation fuse                    |
| **Auto-Update**     | ⬜         | Configure S3/CloudFlare + test deployment |
| **E2E Testing**     | ⬜         | Implement Playwright/WDIO tests           |
| **CI/CD Pipeline**  | ⬜         | Automate builds for 3 platforms           |
| **Error Reporting** | ⬜         | Integrate Sentry/Bugsnag                  |

### Security Hardening Score

**Target for B2B Enterprise**: 8/8 ✅

- [ ] Code signed (macOS + Windows)
- [ ] `runAsNode` fuse disabled
- [ ] `nodeOptions` fuse disabled
- [ ] ASAR integrity validation enabled
- [ ] `onlyLoadAppFromAsar` enabled
- [ ] Context isolation enabled
- [ ] Process sandboxing enabled
- [ ] No `nodeIntegration` in renderers

---

## Conclusion: Phase 2 Integration

### Key Takeaways

**1. Native Modules = Non-Negotiable Rebuild**

- Always use `@electron/rebuild`
- Test on target platforms early
- Use prebuilt binaries when available (better-sqlite3, node-pty)

**2. Code Signing = Table Stakes for B2B**

- Budget \$200-500/year for certificates
- Azure Trusted Signing cheapest for Windows (\$9.99/mo)
- macOS notarization mandatory—no workarounds

**3. Auto-Updates = Competitive Advantage**

- Serverless (S3) approach costs ~\$2-5/month
- Silent background updates improve UX
- Critical for rapid bug fixes in client deployments

**4. Testing = Insurance Policy**

- Playwright best for modern workflows
- Custom IPC drivers for Antigravity agent testing
- Headless CI with `xvfb-run` on Linux

**5. Fuses = Defense in Depth**

- Flip 7 production fuses before first deployment
- Validate with `@electron/fuses read`
- Document in CONSTITUTION.md

### Antigravity + Electron = Production Pipeline

**Agent Orchestration Maps to**:

1. **Planning Agent** → Defines Forge config, fuses, update strategy
2. **Coding Agent** → Implements main/renderer/preload code
3. **Testing Agent** → Writes Playwright tests, validates builds
4. **Build Agent** → Executes `npm run make`, flips fuses, signs binaries
5. **Distribution Agent** → Uploads to S3, updates metadata files
6. **Verification Agent** → Downloads update, validates integrity, tests installation

**Workflow Artifacts**:

- Implementation plans for distribution strategy
- Screenshots of packaged apps (3 platforms)
- Code signing validation logs
- Fuse configuration reports
- Update server curl responses
- Playwright test videos

### Next Steps

**Ready for Phase 3**: Containerization research?

Before proceeding, **immediate actions**:

1. **Obtain certificates**: Start Apple Developer + Azure Trusted Signing applications (1-2 week lead time)
2. **Create prototype**: Build minimal Electron app via Antigravity with Forge
3. **Test full pipeline**: Package → Sign → Upload → Auto-update on staging
4. **Document workflow**: Crystallize as reusable Antigravity skill

Your automation consulting business now has a **production-grade Electron deployment framework** that can deliver enterprise-ready desktop tools with:

- ✅ Cross-platform support (Windows/macOS/Linux)
- ✅ Secure code signing and updates
- ✅ Automated testing and CI/CD
- ✅ Professional security posture
- ✅ Agent-orchestrated development

**Competitive moat**: Combining Antigravity's agent orchestration with Electron's production tooling creates a unique capability—"AI-Built, Enterprise-Deployed Desktop Automation" that traditional developers can't match for speed or reliability.

---

## Phase 3: Strategic Containerization & Layered Architecture

Based on deep research into Electron's advanced patterns and your requirement for "containerized components," I have developed a **Universally Versatile Architecture** that integrates Electron, Docker, and MCP into a cohesive layered system.

This strategy redefines "containerization" for your builds in three distinct dimensions:

1. **Process Containers**: Isolating automation logic (Sidecars).
2. **Service Containers**: Dockerizing local databases/backends.
3. **Logic Containers**: Encapsulating agent capabilities via MCP.

---

## The 5-Layer "Antigravity" Electron Architecture

To "Layer it out" effectively, we move beyond the basic Main/Renderer model to a robust 5-layer architecture. This ensures your automation tools are modular, crash-resistant, and infinitely scalable.

### Layer 1: The Presentation Layer (Renderer Process)

_The "Face" of your automation._

- **Role**: Pure UI rendering. No heavy lifting.
- **Tech**: Angular (your expertise) or React.
- **Constraint**: **Zero Node.js access**. Strictly sandboxed.
- **Antigravity Agent**: `Frontend Agent` scaffolds this using your existing UI skills.

### Layer 2: The Bridge Layer (Preload & Context Isolation)

_The "Secure Conduit."_

- **Role**: The only path between UI and Logic.
- **Mechanism**: `contextBridge.exposeInMainWorld`.
- **Strategy**: Define typed API contracts (e.g., `window.automation.runTask()`).
- **Antigravity Agent**: `Coding Agent` generates these strict TypeScript interfaces.

### Layer 3: The Application Layer (Main Process)

_The "Orchestrator."_

- **Role**: Window management, system menus, update handling.
- **Strategy**: Keep this **thin**. It delegates actual work to Layer 4.
- **Key Pattern**: Use `ipcMain.handle` to route requests from Layer 1 to Layer 4.

### Layer 4: The "Sidecar" Container Layer (Critical for Automation)

_The "Engine Room" – Where your consultant value lives._

- **Concept**: Run automation scripts (Python, Go, specialized Node binaries) as separate child processes managed by Electron.
- **Why**:
  - **Stability**: If a Python script crashes, the UI stays alive.
  - **Versatility**: Use Python for AI/Data libraries (Pandas, PyTorch) that Node.js struggles with.
  - **MCP Integration**: Host local MCP Servers here.[^3_1]
- **Implementation**: Use `utilityProcess` or `child_process.spawn`.

### Layer 5: The Infrastructure Layer (Dockerized Components)

_The "Foundation."_

- **Concept**: Databases (PostgreSQL, Vector DBs) running in Docker containers on the user's machine, managed by the Electron app.
- **Use Case**: Local "mcp databases" for persistent agent memory.
- **Strategy**: Electron checks/starts Docker containers on launch using the Sidecar layer.

---

## Deep Dive: The Sidecar Strategy (Automation & MCP)

This is the most critical component for your "Automation Consultant" persona. It allows you to package complex agentic behaviors into the desktop app.

### A. The Python Sidecar Pattern

For automations requiring Python libraries (e.g., Selenium, AI models):

1. **Package**: Bundle a standalone Python executable (using PyInstaller) inside the Electron app (ASAR unpacked).
2. **Spawn**: Main process spawns the Python executable.
3. **Communicate**: Use **StdIO** (Standard Input/Output) or **ZeroMQ** for fast message passing between Electron (Node) and Python.

**Antigravity Workflow**:

> "Agent, create a Python sidecar that runs a Selenium scraper. Set up the IPC channel so the Angular frontend can trigger the scrape and receive real-time status updates."

### B. The Local MCP Hub Pattern

Your Electron app becomes a **Client** and **Host** for MCP Servers.[^3_2][^3_1]

- **Internal Host**: The app spawns an internal MCP server (e.g., a "FileSystem MCP" or "Postgres MCP") as a sidecar.
- **External Client**: The app can connect to Claude Desktop or other agents via MCP.
- **Benefits**: Your desktop app exposes its internal tools (e.g., "Get Client Data") to other AI agents on the system.

---

## Seamless Integration with Antigravity IDE

Here is how to integrate this architecture into your Agentic Workflow:

### 1. The `PLAN.md` Architecture Template

When starting a new build, instruct the Planning Agent to use this structure:

```markdown
## Project Architecture: Electron-Sidecar-MCP

## Layers

1. **Frontend**: Angular 17 (Renderer)
2. **Bridge**: Preload.ts (Context Isolated)
3. **Core**: Main.ts (Orchestrator)
4. **Sidecar**: /sidecars/python-automation (PyInstaller)
5. **Data**: /docker/docker-compose.yml (Local Vector DB)

## Inter-Process Communication

- Frontend -> Main: IPC 'invoke'
- Main -> Sidecar: StdIO / JSON-RPC
- Sidecar -> Main: Events
```text

### 2. Antigravity Skill: "Scaffold Sidecar"

Create a reusable skill in `.antigravity/skills/electron-sidecar.md`:

- **Input**: "Add a Python sidecar for data processing."
- **Action**:

1. Create `/sidecars/python/main.py`.
2. Configure `pyinstaller` build script.
3. Add `child_process.spawn` logic to `main.ts`.
4. Update `forge.config.js` to include the binary.

### 3. Containerized Build Pipeline (Docker)

Ensure **Reproducibility** by building inside Docker (Layering the _Build_ process).

- Use `electron-userland/builder:wine` Docker image for CI/CD.
- Allows building Windows `.exe` and Linux `.deb` from your Mac/Linux workstation without VM overhead.

---

## Strategy: Is Electron "Better"?

**Verdict**: For your specific "Automation Consultant" goals: **YES**.

| Feature                | Web App          | Electron + Sidecars      | Winner                |
| :--------------------- | :--------------- | :----------------------- | :-------------------- |
| **System Access**      | Restricted       | Full (Filesystem, Shell) | **Electron**          |
| **Python Integration** | Server-side only | Local Sidecar (Offline)  | **Electron**          |
| **MCP Hosting**        | Remote HTTP      | Local Process/StdIO      | **Electron**          |
| **Data Privacy**       | Cloud            | Local (Docker/SQLite)    | **Electron**          |
| **Deployment**         | URL              | Installer (.exe/.dmg)    | **Context Dependent** |

**Why it wins for you**: It allows you to deliver **"Agent-in-a-Box"** solutions. You hand a client an `.exe` that contains the UI, the AI Logic (Sidecar), and the Database (SQLite/Docker), running entirely on their machine.

---

## Next Steps

We have covered:

1. **Fit**: Electron is the right vessel.
2. **Deployment**: Forge, Signing, and Updates are solved.
3. **Architecture**: The 5-Layer Sidecar/MCP model is the strategy.

**Strategic Recommendation**:
Your "Antigravity" framework is now theoretically complete for Desktop Agents.

- **Frontend**: Angular
- **Backend**: Node.js Main Process + Python Sidecars
- **Brain**: MCP Servers running locally

**Call to Action**:
We can now move to **Synthesizing the Master Playbook**. I can generate the specific `AGENTS.md`, `ARCHITECTURE.md`, and `CONSTITUTION.md` file content tailored for this Electron-MCP-Sidecar stack to finalize your Antigravity template.

---

## Avid Antigravity Electron-MCP Playbook

This playbook represents the **crystallized result** of our deep dive. It is the definitive guide for your "Automation Consultant" builds, merging Antigravity's agentic workflow with Electron's enterprise capabilities and MCP's intelligence.

[^4_1]

---

## 1. AGENTS.md (The Kernel)

This file defines the operating system for your agents. It authorizes them to use Electron, Sidecars, and MCP.

```markdown
## AGENTS.md - Avid Antigravity Electron Kernel

## 1. IDENTITY & PURPOSE

You are an expert Automation Architect building "Agent-in-a-Box" desktop
solutions. Your goal is to ship robust, offline-first tools that combine Angular
UIs, Node.js orchestration, and Python/MCP intelligence.

## 2. TECH STACK (Whitelisted)

- **Runtime**: Node.js 20+ (Main), Python 3.11+ (Sidecars)
- **Frontend**: Angular 17+ (Renderer), TailwindCSS
- **Core**: Electron 32+, Electron Forge
- **Data**: Better-SQLite3, Docker (pgvector)
- **Intelligence**: Model Context Protocol (MCP)

## 3. ARCHITECTURE TIERS

1.  **Renderer**: Zero-Node UI. Communications via `window.electronAPI`.
2.  **Preload**: The secure bridge. Typesafe context exposure.
3.  **Main**: Process manager. No heavy business logic here.
4.  **Sidecars**: Python/Go binaries for heavy automation/AI tasks.
5.  **Infra**: Dockerized local services managed by the app.

## 4. OPERATIONAL COMMANDS

- `npm run start`: Launch dev environment with hot-reload.
- `npm run make`: Build production binaries (Mac/Win/Linux).
- `npm run sidecar:build`: Compile Python scripts via PyInstaller.
- `docker compose up`: Start local infrastructure.

## 5. FORBIDDEN ACTIONS (Circuit Breakers)

- ❌ Enabling `nodeIntegration: true` in Renderer.
- ❌ Disabling `contextIsolation`.
- ❌ Hardcoding API keys (Use OS Keychain via `keytar`).
- ❌ Blocking the Main Process (Use Worker Threads or Sidecars).
- ❌ Shipping without Code Signing.

## 6. PRODUCT VISION

> "We build tools that give B2B clients superpowers on their local machines, independent of the cloud, secure by design."
```text

---

## 2. ARCHITECTURE.md (The Blueprint)

This defines the structural laws your agents must follow when scaffolding.

````markdown
## ARCHITECTURE.md - The 5-Layer Electron Pattern

## Layer 1: The Presentation (UI)

- **Path**: `/src/renderer`
- **Tech**: Angular Standalone Components.
- **Rule**: Pure display logic. Requests data via `window.electronAPI`.

## Layer 2: The Bridge (Security)

- **Path**: `/src/preload/index.ts`
- **Rule**: Expose specific functions only. NEVER expose `ipcRenderer` directly.
- **Pattern**:
  ```typescript
  contextBridge.exposeInMainWorld('automation', {
    runTask: (id: string) => ipcRenderer.invoke('task:run', id),
    onStatus: (cb) => ipcRenderer.on('task:status', cb),
  });
  ```

## Layer 3: The Orchestrator (Main)

- **Path**: `/src/main/index.ts`
- **Rule**: Routes traffic. Validates inputs. Spawns Sidecars.
- **Feature**: Auto-Update logic lives here.

## Layer 4: The Intelligence (Sidecars)

- **Path**: `/sidecars/python` or `/sidecars/mcp`
- **Build**: Compiled to single binaries via PyInstaller.
- **Communication**: Stdio (Standard Input/Output) JSON streams.
- **MCP Host**: The Main process acts as an MCP Host for these sidecars.

## Layer 5: The Memory (Data)

- **Path**: `/docker` or `app.getPath('userData')`
- **Storage**: SQLite for app state. Docker for vector/relational data.
- **Backup**: Automated dumps to JSON artifacts.
```text`

---

## 3. CONSTITUTION.md (The Conscience)

This ensures your agents never violate security or reliability principles.

```markdown
## CONSTITUTION.md - Development Constraints

## 1. The Lethal Trifecta (PREVENTION)

NEVER allow a build that combines:

1.  **Remote Content Loading** (External URLs in WebView)
2.  **Node Integration Enabled** (Direct OS Access)
3.  **Context Isolation Disabled** (Bridge Bypass)
    _Violation = Immediate Halt._

## 2. The Sidecar Mandate

"Heavy lifting belongs in the background."

- IF a task takes >100ms, IT MOVES to a Sidecar or Worker.
- IF a task requires Python, IT IS a compiled Sidecar.

## 3. Verification by Artifact

- Every PR must include a **Screenshot** of the UI.
- Every Core Logic change requires a **Playwright Test** video.
- Every Release Build requires a **Code Signing Validation** log.

## 4. Offline First

- The app must function without internet.
- AI features gracefully degrade or switch to local models (Ollama) if offline.
```text

---

## 4. MCP Integration Strategy (The "Brain")

Your app needs to speak "MCP" natively.

### A. Hosting an MCP Server (Internal)

Your app _is_ an MCP server to itself.
**Pattern**: Use `@modelcontextprotocol/sdk` in the Main Process.

```javascript
// src/main/mcp-server.ts
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from
'@modelcontextprotocol/sdk/server/stdio.js';

const server = new McpServer({ name: 'AvidAutomation', version: '1.0.0' });

server.tool('scrape_linkedin', { url: z.string() }, async ({ url }) => {
  // Call Python Sidecar here
  return sidecar.exec('scrape', url);
});

// Connects to stdio for external agents to use YOUR app as a tool
const transport = new StdioServerTransport();
await server.connect(transport);
```text

### B. Connecting to MCP Clients (External)

Your app can connect to _other_ agents (like Claude Desktop).
**Pattern**: Add a "Connect to Agent" button in your Angular UI that spawns a connection to an external MCP host.

---

## 5. Deployment Checklist (The "Go" Signal)

Before you ship to a client, run this **Avid Verification Protocol**:

1. **Unit Tests**: `npm run test` (Logic verified?)
2. **E2E Tests**: `npm run e2e` (Playwright clicked through the UI?)
3. **Sidecar Check**: Does the Python binary run on a _clean_ machine?
4. **Signing**: Is the binary Green-Checked by SmartScreen/Gatekeeper?
5. **Updates**: Does the app detect a fake "v+1" on your S3 bucket?

---

## Implementation Plan

1. **Initialize**: Run `npm init electron-app@latest my-automation-tool -- --template=typescript-webpack`.
2. **Inject**: Copy the `AGENTS.md`, `ARCHITECTURE.md`, `CONSTITUTION.md` files into the root.
3. **Scaffold**: Ask your Antigravity Agent:
   > "Review ARCHITECTURE.md. Scaffold the Angular frontend and the Python Sidecar structure. Ensure the IPC bridge is typed according to Layer 2 rules."

You now have a **Universally Versatile** factory for building enterprise-grade automation tools. This is the "Avid Antigravity" standard.

---

# References

[^1_1]: Antigravity-fullstack-use-cases.md

[^1_2]: Antigravity-Front-end-ui-use-case.docx

[^1_3]: antigravity-professional-use-case.md

[^1_4]: setup.js.pdf

[^1_5]: CONSTITUTION.md

[^1_6]: ARCHITECTURE.md

[^1_7]: TASKS.md

[^1_8]: AGENTS.md

[^2_1]: Antigravity-fullstack-use-cases.md

[^2_2]: Antigravity-Front-end-ui-use-case.docx

[^2_3]: antigravity-professional-use-case.md

[^2_4]: setup.js.pdf

[^2_5]: CONSTITUTION.md

[^2_6]: ARCHITECTURE.md

[^2_7]: TASKS.md

[^2_8]: AGENTS.md

[^2_9]: README.md

[^3_1]: <https://mcpmarket.com/server/electron>

[^3_2]: <https://github.com/amafjarkasi/electron-mcp-server>

[^4_1]: antigravity-professional-use-case.md

---

## References

[^1_1]: Antigravity-fullstack-use-cases.md

[^1_2]: Antigravity-Front-end-ui-use-case.docx

[^1_3]: antigravity-professional-use-case.md

[^1_4]: setup.js.pdf

[^1_5]: CONSTITUTION.md

[^1_6]: ARCHITECTURE.md

[^1_7]: TASKS.md

[^1_8]: AGENTS.md

[^2_1]: Antigravity-fullstack-use-cases.md

[^2_2]: Antigravity-Front-end-ui-use-case.docx

[^2_3]: antigravity-professional-use-case.md

[^2_4]: setup.js.pdf

[^2_5]: CONSTITUTION.md

[^2_6]: ARCHITECTURE.md

[^2_7]: TASKS.md

[^2_8]: AGENTS.md

[^2_9]: README.md

[^3_1]: <https://mcpmarket.com/server/electron>

[^3_2]: <https://github.com/amafjarkasi/electron-mcp-server>

[^4_1]: antigravity-professional-use-case.md

---

## References

[^1_1]: Antigravity-fullstack-use-cases.md

[^1_2]: Antigravity-Front-end-ui-use-case.docx

[^1_3]: antigravity-professional-use-case.md

[^1_4]: setup.js.pdf

[^1_5]: CONSTITUTION.md

[^1_6]: ARCHITECTURE.md

[^1_7]: TASKS.md

[^1_8]: AGENTS.md

[^2_1]: Antigravity-fullstack-use-cases.md

[^2_2]: Antigravity-Front-end-ui-use-case.docx

[^2_3]: antigravity-professional-use-case.md

[^2_4]: setup.js.pdf

[^2_5]: CONSTITUTION.md

[^2_6]: ARCHITECTURE.md

[^2_7]: TASKS.md

[^2_8]: AGENTS.md

[^2_9]: README.md

[^3_1]: <https://mcpmarket.com/server/electron>

[^3_2]: <https://github.com/amafjarkasi/electron-mcp-server>

[^4_1]: antigravity-professional-use-case.md

