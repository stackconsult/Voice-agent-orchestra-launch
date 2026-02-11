# Local LLM Agent Troubleshooting Guide

## Overview

This document addresses common issues with the Local LLM Agent and provides comprehensive troubleshooting procedures.

## 🚨 Common Issues & Solutions

### **Issue 1: URL Parsing Errors**
**Symptoms**: 
```
ERROR: Connection test failed: HTTPConnectionPool(host='http', port=80)
```

**Root Cause**: LocalLMAgent not reading environment variables correctly

**Solution**: ✅ FIXED - All LocalLMAgent instantiations now use:
```python
base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
```

**Files Fixed**:
- `ai_os/agents/offline_online_context_switcher.py`
- `ai_os/workflows/enhanced_skill_generator.py`
- `ai_os/workflows/skill_generator.py`
- `ai_os/agents/local_lm_agent.py`

### **Issue 2: Connection Refused**
**Symptoms**:
```
ERROR: Connection test failed: HTTPConnectionPool(host='localhost', port=11434): 
Max retries exceeded with url: /api/tags (Caused by NewConnectionError: 
Failed to establish a new connection: [Errno 61] Connection refused)
```

**Root Cause**: Ollama service not running

**Solution**: Start Ollama service
```bash
# Start Ollama
ollama serve

# Or install if not present
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3
```

### **Issue 3: macOS Compatibility**
**Symptoms**:
```
Error: kLSIncompatibleSystemVersionErr: The app cannot run on the current OS version
```

**Root Cause**: Ollama version incompatible with macOS 12.7.6 (Monterey)

**Solution**: Install compatible Ollama version
```bash
# Download compatible binary (v0.1.17 for macOS 12.7.6)
curl -L https://github.com/ollama/ollama/releases/download/v0.1.17/ollama-darwin -o ollama-binary
chmod +x ollama-binary
sudo mv ollama-binary /usr/local/bin/ollama

# Start service
nohup ollama serve > ollama.log 2>&1 &
```

### **Issue 4: Disk Space Full**
**Symptoms**:
```
Error: no space left on device
```

**Root Cause**: Insufficient disk space for model downloads

**Solution**: Clear disk space or use smaller models
```bash
# Check disk space
df -h

# Use smaller models (if space available)
ollama pull qwen2:0.5b  # ~300MB vs 4.7GB for llama3

# Or clear space in ~/Downloads, ~/Desktop, etc.
```

### **Issue 3: Proxy Interference**
**Symptoms**: Requests to localhost being routed through proxy

**Solution**: ✅ FIXED - Added proxy bypass for local connections
```python
session = requests.Session()
session.trust_env = False  # Don't use proxy settings
```

## 🔧 Troubleshooting Procedures

### **Step 1: Environment Validation**
```bash
# Check environment variables
echo $OLLAMA_BASE_URL

# Should output: http://localhost:11434 (or your custom URL)
```

### **Step 2: Service Status Check**
```bash
# Check if Ollama is running
ollama list

# If command fails, start Ollama
ollama serve &
```

### **Step 3: URL Parsing Test**
```bash
# Test URL parsing (should show correct host/port)
python3 -c "
from ai_os.agents.local_lm_agent import LocalLMAgent
agent = LocalLMAgent()
print(f'Base URL: {agent.base_url}')
"
```

### **Step 4: Connection Test**
```bash
# Test direct connection
curl http://localhost:11434/api/tags

# Should return list of models or connection error
```

## 📋 Environment Configuration

### **Required Environment Variables**
```bash
# Local LLM Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3

# Optional: Custom Ollama URL
OLLAMA_BASE_URL=http://192.168.1.100:11434
```

### **Environment Setup**
```bash
# Copy template
cp .env.example .env

# Edit configuration
nano .env

# Load environment
source .env
```

## 🚀 Installation & Setup

### **Complete Setup**
```bash
# Run comprehensive installation
./install_complete.sh

# This handles:
# - Ollama installation
# - Model pulling
# - Environment setup
# - Dependency installation
```

### **Manual Setup**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull model
ollama pull llama3

# Start service
ollama serve &

# Test connection
ollama list
```

## 🔄 Workflow Integration

### **For Development Agents**
1. Always use `os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")`
2. Add proper URL parsing for local connections
3. Use `session.trust_env = False` for local requests
4. Validate environment variables before instantiation

### **For Troubleshooting Agents**
1. Check environment variables first
2. Verify service status
3. Test URL parsing
4. Check for proxy interference
5. Validate connection directly

### **For Deployment Agents**
1. Ensure Ollama is installed and running
2. Configure environment variables
3. Test local LLM connectivity
4. Monitor service health

## 📊 Success Criteria

### **Installation Success**
- [ ] Ollama installed and running
- [ ] Model pulled successfully
- [ ] Environment variables configured
- [ ] URL parsing working correctly
- [ ] Connection test passing

### **Runtime Success**
- [ ] Local LLM agent initializes without errors
- [ ] Connection test succeeds
- [ ] Model selection works
- [ ] Workflow generation functional

## 🚫 Prohibited Actions

### **Never Do These**
1. Hardcode localhost URLs without environment variable fallback
2. Use relative imports in entry point files
3. Skip environment variable validation
4. Ignore proxy settings for local connections
5. Deploy without Ollama service validation

### **Always Do These**
1. Use `os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")`
2. Add proper URL parsing and logging
3. Use `session.trust_env = False` for local connections
4. Validate service status before use
5. Document all configuration requirements

## 📚 Additional Resources

### **Documentation**
- `docs/DEPENDENCY_MANAGEMENT.md` - Complete dependency guide
- `.windsurf/DEPENDENCY_WORKFLOW.md` - Agent workflow guidelines
- `README.md` - Installation and setup instructions

### **Validation Tools**
```bash
# Run complete validation
python3 validate_enhanced_ai_os.py

# Test API server
python3 -c "from ai_os.api_server import app; print('API OK')"

# Test local LLM
python3 -c "from ai_os.agents.local_lm_agent import LocalLMAgent; print('Local LLM OK')"
```

---

**Last Updated**: 2024-01-01  
**Version**: 1.0.0  
**Status**: Production Ready
