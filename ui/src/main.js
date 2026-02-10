const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const axios = require('axios');

// Enhanced AI-OS API Configuration
const API_BASE_URL = 'http://localhost:8000';

let mainWindow;
let apiServerProcess;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
            webSecurity: false
        },
        icon: path.join(__dirname, '../assets/icon.png'),
        title: 'Enhanced AI-OS - Skill Engine UI'
    });

    // Load the HTML file
    mainWindow.loadFile(path.join(__dirname, '../public/index.html'));

    // Open DevTools in development
    if (process.argv.includes('--dev')) {
        mainWindow.webContents.openDevTools();
    }

    // Handle window closed
    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

// IPC Handlers for API Communication
ipcMain.handle('api-health-check', async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/health`);
        return { success: true, data: response.data };
    } catch (error) {
        console.error('Health check failed:', error.message);
        return { success: false, error: error.message };
    }
});

ipcMain.handle('api-list-skills', async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/skills`);
        return { success: true, data: response.data };
    } catch (error) {
        console.error('List skills failed:', error.message);
        return { success: false, error: error.message };
    }
});

ipcMain.handle('api-execute-skill', async (event, skillName, context = {}) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/execute`, {
            name: skillName,
            context: context
        });
        return { success: true, data: response.data };
    } catch (error) {
        console.error('Execute skill failed:', error.message);
        return { success: false, error: error.message };
    }
});

ipcMain.handle('api-generate-skill', async (event, prompt, author = 'AI-OS User') => {
    try {
        const response = await axios.post(`${API_BASE_URL}/generate`, {
            prompt: prompt,
            author: author
        });
        return { success: true, data: response.data };
    } catch (error) {
        console.error('Generate skill failed:', error.message);
        return { success: false, error: error.message };
    }
});

ipcMain.handle('api-analyze-task', async (event, description) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/analyze`, {
            description: description
        });
        return { success: true, data: response.data };
    } catch (error) {
        console.error('Analyze task failed:', error.message);
        return { success: false, error: error.message };
    }
});

ipcMain.handle('api-get-skill-details', async (event, skillName) => {
    try {
        const response = await axios.get(`${API_BASE_URL}/skill/${skillName}/details`);
        return { success: true, data: response.data };
    } catch (error) {
        console.error('Get skill details failed:', error.message);
        return { success: false, error: error.message };
    }
});

ipcMain.handle('api-delete-skill', async (event, skillName) => {
    try {
        const result = await dialog.showMessageBox(mainWindow, {
            type: 'warning',
            buttons: ['Cancel', 'Delete'],
            defaultId: 0,
            message: `Delete Skill: ${skillName}`,
            detail: 'This action cannot be undone. Are you sure you want to delete this skill and all its files?'
        });

        if (result.response === 1) { // Delete button
            const response = await axios.delete(`${API_BASE_URL}/skill/${skillName}`);
            return { success: true, data: response.data };
        } else {
            return { success: false, error: 'User cancelled deletion' };
        }
    } catch (error) {
        console.error('Delete skill failed:', error.message);
        return { success: false, error: error.message };
    }
});

// App Event Handlers
app.whenReady().then(() => {
    createWindow();

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

// Error handling
process.on('uncaughtException', (error) => {
    console.error('Uncaught Exception:', error);
    if (mainWindow) {
        dialog.showErrorBox('Uncaught Exception', error.message);
    }
});

process.on('unhandledRejection', (reason, promise) => {
    console.error('Unhandled Rejection at:', promise, 'reason:', reason);
    if (mainWindow) {
        dialog.showErrorBox('Unhandled Rejection', reason.toString());
    }
});

console.log('Enhanced AI-OS UI started');
