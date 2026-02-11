#!/bin/bash

# Enhanced AI-OS Complete Installation Script
# Handles all dependencies, environment setup, and system configuration

set -e  # Exit on any error

echo "🚀 Enhanced AI-OS Complete Installation"
echo "======================================"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check system requirements
check_system() {
    echo "🔍 Checking system requirements..."
    
    # Check Python version
    PYTHON_VERSION=$(python3 -c "import sys; print(f\"{sys.version_info.major}.{sys.version_info.minor}\")")
    REQUIRED_PYTHON="3.9"
    
    if [[ "$PYTHON_VERSION" < "$REQUIRED_PYTHON" ]]; then
        print_error "Python $REQUIRED_PYTHON or higher is required. Found: $PYTHON_VERSION"
        exit 1
    fi
    print_success "Python version check passed: $PYTHON_VERSION"
    
    # Check system
    if [[ "$OSTYPE" != "Darwin"* ]]; then
        print_error "Enhanced AI-OS is designed for macOS systems"
        exit 1
    fi
    print_success "macOS system check passed"
    
    # Check for Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is required but not installed"
        print_info "Please install Node.js from https://nodejs.org/"
        exit 1
    fi
    NODE_VERSION=$(node --version)
    print_success "Node.js version: $NODE_VERSION"
    
    # Check for npm
    if ! command -v npm &> /dev/null; then
        print_error "npm is required but not installed"
        exit 1
    fi
    NPM_VERSION=$(npm --version)
    print_success "npm version: $NPM_VERSION"
}

# Setup Python environment
setup_python_env() {
    echo "🐍 Setting up Python environment..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_info "Creating Python virtual environment..."
        python3 -m venv venv
    else
        print_info "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    print_info "Upgrading pip..."
    pip install --upgrade pip
    
    # Install Python dependencies
    print_info "Installing Python dependencies..."
    if pip install -r requirements.txt; then
        print_success "Python dependencies installed"
    else
        print_error "Failed to install Python dependencies"
        exit 1
    fi
}

# Install system dependencies
install_system_deps() {
    echo "🔧 Installing system dependencies..."
    
    # Check for Homebrew
    if ! command -v brew &> /dev/null; then
        print_warning "Homebrew not found. Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    else
        print_success "Homebrew already installed"
    fi
    
    # Install FFmpeg
    if ! command -v ffmpeg &> /dev/null; then
        print_info "Installing FFmpeg..."
        brew install ffmpeg
    else
        print_success "FFmpeg already installed"
    fi
    
    # Install Ollama
    if ! command -v ollama &> /dev/null; then
        print_info "Installing Ollama..."
        curl -fsSL https://ollama.ai/install.sh | sh
    else
        print_success "Ollama already installed"
    fi
    
    # Install whisper.cpp
    if [ ! -f "/usr/local/bin/whisper.cpp" ]; then
        print_info "Installing whisper.cpp..."
        WHISPER_DIR="$HOME/.local/bin"
        mkdir -p "$WHISPER_DIR"
        curl -L https://github.com/ggerganov/whisper.cpp/releases/download/latest/download/whisper.cpp-mac.tar.gz | tar -xzf -C "$WHISPER_DIR"
        cd "$WHISPER_DIR"
        make whisper.cpp
        sudo mv whisper.cpp /usr/local/bin/whisper.cpp
        rm -rf whisper.cpp-mac.tar.gz
        print_success "whisper.cpp installed"
    else
        print_success "whisper.cpp already installed"
    fi
}

# Setup Node.js environment
setup_node_env() {
    echo "📦 Setting up Node.js environment..."
    
    # Navigate to UI directory
    cd ui
    
    # Install Node.js dependencies
    print_info "Installing Node.js dependencies..."
    if npm install; then
        print_success "Node.js dependencies installed"
    else
        print_error "Failed to install Node.js dependencies"
        exit 1
    fi
    
    # Install Electron globally if needed
    if ! command -v electron &> /dev/null; then
        print_info "Installing Electron globally..."
        npm install -g electron
    else
        print_success "Electron already installed"
    fi
    
    # Return to project root
    cd ..
}

