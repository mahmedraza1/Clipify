#!/bin/bash

# download_video.sh
# Downloads YouTube video using yt-dlp to ~/automation/download/
# Usage: ./download_video.sh <YouTube_URL>

set -e  # Exit on any error

# Check if URL is provided
if [ $# -eq 0 ]; then
    echo "Error: Please provide a YouTube URL"
    echo "Usage: $0 <YouTube_URL>"
    exit 1
fi

URL="$1"
DOWNLOAD_DIR="$HOME/automation/download"

# Create download directory if it doesn't exist
mkdir -p "$DOWNLOAD_DIR"

echo "📥 Downloading video from: $URL"
echo "📁 Saving to: $DOWNLOAD_DIR"

# Download video with best quality (prefer 1080p) and subtitles
cd "$DOWNLOAD_DIR"

# First, try to download with automatic subtitles (YouTube's own captions)
echo "🎯 Attempting to download YouTube subtitles..."
yt-dlp --write-auto-subs --sub-langs "en,en-US,en-GB" --sub-format "srt" --skip-download -o "%(title)s.%(ext)s" "$URL" || echo "⚠️  No auto-generated subtitles found"

# Then try to download manual subtitles (human-created)
echo "🎯 Attempting to download manual subtitles..."
yt-dlp --write-subs --sub-langs "en,en-US,en-GB" --sub-format "srt" --skip-download -o "%(title)s.%(ext)s" "$URL" || echo "⚠️  No manual subtitles found"

# Download the video
echo "🎥 Downloading video..."
yt-dlp -f "best[height<=1080][ext=mp4]/best[ext=mp4]" -o "%(title)s.%(ext)s" "$URL"

if [ $? -eq 0 ]; then
    echo "✅ Video downloaded successfully to $DOWNLOAD_DIR"
    
    # Process any downloaded subtitle files
    echo "📝 Processing downloaded subtitles..."
    SUBTITLES_DIR="$HOME/automation/subtitles"
    mkdir -p "$SUBTITLES_DIR"
    
    # Find downloaded subtitle files and move them
    for srt_file in "$DOWNLOAD_DIR"/*.srt; do
        if [ -f "$srt_file" ]; then
            # Extract video title from filename
            base_name=$(basename "$srt_file" | sed 's/\.[a-z][a-z]*\.srt$//' | sed 's/\.srt$//')
            new_name="$base_name.srt"
            mv "$srt_file" "$SUBTITLES_DIR/$new_name"
            echo "✅ Moved subtitles: $new_name"
        fi
    done
    
    # List the downloaded file
    echo "📄 Downloaded file:"
    ls -la "$DOWNLOAD_DIR"/*.mp4 | tail -1
    
    # List any subtitle files
    if ls "$SUBTITLES_DIR"/*.srt 1> /dev/null 2>&1; then
        echo "📝 Subtitle files:"
        ls -la "$SUBTITLES_DIR"/*.srt | tail -1
    fi
else
    echo "❌ Error downloading video"
    exit 1
fi
