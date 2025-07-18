#!/bin/bash

# transcribe_video.sh
# Transcribes all MP4 files in ~/automation/download using whisper.cpp
# Outputs .srt and .txt files to ~/automation/subtitles
# Usage: ./transcribe_video.sh

set -e  # Exit on any error

DOWNLOAD_DIR="$HOME/automation/download"
SUBTITLES_DIR="$HOME/automation/subtitles"
WHISPER_DIR="$HOME/whisper.cpp"

# Find the best available model (prefer larger models for better accuracy)
if [ -f "$WHISPER_DIR/models/ggml-medium.bin" ]; then
    MODEL_PATH="$WHISPER_DIR/models/ggml-medium.bin"
    echo "🎯 Using medium model for better accuracy"
elif [ -f "$WHISPER_DIR/models/ggml-base.en.bin" ]; then
    MODEL_PATH="$WHISPER_DIR/models/ggml-base.en.bin"
    echo "🎯 Using base.en model"
elif [ -f "$WHISPER_DIR/models/ggml-base.bin" ]; then
    MODEL_PATH="$WHISPER_DIR/models/ggml-base.bin"
    echo "🎯 Using base model"
else
    echo "❌ No whisper models found!"
    echo "Available models in $WHISPER_DIR/models/:"
    ls -la "$WHISPER_DIR/models/"*.bin 2>/dev/null || echo "No .bin files found"
    exit 1
fi

# Create subtitles directory if it doesn't exist
mkdir -p "$SUBTITLES_DIR"

# Check if whisper.cpp exists
if [ ! -d "$WHISPER_DIR" ]; then
    echo "❌ Error: whisper.cpp not found at $WHISPER_DIR"
    echo "Please clone and compile whisper.cpp first:"
    echo "git clone https://github.com/ggerganov/whisper.cpp.git ~/whisper.cpp"
    echo "cd ~/whisper.cpp && make"
    exit 1
fi

# Check if there are any MP4 files to process
if ! ls "$DOWNLOAD_DIR"/*.mp4 1> /dev/null 2>&1; then
    echo "❌ No MP4 files found in $DOWNLOAD_DIR"
    exit 1
fi

echo "🎤 Starting transcription of videos..."

# Check for existing YouTube subtitles first
echo "🔍 Checking for existing YouTube subtitles..."
YOUTUBE_SUBS_FOUND=false

for video_file in "$DOWNLOAD_DIR"/*.mp4; do
    video_basename=$(basename "$video_file" .mp4)
    existing_srt="$SUBTITLES_DIR/$video_basename.srt"
    
    if [ -f "$existing_srt" ]; then
        echo "✅ Found existing subtitles for: $video_basename"
        echo "📝 Subtitle file: $existing_srt"
        YOUTUBE_SUBS_FOUND=true
    fi
done

if [ "$YOUTUBE_SUBS_FOUND" = true ]; then
    echo "🎉 Using existing YouTube subtitles - skipping whisper transcription"
    echo "📁 Subtitles ready in: $SUBTITLES_DIR"
    ls -la "$SUBTITLES_DIR"
    exit 0
fi

echo "⚠️  No YouTube subtitles found - proceeding with whisper transcription..."

# Process each MP4 file
for video_file in "$DOWNLOAD_DIR"/*.mp4; do
    if [ -f "$video_file" ]; then
        filename=$(basename "$video_file" .mp4)
        echo "🎬 Processing: $filename"
        
        # Convert MP4 to WAV for whisper.cpp (it doesn't handle MP4 well)
        wav_file="/tmp/${filename}.wav"
        echo "🎵 Converting audio to WAV format..."
        ffmpeg -i "$video_file" -ar 16000 -ac 1 -f wav "$wav_file" -y -loglevel quiet
        
        if [ ! -f "$wav_file" ]; then
            echo "❌ Failed to convert audio for: $filename"
            continue
        fi
        
        # Get CPU core count and use 50% for optimal performance without overloading
        cpu_cores=$(nproc)
        half_cores=$((cpu_cores / 2))
        if [ $half_cores -lt 1 ]; then
            half_cores=1
        fi
        echo "💻 Using $half_cores threads (50% of $cpu_cores CPU cores)"
        
        # Run whisper.cpp transcription on WAV file with word-level timestamps
        cd "$WHISPER_DIR"
        ./build/bin/whisper-cli -m "$MODEL_PATH" -f "$wav_file" --output-txt --output-srt --output-file "$SUBTITLES_DIR/$filename" --print-progress --threads $half_cores --word-thold 0.01
        
        # Clean up temporary WAV file
        rm -f "$wav_file"
        
        if [ $? -eq 0 ]; then
            echo "✅ Transcribed: $filename"
        else
            echo "❌ Failed to transcribe: $filename"
        fi
    fi
done

echo "📝 Transcription complete. Files saved to: $SUBTITLES_DIR"
ls -la "$SUBTITLES_DIR"
