#!/bin/bash

# setup.sh - Install all dependencies for the automation system
# Usage: ./setup.sh

set -e

echo "🔧 Setting up automation system dependencies..."

# Update package database
echo "📦 Updating package database..."
sudo pacman -Sy

# Install system dependencies
echo "🛠️  Installing system dependencies..."
sudo pacman -S --needed --noconfirm \
    python \
    python-pip \
    ffmpeg \
    yt-dlp \
    git \
    make \
    gcc \
    bc

# Install Python dependencies
echo "🐍 Installing Python dependencies..."

# Try to install via pacman first (Arch way)
echo "📦 Installing Python packages via pacman..."
sudo pacman -S --needed --noconfirm \
    python-requests \
    python-setuptools

# For packages not available in Arch repos, create a virtual environment
echo "🔧 Creating virtual environment for remaining packages..."
python -m venv ~/automation/venv
source ~/automation/venv/bin/activate

echo "📥 Installing remaining packages in virtual environment..."
pip install moviepy langdetect

echo "✅ Python dependencies installed!"
echo "ℹ️  Note: When running scripts, use the virtual environment:"
echo "   source ~/automation/venv/bin/activate"

# Check if whisper.cpp exists, if not provide instructions
if [ ! -d "$HOME/whisper.cpp" ]; then
    echo "⚠️  whisper.cpp not found!"
    echo "📥 Cloning and building whisper.cpp..."
    
    cd "$HOME"
    git clone https://github.com/ggerganov/whisper.cpp.git
    cd whisper.cpp
    make
    
    # Ensure build directory exists and contains main executable
    if [ ! -f "./build/bin/main" ]; then
        echo "⚠️  Main executable not found in build/bin/, trying alternative build..."
        mkdir -p build && cd build
        cmake ..
        make -j4
        cd ..
    fi
    
    echo "⬇️  Downloading base model..."
    bash ./models/download-ggml-model.sh base.en
    
    echo "✅ whisper.cpp setup complete!"
else
    echo "✅ whisper.cpp already exists at $HOME/whisper.cpp"
    
    # Check if base model exists
    if [ -f "$HOME/whisper.cpp/models/ggml-base.en.bin" ]; then
        echo "✅ Base model already exists"
    else
        echo "⬇️  Downloading base model..."
        cd "$HOME/whisper.cpp"
        bash ./models/download-ggml-model.sh base.en
    fi
fi

# Make all scripts executable
echo "🔑 Making scripts executable..."
chmod +x ~/automation/scripts/*.sh ~/automation/scripts/*.py

echo "🎉 Setup complete!"
echo ""
echo "⚠️  IMPORTANT: For Arch Linux, activate the virtual environment before running Python scripts:"
echo "   source ~/automation/venv/bin/activate"
echo ""
echo "📋 Usage:"
echo "   source ~/automation/venv/bin/activate     # Activate virtual environment"
echo "   ./scripts/process_all.sh <YouTube_URL>    # Process complete video"
echo "   ./scripts/download_video.sh <URL>         # Download only"
echo "   ./scripts/transcribe_video.sh             # Transcribe only"
echo "   ./scripts/run_python.sh romanize_subtitles.py    # Romanize only"
echo "   ./scripts/run_python.sh suggest_clip.py          # Suggest clips only"
echo "   ./scripts/create_short.sh                 # Create shorts only"
echo "   ./scripts/run_python.sh create_interactive_subtitles.py  # Add subtitles only"
echo ""
echo "🔧 Dependencies installed:"
echo "   ✅ yt-dlp (YouTube downloader)"
echo "   ✅ ffmpeg (video processing)"
echo "   ✅ whisper.cpp (speech recognition)"
echo "   ✅ Python packages (requests, moviepy, langdetect) in virtual environment"
