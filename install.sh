#!/bin/bash

# AI-OS Installation Script
# One-command setup for the voice-driven workflow automation system

set -e  # Exit on any error

echo "🚀 AI-OS Installation Script"
echo "===================="

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
if [[ "$OSTYPE" != "Darwin"* ]]; then
    echo "❌ Error: AI-OS is designed for macOS systems"
    exit 1
fi

echo "✅ macOS system check passed"

# Create virtual environment
echo "📦 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Install FFmpeg (for audio recording)
if ! command -v ffmpeg &> /dev/null; then
    echo "📦 Installing FFmpeg..."
    if command -v brew &> /dev/null; then
        brew install ffmpeg
    else
        echo "❌ Please install FFmpeg manually:"
        echo "  - With Homebrew: brew install ffmpeg"
        echo "  - Download from: https://ffmpeg.org/download.html"
        exit 1
    fi
else
    echo "✅ FFmpeg already installed"
fi

# Install whisper.cpp (for offline transcription)
if [ ! -f "/usr/local/bin/whisper.cpp" ]; then
    echo "📦 Installing whisper.cpp..."
    WHISPER_DIR="$HOME/.local/bin"
    mkdir -p "$WHISPER_DIR"
    curl -L https://github.com/ggerganov/whisper.cpp/releases/download/latest/download/whisper.cpp-mac.tar.gz | tar -xzf -C "$WHISPER_DIR"
    cd "$WHISPER_DIR"
    make whisper.cpp
    sudo mv whisper.cpp /usr/local/bin/whisper.cpp
    rm -rf whisper.cpp-mac.tar.gz
    echo "✅ whisper.cpp installed to /usr/local/bin/whisper.cpp"
else
    echo "✅ whisper.cpp already installed"
fi

# Create AI-OS directories
echo "📁 Creating AI-OS directories..."
mkdir -p ~/.aios/{logs,snapshots,skills,tmp}

# Create skills directory
mkdir -p skills

# Create templates directory
mkdir -p templates

# Install PyObjC for AppleScript support
echo "📦 Installing PyObjC for AppleScript support..."
pip install PyObjC

echo "🎉 Installation completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Copy .env.example to .env and configure your API keys"
echo "2. Run 'python -m ai_os.main --init' to initialize the system"
echo "3. Run 'python -m ai_os.main --ppt' to start the voice interface"
echo ""
echo "📚 For help: python -m ai_os.main --help"
echo "📚 For docs: see docs/ directory"

echo "🎯 AI-OS is ready!"