# Setup environment configuration
setup_env_config() {
    echo "⚙️  Setting up environment configuration..."
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        print_info "Creating .env file from template..."
        cp .env.example .env
        print_success ".env file created"
        print_warning "Please edit .env file with your API keys and configuration"
    else
        print_info ".env file already exists"
    fi
}

# Create necessary directories
create_directories() {
    echo "📁 Creating necessary directories..."
    
    # AI-OS directories
    mkdir -p ~/.aios/{logs,snapshots,skills,tmp}
    print_success "AI-OS directories created"
    
    # Project directories
    mkdir -p skills
    mkdir -p templates
    mkdir -p workspace
    print_success "Project directories created"
}

# Pull Ollama models
setup_ollama_models() {
    echo "🤖 Setting up Ollama models..."
    
    # Check if Ollama is running
    if ! ollama list &> /dev/null; then
        print_info "Starting Ollama service..."
        ollama serve &
        sleep 5  # Wait for service to start
    fi
    
    # Pull default model
    print_info "Pulling Llama3 model (this may take a while)..."
    if ollama pull llama3; then
        print_success "Llama3 model installed"
    else
        print_warning "Failed to pull Llama3 model. You can run 'ollama pull llama3' manually later."
    fi
}

# Test installation
test_installation() {
    echo "🧪 Testing installation..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Test Python imports
    print_info "Testing Python imports..."
    python3 -c "
import sys
try:
    import anthropic
    import openai
    import fastapi
    import sounddevice
    import yaml
    print('✅ All critical imports successful')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"
    
    # Test validation script
    print_info "Running validation script..."
    if python3 validate_enhanced_ai_os.py; then
        print_success "Validation script passed"
    else
        print_warning "Validation script had issues (may be normal without API keys)"
    fi
    
    # Test API server
    print_info "Testing API server startup..."
    timeout 10s python3 ai_os/api_server.py &
    API_PID=$!
    sleep 3
    
    if ps -p $API_PID > /dev/null; then
        print_success "API server starts successfully"
        kill $API_PID 2>/dev/null
    else
        print_warning "API server may have issues"
    fi
}

# Create startup scripts
create_startup_scripts() {
    echo "📜 Creating startup scripts..."
    
    # Create API server startup script
    cat > start_api_server.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python3 ai_os/api_server.py
EOF
    chmod +x start_api_server.sh
    
    # Create UI startup script
    cat > start_ui.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")/ui"
npm start
EOF
    chmod +x start_ui.sh
    
    # Create CLI startup script
    cat > start_cli.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python3 ai_os/main.py --cli
EOF
    chmod +x start_cli.sh
    
    print_success "Startup scripts created"
}

# Main installation flow
main() {
    echo "Starting Enhanced AI-OS complete installation..."
    
    check_system
    setup_python_env
    install_system_deps
    setup_node_env
    setup_env_config
    create_directories
    setup_ollama_models
    test_installation
    create_startup_scripts
    
    echo ""
    echo "🎉 Enhanced AI-OS installation completed successfully!"
    echo ""
    echo "📋 Quick Start:"
    echo "1. Edit .env file with your API keys (optional)"
    echo "2. Start API server: ./start_api_server.sh"
    echo "3. Start UI: ./start_ui.sh"
    echo "4. Or use CLI: ./start_cli.sh"
    echo ""
    echo "📚 Documentation:"
    echo "- README.md for overview"
    echo "- docs/ directory for detailed guides"
    echo "- Visit http://localhost:8000/docs for API documentation"
    echo ""
    echo "🔧 Troubleshooting:"
    echo "- If sounddevice fails: brew install portaudio"
    echo "- If Electron fails: npm install -g electron"
    echo "- If Ollama fails: ollama serve && ollama pull llama3"
    echo ""
    print_success "Enhanced AI-OS is ready! 🚀"
}

# Run main function
main "$@"
