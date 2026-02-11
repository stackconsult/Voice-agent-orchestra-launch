---
description: Dependency management workflow for Enhanced AI-OS
---

# Enhanced AI-OS Dependency Management Workflow

## 🎯 Objective

Ensure all Enhanced AI-OS components use approved dependencies and follow proper installation procedures to prevent deployment failures.

## 🔄 Workflow Steps

### **Phase 1: Environment Validation**
```bash
# 1. Check system requirements
python3 --version  # Must be 3.9+
node --version     # Must be 16+
brew --version     # Must be installed

# 2. Validate project structure
ls -la requirements.txt .env.example install_complete.sh
```

### **Phase 2: Dependency Installation**
```bash
# 3. Run automated installation
./install_complete.sh

# 4. Validate installation
source venv/bin/activate
python3 validate_enhanced_ai_os.py
```

### **Phase 3: Service Startup**
```bash
# 5. Start services in correct order
./start_api_server.sh    # Terminal 1
./start_ui.sh           # Terminal 2 (optional)
```

## ⚠️ Common Failure Points

### **Voice Dependencies**
- **Issue**: `ModuleNotFoundError: sounddevice`
- **Fix**: Run `brew install portaudio` then reinstall dependencies
- **Prevention**: Always run complete installation script

### **API Server Imports**
- **Issue**: `ImportError: attempted relative import`
- **Fix**: Use absolute imports: `from ai_os.workflows.enhanced_skill_executor import`
- **Prevention**: Never use relative imports in entry point files

### **UI Dependencies**
- **Issue**: `electron: command not found`
- **Fix**: `npm install -g electron` then `npm rebuild`
- **Prevention**: Use automated installation script

### **Environment Configuration**
- **Issue**: Missing `.env` file
- **Fix**: `cp .env.example .env` then configure
- **Prevention**: Always copy template during installation

## 🚫 Prohibited Actions

### **Never Do These**
1. **Install dependencies without virtual environment**
2. **Use pip install outside venv**
3. **Run API server with relative imports**
4. **Skip environment configuration**
5. **Install voice deps manually without system deps**
6. **Use npm install without electron setup**

### **Always Do These**
1. **Use `./install_complete.sh` for installation**
2. **Validate with `python3 validate_enhanced_ai_os.py`**
3. **Use startup scripts for service management**
4. **Check system requirements before installation**
5. **Test in clean environment before deployment**

## 🔧 Troubleshooting Procedures

### **Step 1: Environment Check**
```bash
# Check Python environment
which python3
python3 --version
source venv/bin/activate
which python  # Should point to venv

# Check Node.js environment
which node
which npm
node --version
npm --version
```

### **Step 2: Dependency Validation**
```bash
# Test critical imports
python3 -c "
import sounddevice, soundfile, faster_whisper
import fastapi, uvicorn, anthropic, openai
print('All dependencies OK')
"

# Test API server
timeout 5s python3 ai_os/api_server.py
```

### **Step 3: Service Health Check**
```bash
# Check API server
curl http://localhost:8000/health

# Check Ollama
ollama list

# Check voice devices
python3 -c "import sounddevice; print(sounddevice.query_devices())"
```

## 📊 Success Criteria

### **Installation Success**
- [ ] All dependencies installed without errors
- [ ] Virtual environment functional
- [ ] API server starts successfully
- [ ] UI application launches
- [ ] Voice components operational
- [ ] Validation script passes

### **Runtime Success**
- [ ] API endpoints respond correctly
- [ ] Skills execute without import errors
- [ ] Voice recording works
- [ ] UI connects to backend
- [ ] Error handling functional

## 🔄 Recovery Procedures

### **Complete Reinstall**
```bash
# Clean slate
rm -rf venv
rm -rf node_modules
rm -rf ui/node_modules

# Fresh install
./install_complete.sh
```

### **Partial Recovery**
```bash
# Python dependencies only
source venv/bin/activate
pip install -r requirements.txt

# Node.js dependencies only
cd ui && npm install && cd ..

# Voice dependencies only
brew install portaudio ffmpeg
pip install sounddevice soundfile faster-whisper
```

## 📋 Monitoring Checklist

### **Pre-Deployment**
- [ ] Run `python3 validate_enhanced_ai_os.py`
- [ ] Test all startup scripts
- [ ] Verify environment configuration
- [ ] Check system requirements

### **Post-Deployment**
- [ ] Monitor API server logs
- [ ] Check UI console for errors
- [ ] Validate voice functionality
- [ ] Test skill execution

### **Ongoing**
- [ ] Weekly dependency health check
- [ ] Monthly security updates
- [ ] Quarterly full validation
- [ ] Annual dependency review

## 🎯 Agent Guidelines

### **For Installation Agents**
1. Always use `install_complete.sh`
2. Validate system requirements first
3. Check for conflicts before installation
4. Document any deviations from standard procedure

### **For Development Agents**
1. Test dependency changes in isolation
2. Update requirements.txt with version constraints
3. Validate all import paths
4. Update documentation for any changes

### **For Deployment Agents**
1. Never deploy without running validation
2. Use approved startup scripts only
3. Monitor service health after deployment
4. Have rollback procedures ready

### **For Troubleshooting Agents**
1. Check environment first
2. Validate all dependencies
3. Test services individually
4. Document all issues and solutions

---

**Status**: Production Ready  
**Last Updated**: 2024-01-01  
**Version**: 1.0.0
