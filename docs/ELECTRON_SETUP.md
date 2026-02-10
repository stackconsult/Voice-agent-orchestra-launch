# Electron "Downloadable Wizard" Setup Guide

This guide details how to build the professional setup version of Antigravity applications for client deployment.

---

## 1. Professional UI Principles

- **Aesthetics**: High-contrast dark mode, glassmorphism, and smooth transitions.
- **Micro-animations**: Progress bars for installation/setup, hover effects on action buttons.
- **Clarity**: Step-by-step wizard interface (Prerequisites -> Configuration -> Initialization).

## 2. Technical Requirements

- **Runtime**: Electron 32+ (Node 24+).
- **Packaging**: Electron Forge with `@electron-forge/maker-squirrel` (Windows) or `@electron-forge/maker-dmg` (macOS).
- **Database**: `better-sqlite3` for local state persistence.

## 3. The Setup Flow

1. **Welcome Screen**: Brand intro and License Agreement.
2. **Dependency Check**: Automatically verify if Node.js/Git are installed.
3. **Configuration**: User enters API keys (OpenAI, Anthropic, etc.) and workspace path.
4. **Initialization**: Scaffolds the `.antigravity/` folder and pulls necessary containers.
5. **Launch**: Hands off control to the main Antigravity IDE.

## 4. Building the Installer

```bash
# Generate production installers
npm run make

# The installers will be located in:
# Windows: ./out/make/squirrel.windows/x64/
# macOS: ./out/make/MyApp-x64.dmg
```

## 5. Security Posture

- **Code Signing**: Essential for avoiding "Untrusted Developer" warnings.
- **Fuses**: Enable `OnlyLoadAppFromAsar` to prevent local source tampering.
- **Context Bridge**: Ensure all sensitive Node.js APIs are gated behind a secure preload bridge.
