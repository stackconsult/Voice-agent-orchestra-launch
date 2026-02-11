#!/bin/bash

# Enhanced AI-OS Voice Activator Installation Script
# Installs all dependencies for voice-activated workflow automation

set -e  # Exit on any error

echo "🎙️ Enhanced AI-OS Voice Activator Installation"
echo "=============================================="

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f\"{sys.version_info.major}.{sys.version_info.minor}\")")
REQUIRED_PYTHON="3.9"

if [ "$PYTHON_VERSION" -lt "$REQUIRED_PYTHON" ]; then
    echo "❌ Error: Python $REQUIRED_PYTHON or higher is required. Found: $PYTHON_VERSION"
    echo "Please install Python 3.9+ and try again."
    exit 1
fi

echo "✅ Python version check passed: $PYTHON_VERSION"

# Check system
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ Error: Voice Activator is designed for macOS systems"
    exit 1
fi

echo "✅ macOS system check passed"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Install API server dependencies
echo "📦 Installing API server dependencies..."
pip install -r requirements-api.txt

# Install system dependencies
echo "🔧 Installing system dependencies..."

# Install portaudio for sounddevice
if ! brew list portaudio &> /dev/null; then
    echo "📦 Installing portaudio..."
    brew install portaudio
else
    echo "✅ portaudio already installed"
fi

# Install ffmpeg for audio processing
if ! command -v ffmpeg &> /dev/null; then
    echo "📦 Installing ffmpeg..."
    brew install ffmpeg
else
    echo "✅ ffmpeg already installed"
fi

# Check/install Ollama for local LLM
if ! command -v ollama &> /dev/null; then
    echo "📦 Installing Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
else
    echo "✅ Ollama already installed"
fi

# Start Ollama service
if pgrep -x "ollama" > /dev/null; then
    echo "✅ Ollama already running"
else
    echo "🚀 Starting Ollama..."
    ollama serve &
    sleep 5
fi

# Pull recommended model
echo "📥 Pulling recommended LLM model..."
ollama pull llama3.2:3b || ollama pull llama2 || echo "⚠️ Please manually pull a model: ollama pull llama3.2:3b"

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p ~/.aios/{logs,snapshots,skills,tmp}
mkdir -p skills
mkdir -p tmp

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your API keys"
else
    echo "✅ .env file already exists"
fi

# Test voice components
echo "🧪 Testing voice components..."

python3 -c "
try:
    import sounddevice
    print('✅ sounddevice imported successfully')
except ImportError as e:
    print(f'❌ sounddevice import failed: {e}')

try:
    import soundfile
    print('✅ soundfile imported successfully')
except ImportError as e:
    print(f'❌ soundfile import failed: {e}')

try:
    from faster_whisper import WhisperModel
    print('✅ faster_whisper imported successfully')
except ImportError as e:
    print(f'❌ faster_whisper import failed: {e}')

try:
    from pynput import keyboard
    print('✅ pynput imported successfully')
except ImportError as e:
    print(f'❌ pynput import failed: {e}')

try:
    import PyQt6
    print('✅ PyQt6 imported successfully')
except ImportError as e:
    print(f'❌ PyQt6 import failed: {e}')
"

echo ""
echo "🎉 Voice Activator installation completed!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env with your API keys (if using cloud models)"
echo "2. Test voice system: python -m ai_os.main --voice"
echo "3. Press Cmd+Shift+V to activate voice recording"
echo ""
echo "🎙️ Voice Commands to try:"
echo "  'Create a skill to organize my downloads folder'"
echo "  'List all PDF files in my downloads folder'"
echo ""
echo "🚀 Voice Activator is ready!"
