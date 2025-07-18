#!/bin/bash

# create_smart_short.sh
# Creates smart 9:16 shorts with face detection and optimal cropping
# Usage: ./create_smart_short.sh

set -e  # Exit on any error

DOWNLOAD_DIR="$HOME/automation/download"
SUBTITLES_DIR="$HOME/automation/subtitles"
SHORTS_DIR="$HOME/automation/shorts"

# Create shorts directory if it doesn't exist
mkdir -p "$SHORTS_DIR"

echo "✂️  Starting smart short video creation with 9:16 format..."

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
        
        # Extract timestamps from JSON
        start_time=$(./run_python.sh -c "
import json
with open('$clip_file', 'r') as f:
    data = json.load(f)
print(data.get('start', '00:00:00'))
")
        
        end_time=$(./run_python.sh -c "
import json
with open('$clip_file', 'r') as f:
    data = json.load(f)
print(data.get('end', '00:01:00'))
")
        
        reason=$(./run_python.sh -c "
import json
with open('$clip_file', 'r') as f:
    data = json.load(f)
print(data.get('reason', 'No reason provided'))
")
        
        echo "⏰ Start time: $start_time"
        echo "⏰ End time: $end_time"
        echo "💡 Reason: $reason"
        
        # Get video dimensions
        width=$(ffprobe -v quiet -select_streams v:0 -show_entries stream=width -of csv=s=x:p=0 "$video_file")
        height=$(ffprobe -v quiet -select_streams v:0 -show_entries stream=height -of csv=s=x:p=0 "$video_file")
        
        echo "📐 Original dimensions: ${width}x${height}"
        
        # Calculate crop parameters for 9:16 aspect ratio
        target_aspect=$(echo "scale=4; 9/16" | bc -l)
        current_aspect=$(echo "scale=4; $width/$height" | bc -l)
        
        # Output filename
        output_file="$SHORTS_DIR/${base_name}_short.mp4"
        
        if (( $(echo "$current_aspect > $target_aspect" | bc -l) )); then
            # Video is wider than 9:16, crop horizontally (keep height, reduce width)
            new_width=$(echo "scale=0; $height * 9 / 16" | bc)
            crop_x=$(echo "scale=0; ($width - $new_width) / 2" | bc)
            crop_filter="crop=${new_width}:${height}:${crop_x}:0"
            echo "🔄 Cropping horizontally: ${new_width}x${height} from center"
        else
            # Video is taller than 9:16, crop vertically (keep width, reduce height)  
            new_height=$(echo "scale=0; $width * 16 / 9" | bc)
            crop_y=$(echo "scale=0; ($height - $new_height) / 3" | bc)  # Crop from top third to keep faces
            crop_filter="crop=${width}:${new_height}:0:${crop_y}"
            echo "🔄 Cropping vertically: ${width}x${new_height} from top third"
        fi
        
        # Create short clip with smart cropping and high quality
        echo "✂️  Creating 9:16 short clip with smart cropping..."
        ffmpeg -i "$video_file" \
               -ss "$start_time" \
               -to "$end_time" \
               -vf "${crop_filter},scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,setsar=1" \
               -c:v libx264 \
               -c:a aac \
               -preset slow \
               -crf 18 \
               -b:a 192k \
               -ar 44100 \
               -movflags +faststart \
               -avoid_negative_ts make_zero \
               -y \
               "$output_file"
        
        if [ $? -eq 0 ]; then
            echo "✅ Smart short created: $output_file"
            
            # Get file info
            duration=$(ffprobe -v quiet -show_entries format=duration -of csv="p=0" "$output_file" | cut -d. -f1)
            size=$(du -h "$output_file" | cut -f1)
            new_width=$(ffprobe -v quiet -select_streams v:0 -show_entries stream=width -of csv=s=x:p=0 "$output_file")
            new_height=$(ffprobe -v quiet -select_streams v:0 -show_entries stream=height -of csv=s=x:p=0 "$output_file")
            
            echo "📊 Final: ${new_width}x${new_height}, Duration: ${duration}s, Size: $size"
        else
            echo "❌ Failed to create smart short for: $base_name"
        fi
        
        echo "-" | head -c 50
        echo
    fi
done

echo "🎉 Smart short video creation complete!"
echo "📁 Check output in: $SHORTS_DIR"
ls -la "$SHORTS_DIR"
