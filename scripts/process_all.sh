#!/bin/bash

# process_all.sh
# Complete pipeline to process YouTube video into short with interactive subtitles
# Usage: ./process_all.sh <YouTube_URL>

set -e  # Exit on any error

# Configuration
SCRIPTS_DIR="$HOME/automation/scripts"
DOWNLOAD_DIR="$HOME/automation/download"
SUBTITLES_DIR="$HOME/automation/subtitles"
SHORTS_DIR="$HOME/automation/shorts"
VENV_DIR="$HOME/automation/venv"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Activate virtual environment if it exists
if [ -d "$VENV_DIR" ]; then
    log "🐍 Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
fi

# Check if URL is provided
if [ $# -eq 0 ]; then
    error "Please provide a YouTube URL"
    echo "Usage: $0 <YouTube_URL>"
    exit 1
fi

URL="$1"

log "🚀 Starting complete video processing pipeline"
log "📺 YouTube URL: $URL"

# Create all necessary directories
mkdir -p "$DOWNLOAD_DIR" "$SUBTITLES_DIR" "$SHORTS_DIR"

# Step 1: Download video
log "📥 Step 1: Downloading video..."
cd "$SCRIPTS_DIR"
if bash download_video.sh "$URL"; then
    success "Video downloaded successfully"
else
    error "Failed to download video"
    exit 1
fi

# Step 2: Transcribe video
log "🎤 Step 2: Transcribing video..."
if bash transcribe_video.sh; then
    success "Video transcribed successfully"
else
    error "Failed to transcribe video"
    exit 1
fi

# Step 3: Romanize subtitles (if needed)
log "🌐 Step 3: Romanizing subtitles..."
if ./run_python.sh romanize_subtitles.py; then
    success "Subtitles romanized successfully"
else
    warning "Romanization failed, continuing with original subtitles"
fi

# Step 4: Suggest clip
log "🎯 Step 4: Analyzing transcript for viral clips..."
if ./run_python.sh suggest_clip.py; then
    success "Clip suggestions generated successfully"
else
    error "Failed to generate clip suggestions"
    exit 1
fi

# Step 5: Create short
log "✂️  Step 5: Creating smart short video clips (9:16 format)..."
if bash create_smart_short.sh; then
    success "Smart short videos created successfully"
else
    error "Failed to create short videos"
    exit 1
fi

# Step 6: Add interactive subtitles
log "🎭 Step 6: Adding interactive subtitles..."
if ./run_python.sh create_interactive_subtitles.py; then
    success "Interactive subtitles added successfully"
else
    warning "Failed to add interactive subtitles, short videos available without subtitles"
fi

# Final summary
log "📊 Processing complete! Summary:"
echo "----------------------------------------"

# Count files in each directory
download_count=$(ls -1 "$DOWNLOAD_DIR"/*.mp4 2>/dev/null | wc -l || echo "0")
subtitle_count=$(ls -1 "$SUBTITLES_DIR"/*.txt 2>/dev/null | wc -l || echo "0")
srt_count=$(ls -1 "$SUBTITLES_DIR"/*.srt 2>/dev/null | wc -l || echo "0")
clip_count=$(ls -1 "$SUBTITLES_DIR"/*.clip.json 2>/dev/null | wc -l || echo "0")
short_count=$(ls -1 "$SHORTS_DIR"/*_short.mp4 2>/dev/null | wc -l || echo "0")
final_count=$(ls -1 "$SHORTS_DIR"/*_with_subtitles.mp4 2>/dev/null | wc -l || echo "0")

echo "📥 Downloaded videos: $download_count"
echo "📝 Text transcripts: $subtitle_count"
echo "🎬 SRT subtitles: $srt_count"
echo "🎯 Clip suggestions: $clip_count"
echo "✂️  Short clips: $short_count"
echo "🎭 Final videos with subtitles: $final_count"

echo "----------------------------------------"
echo "📁 Check these directories for output:"
echo "   Downloads: $DOWNLOAD_DIR"
echo "   Subtitles: $SUBTITLES_DIR"
echo "   Shorts: $SHORTS_DIR"

if [ "$final_count" -gt 0 ]; then
    success "🎉 Pipeline completed successfully!"
    log "📱 Your short videos with interactive subtitles are ready for social media!"
else
    warning "⚠️  Pipeline completed with some issues. Check the logs above."
fi
