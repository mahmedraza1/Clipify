#!/bin/bash

# create_short.sh
# Creates short video clips based on clip.json timestamps using ffmpeg
# Usage: ./create_short.sh

set -e  # Exit on any error

DOWNLOAD_DIR="$HOME/automation/download"
SUBTITLES_DIR="$HOME/automation/subtitles"
SHORTS_DIR="$HOME/automation/shorts"

# Create shorts directory if it doesn't exist
mkdir -p "$SHORTS_DIR"

echo "✂️  Starting short video creation..."

# Check if there are any clip.json files
if ! ls "$SUBTITLES_DIR"/*.clip.json 1> /dev/null 2>&1; then
    echo "❌ No clip.json files found in $SUBTITLES_DIR"
    echo "Please run suggest_clip.py first"
    exit 1
fi

# Process each clip.json file
for clip_file in "$SUBTITLES_DIR"/*.clip.json; do
    if [ -f "$clip_file" ]; then
        # Extract base filename without .clip.json extension
        base_name=$(basename "$clip_file" .clip.json)
        
        # Find corresponding video file
        video_file=""
        for ext in mp4 mkv avi mov; do
            if [ -f "$DOWNLOAD_DIR/$base_name.$ext" ]; then
                video_file="$DOWNLOAD_DIR/$base_name.$ext"
                break
            fi
        done
        
        if [ -z "$video_file" ]; then
            echo "❌ No video file found for: $base_name"
            continue
        fi
        
        echo "🎬 Processing: $base_name"
        echo "📁 Video file: $video_file"
        echo "📋 Clip file: $clip_file"
        
        # Extract timestamps from JSON using python directly
        start_time=$(python3 -c "
import json
with open('$clip_file', 'r') as f:
    data = json.load(f)
print(data.get('start', '00:00:00'))
")
        
        end_time=$(python3 -c "
import json
with open('$clip_file', 'r') as f:
    data = json.load(f)
print(data.get('end', '00:01:00'))
")
        
        reason=$(python3 -c "
import json
with open('$clip_file', 'r') as f:
    data = json.load(f)
print(data.get('reason', 'No reason provided'))
")
        
        echo "⏰ Start time: $start_time"
        echo "⏰ End time: $end_time"
        echo "💡 Reason: $reason"
        
        # Output filename
        output_file="$SHORTS_DIR/${base_name}_short.mp4"
        
        # Create short clip using ffmpeg with 9:16 aspect ratio and smart cropping
        echo "✂️  Creating HIGH QUALITY vertical short clip (9:16) with audio and smart crop..."
        
        # Get CPU core count and use 50%
        cpu_cores=$(nproc)
        half_cores=$((cpu_cores / 2))
        if [ $half_cores -lt 1 ]; then
            half_cores=1
        fi
        
        # Smart crop filter: Better approach for 16:9 to 9:16 conversion
        # First scale to 1920 height maintaining aspect, then center crop with slight upward bias
        smart_crop="scale=-1:1920:force_original_aspect_ratio=increase,crop=1080:1920:iw/2-540:ih/6"
        
        # Detect available hardware acceleration
        if ffmpeg -f lavfi -i testsrc=duration=1:size=320x240:rate=1 -c:v h264_nvenc -f null - 2>/dev/null; then
            echo "🚀 Using NVIDIA GPU acceleration (${half_cores} CPU threads)"
            ffmpeg -i "$video_file" \
                   -ss "$start_time" \
                   -to "$end_time" \
                   -vf "$smart_crop" \
                   -c:v h264_nvenc \
                   -preset hq \
                   -rc vbr \
                   -cq 16 \
                   -b:v 15M \
                   -maxrate 20M \
                   -bufsize 30M \
                   -c:a aac \
                   -b:a 320k \
                   -ar 48000 \
                   -threads $half_cores \
                   -avoid_negative_ts make_zero \
                   -y \
                   "$output_file"
        elif ffmpeg -f lavfi -i testsrc=duration=1:size=320x240:rate=1 -c:v h264_vaapi -f null - 2>/dev/null; then
            echo "🚀 Using Intel/AMD GPU acceleration (${half_cores} CPU threads)"
            ffmpeg -i "$video_file" \
                   -ss "$start_time" \
                   -to "$end_time" \
                   -vf "$smart_crop" \
                   -c:v h264_vaapi \
                   -preset slow \
                   -crf 16 \
                   -b:v 15M \
                   -maxrate 20M \
                   -bufsize 30M \
                   -c:a aac \
                   -b:a 320k \
                   -ar 48000 \
                   -threads $half_cores \
                   -avoid_negative_ts make_zero \
                   -y \
                   "$output_file"
        else
            echo "💻 Using HIGH QUALITY CPU encoding (${half_cores} threads - 50% CPU limit)"
            ffmpeg -i "$video_file" \
                   -ss "$start_time" \
                   -to "$end_time" \
                   -vf "$smart_crop" \
                   -c:v libx264 \
                   -preset slower \
                   -crf 14 \
                   -b:v 15M \
                   -maxrate 20M \
                   -bufsize 30M \
                   -c:a aac \
                   -b:a 320k \
                   -ar 48000 \
                   -threads $half_cores \
                   -avoid_negative_ts make_zero \
                   -y \
                   "$output_file"
        fi
        
        if [ $? -eq 0 ]; then
            echo "✅ Short created: $output_file"
            
            # Get file info
            duration=$(ffprobe -v quiet -show_entries format=duration -of csv="p=0" "$output_file" | cut -d. -f1)
            size=$(du -h "$output_file" | cut -f1)
            
            echo "📊 Duration: ${duration}s, Size: $size"
        else
            echo "❌ Failed to create short for: $base_name"
        fi
        
        echo "-" | head -c 50
        echo
    fi
done

echo "🎉 Short video creation complete!"
echo "📁 Check output in: $SHORTS_DIR"
ls -la "$SHORTS_DIR"
