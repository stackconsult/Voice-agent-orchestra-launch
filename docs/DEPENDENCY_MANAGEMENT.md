# Enhanced AI-OS Dependency Management Guide

## Overview

This document outlines the approved dependency management practices, installation procedures, and troubleshooting guidelines for the Enhanced AI-OS system.

## 🚨 Critical Dependency Issues - RESOLVED

### **Issue 1: Missing Voice Dependencies**
**Problem**: Voice components failed due to missing audio libraries
- `sounddevice` - Audio recording/playback
- `soundfile` - Audio file handling
- `faster-whisper` - Speech transcription
- `pynput` - Keyboard/mouse input
- `numpy` - Numerical operations

**Solution**: Added to `requirements.txt` with version constraints
```bash
# Voice/Audio Dependencies
sounddevice>=0.4.6
soundfile>=0.12.1
faster-whisper>=0.9.0
pynput>=1.7.6
numpy>=1.24.0
aiohttp>=3.9.0
```

### **Issue 2: API Server Import Path Problems**
**Problem**: Relative imports failed when running API server directly
```python
# BROKEN - Relative imports
from .workflows.enhanced_skill_executor import EnhancedSkillExecutor

# FIXED - Absolute imports
from ai_os.workflows.enhanced_skill_executor import EnhancedSkillExecutor
```

**Solution**: Updated import paths in `ai_os/api_server.py`

### **Issue 3: UI Dependencies Not Installed**
**Problem**: Electron and UI dependencies missing
**Solution**: Comprehensive Node.js setup in installation script

### **Issue 4: Environment Configuration Conflicts**
**Problem**: Merge conflicts in `.env.example`
**Solution**: Clean, unified environment configuration

## 📦 Approved Dependencies

### **Core AI Dependencies**
```txt
anthropic>=0.25.0      # Claude API
openai>=1.6.0          # OpenAI API
google-generativeai>=0.3.0  # Gemini API
```

### **System Dependencies**
```txt
PyQt6>=6.6.0           # GUI framework
PyObjC>=9.0            # macOS AppleScript
pydantic>=2.5.0        # Data validation
python-dotenv>=1.0.0   # Environment variables
requests>=2.31.0        # HTTP client
pyyaml>=6.0.1          # YAML parsing
psutil>=5.9.0           # System monitoring
```

### **Voice/Audio Dependencies**
```txt
sounddevice>=0.4.6     # Audio I/O
soundfile>=0.12.1      # Audio files
faster-whisper>=0.9.0  # Speech recognition
pynput>=1.7.6          # Input devices
numpy>=1.24.0          # Numerical computing
aiohttp>=3.9.0         # Async HTTP
```

### **API Server Dependencies**
```txt
fastapi>=0.104.0        # Web framework
uvicorn[standard]>=0.24.0 # ASGI server
python-multipart>=0.0.6  # File uploads
```

### **Enhanced Dependencies**
```txt
aiofiles>=23.0.0       # Async file I/O
jinja2>=3.1.0          # Template engine
python-dateutil>=2.8.0 # Date utilities
```

## 🔧 Installation Procedures

### **Automated Installation (Recommended)**
```bash
# Run complete installation
./install_complete.sh
```

### **Manual Installation**
```bash
# 1. Python environment
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 2. System dependencies
brew install ffmpeg
curl -fsSL https://ollama.ai/install.sh | sh
curl -L https://github.com/ggerganov/whisper.cpp/releases/download/latest/download/whisper.cpp-mac.tar.gz | tar -xzf -C ~/.local/bin

# 3. Node.js environment
cd ui
npm install
npm install -g electron
cd ..

# 4. Environment setup
cp .env.example .env
# Edit .env with your configuration

# 5. Models
ollama pull llama3
```

## 🚀 Startup Procedures

### **API Server**
```bash
# Method 1: Direct
source venv/bin/activate
python3 ai_os/api_server.py

# Method 2: Script
./start_api_server.sh
```

### **UI Application**
```bash
# Method 1: Direct
cd ui
npm start

# Method 2: Script
./start_ui.sh
```

### **CLI Interface**
```bash
# Method 1: Direct
source venv/bin/activate
python3 ai_os/main.py --cli

# Method 2: Script
./start_cli.sh
```

## 🛠️ Troubleshooting Guide

### **Voice Dependencies Issues**
```bash
# If sounddevice fails
brew install portaudio

# If audio recording fails
# Check microphone permissions in System Preferences
# Ensure audio device is available
python3 -c "import sounddevice; print(sounddevice.query_devices())"
```

### **API Server Issues**
```bash
# If imports fail
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
source venv/bin/activate
python3 ai_os/api_server.py

# If port is occupied
lsof -ti:8000 | xargs kill -9
```

### **UI Issues**
```bash
# If Electron fails
npm install -g electron
npm rebuild

# If display issues
export DISPLAY=:0
```

### **Ollama Issues**
```bash
# If Ollama doesn't start
ollama serve &
sleep 5

# If model pull fails
ollama pull llama3
# Or try a smaller model
ollama pull llama3:8b
```

## 📋 Validation Checklist

### **Pre-Installation**
- [ ] Python 3.9+ installed
- [ ] Node.js 16+ installed
- [ ] macOS system confirmed
- [ ] Homebrew available

### **Post-Installation**
- [ ] Virtual environment created
- [ ] All Python dependencies installed
- [ ] Voice dependencies working
- [ ] API server starts successfully
- [ ] UI application launches
- [ ] CLI interface functional
- [ ] Ollama service running
- [ ] Llama3 model available

### **Runtime Validation**
```bash
# Test voice components
python3 -c "import sounddevice, soundfile, faster_whisper; print('Voice OK')"

# Test API server
curl http://localhost:8000/health

# Test UI
electron ui/src/main.js

# Test CLI
python3 ai_os/main.py --help
```

## 🔄 Dependency Updates

### **Update Process**
1. Test new versions in development environment
2. Update `requirements.txt` with new version constraints
3. Update installation script if needed
4. Run full validation suite
5. Update documentation

### **Version Pinning Strategy**
- **Critical dependencies**: Pin to specific versions
- **Standard dependencies**: Use minimum version with compatible range
- **Development dependencies**: Latest stable versions

### **Security Updates**
- Monitor security advisories for all dependencies
- Update vulnerable packages immediately
- Test compatibility before deployment

## 📊 Monitoring and Maintenance

### **Dependency Health Monitoring**
```bash
# Check for outdated packages
pip list --outdated

# Check for security issues
pip-audit

# Validate environment
python3 validate_enhanced_ai_os.py
```

### **Regular Maintenance Tasks**
- Monthly dependency updates
- Quarterly security audits
- Annual dependency review and cleanup

## 🚫 Prohibited Dependencies

### **Unsupported Packages**
- Python 2.x packages
- Deprecated libraries
- Packages with known security vulnerabilities
- Non-maintained packages

### **Conflict Prevention**
- Avoid conflicting version requirements
- Prevent circular dependencies
- Minimize dependency bloat
- Use virtual environments consistently

## 📚 Best Practices

### **Development**
- Always use virtual environments
- Pin dependency versions for production
- Test in clean environments
- Document all dependency changes

### **Deployment**
- Use the automated installation script
- Validate all dependencies before deployment
- Monitor dependency health in production
- Have rollback procedures ready

### **Troubleshooting**
- Check logs for dependency errors
- Use isolated environments for testing
- Document all issues and solutions
- Share fixes with the team

---

**Last Updated**: 2024-01-01  
**Version**: 1.0.0  
**Status**: Production Ready
