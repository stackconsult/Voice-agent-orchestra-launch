# Enhanced AI-OS UI - Electron Integration

## 🚀 Overview

This is the Electron UI application for the Enhanced AI-OS Skill Engine. It provides a modern, user-friendly interface for interacting with the AI-OS backend API.

## 📦 Installation

### Prerequisites
- Node.js 16+ 
- Enhanced AI-OS backend running (see main README)

### Setup
```bash
cd ui
npm install
```

## 🎯 Features

### **Core Functionality**
- 📚 **Skill Management**: View, execute, and manage AI skills
- 🎨 **Skill Generation**: Create new skills from natural language
- 🧠 **Task Analysis**: Analyze tasks to recommend execution modes
- ⚡ **Real-time Execution**: Monitor skill execution in real-time
- 🏥 **Health Monitoring**: System status and health checks

### **UI Components**
- **Modern Interface**: Gradient backgrounds, smooth animations
- **Responsive Design**: Adapts to different screen sizes
- **Real-time Updates**: Live status indicators
- **Error Handling**: User-friendly error messages
- **Dark Mode**: Professional appearance

## 🔧 Configuration

### API Server Connection
The UI connects to the Enhanced AI-OS API server at `http://localhost:8000`.

Ensure the API server is running:
```bash
cd ..  # Back to project root
python ai_os/api_server.py
```

### Development Mode
```bash
npm run dev
```

### Production Build
```bash
npm run build
```

## 🎮 Usage

### **Starting the Application**
```bash
npm start
```

### **Main Tabs**

#### 📚 Skills Tab
- View all available skills
- Execute skills with one click
- View skill details
- Delete unwanted skills

#### 🎨 Generate Tab
- Create new skills from descriptions
- Automatic model selection
- Progressive loading architecture
- YAML frontmatter generation

#### 🧠 Analyze Tab
- Analyze task descriptions
- Get execution mode recommendations
- Model selection reasoning
- Security requirements

#### ⚡ Execute Tab
- Direct skill execution
- Real-time progress monitoring
- Execution logs
- Error reporting

## 🔌 API Integration

### **IPC Communication**
The UI uses Electron's IPC system to communicate with the Node.js backend:

```javascript
// Example: Execute a skill
const result = await ipcRenderer.invoke('api-execute-skill', skillName);
```

### **API Endpoints**
- `GET /health` - System health check
- `GET /skills` - List all skills
- `POST /execute` - Execute a skill
- `POST /generate` - Generate a new skill
- `POST /analyze` - Analyze a task
- `GET /skill/{name}/details` - Get skill details
- `DELETE /skill/{name}` - Delete a skill

## 🎨 UI Features

### **Design System**
- **Colors**: Purple gradient theme (#667eea to #764ba2)
- **Typography**: System fonts for native feel
- **Animations**: Smooth transitions and hover effects
- **Icons**: Emoji icons for universal understanding

### **Status Indicators**
- **Connected**: Green dot when API is reachable
- **Disconnected**: Red dot when API is down
- **Loading**: Spinner animations during operations

### **Error Handling**
- **User-friendly messages**: Clear, actionable error descriptions
- **Graceful degradation**: UI continues working during API issues
- **Retry mechanisms**: Automatic health checks and retry logic

## 🛠️ Development

### **File Structure**
```
ui/
├── src/
│   └── main.js          # Electron main process
├── public/
│   └── index.html       # UI application
├── package.json         # Dependencies and scripts
└── README.md           # This file
```

### **Key Technologies**
- **Electron**: Desktop application framework
- **Axios**: HTTP client for API calls
- **Vanilla JS**: No frontend framework dependencies
- **CSS3**: Modern styling with animations

### **Debugging**
- **DevTools**: Built-in Chrome DevTools in development mode
- **Console Logging**: Detailed logging for debugging
- **Error Reporting**: Comprehensive error handling

## 🔒 Security

### **Security Features**
- **Local API Only**: Connects to localhost API server
- **No External Requests**: All API calls are local
- **Input Validation**: User inputs are validated before sending
- **Error Sanitization**: Error messages are sanitized for display

### **Best Practices**
- **Content Security**: No inline scripts or unsafe content
- **API Authentication**: Ready for API key integration
- **Data Privacy**: No data sent to external services

## 🚀 Deployment

### **Development**
```bash
npm run dev
```

### **Production**
```bash
npm run build
```

### **Distribution**
The application can be packaged for:
- **Windows**: .exe installer
- **macOS**: .dmg package  
- **Linux**: .AppImage or .deb

## 🐛 Troubleshooting

### **Common Issues**

#### **API Connection Failed**
- Ensure API server is running on port 8000
- Check network connectivity
- Verify CORS settings

#### **Skill Execution Errors**
- Check skill file permissions
- Verify skill syntax
- Review API server logs

#### **UI Not Loading**
- Clear application cache
- Restart Electron app
- Check console for errors

### **Debug Mode**
Enable debug mode for detailed logging:
```bash
npm run dev
```

## 📚 Related Documentation

- [Main Enhanced AI-OS README](../README.md)
- [API Server Documentation](../ai_os/api_server.py)
- [Error Handling Workflow](../docs/ERROR_HANDLING_WORKFLOW.md)
- [Enhanced Skill Engine](../docs/)

## 🤝 Contributing

When contributing to the UI:
1. Test all functionality
2. Check for console errors
3. Verify API integration
4. Update documentation
5. Follow error handling workflow

## 📄 License

MIT License - see main project LICENSE file for details.
