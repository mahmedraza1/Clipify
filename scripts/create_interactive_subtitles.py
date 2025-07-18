#!/usr/bin/env python3

"""
create_interactive_subtitles.py
Creates interactive subtitles overlay for short videos using MoviePy
Usage: python3 create_interactive_subtitles.py
"""

import os
import sys
import json
import re
from pathlib import Path
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
# Note: moviepy.config.check_for_packages doesn't exist in v1.0.3

# Configuration
SHORTS_DIR = os.path.expanduser("~/automation/shorts")
SUBTITLES_DIR = os.path.expanduser("~/automation/subtitles")

def parse_srt_file(srt_path):
    """Parse SRT file and extract subtitle entries with timestamps"""
    subtitles = []
    
    try:
        with open(srt_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        # Split by double newlines to get individual subtitle blocks
        blocks = re.split(r'\n\s*\n', content)
        
        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) >= 3:
                # Parse timestamp line (format: 00:00:01,000 --> 00:00:04,000)
                timestamp_line = lines[1]
                match = re.match(r'(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})', timestamp_line)
                
                if match:
                    start_time = match.group(1)
                    end_time = match.group(2)
                    
                    # Join all remaining lines as subtitle text
                    text = ' '.join(lines[2:]).strip()
                    
                    # Convert timestamp to seconds
                    start_seconds = timestamp_to_seconds(start_time)
                    end_seconds = timestamp_to_seconds(end_time)
                    
                    subtitles.append({
                        'start': start_seconds,
                        'end': end_seconds,
                        'text': text
                    })
        
        return subtitles
        
    except Exception as e:
        print(f"❌ Error parsing SRT file {srt_path}: {e}")
        return []

def timestamp_to_seconds(timestamp):
    """Convert SRT timestamp (HH:MM:SS,mmm) to seconds"""
    time_part, ms_part = timestamp.split(',')
    h, m, s = map(int, time_part.split(':'))
    ms = int(ms_part)
    
    return h * 3600 + m * 60 + s + ms / 1000.0

def create_word_highlighting_clips(text, start_time, end_time, video_size):
    """Create interactive word-by-word highlighting subtitle clips"""
    duration = end_time - start_time
    words = text.split()
    
    if not words:
        return []
    
    # Calculate time per word with slight overlap for smooth transitions
    time_per_word = duration / len(words)
    
    clips = []
    font_size = min(100, video_size[0] // 10)  # Larger font for better visibility
    y_position = video_size[1] * 0.75  # Match background subtitle position
    
    for i, word in enumerate(words):
        word_start = start_time + (i * time_per_word)
        word_end = min(start_time + ((i + 1) * time_per_word), end_time)
        word_duration = word_end - word_start
        
        if word_duration <= 0:
            continue
        
        # Create highlighted version (current word being spoken)
        highlighted_clip = TextClip(word,
                                  fontsize=font_size,
                                  color='#FFD700',  # Gold color for highlight
                                  stroke_color='black',
                                  stroke_width=4,
                                  font='Liberation-Sans-Bold')
        
        # Position to match background text
        highlighted_clip = highlighted_clip.set_position(('center', y_position)).set_duration(word_duration).set_start(word_start)
        clips.append(highlighted_clip)
    
    return clips

def create_subtitle_clip(text, start_time, end_time, video_size):
    """Create a subtitle text clip optimized for 9:16 vertical videos with better formatting"""
    duration = end_time - start_time
    words = text.split()
    
    # Limit to 4-5 words maximum for better readability
    max_words = 5
    if len(words) > max_words:
        # Split into multiple shorter clips
        clips = []
        for i in range(0, len(words), max_words):
            chunk_words = words[i:i + max_words]
            chunk_text = ' '.join(chunk_words)
            
            # Calculate timing for this chunk
            chunk_duration = duration * len(chunk_words) / len(words)
            chunk_start = start_time + (duration * i / len(words))
            
            formatted_text = chunk_text
            font_size = min(70, video_size[0] // 12)
            
            txt_clip = TextClip(formatted_text,
                               fontsize=font_size,
                               color='white',
                               stroke_color='black',
                               stroke_width=3,
                               font='Liberation-Sans-Bold',
                               method='caption',
                               size=(video_size[0] * 0.9, None))
            
            y_position = video_size[1] * 0.82  # Slightly lower
            txt_clip = txt_clip.set_position(('center', y_position)).set_duration(chunk_duration).set_start(chunk_start)
            clips.append(txt_clip)
        
        return clips
    else:
        # Single clip for short text
        formatted_text = ' '.join(words)
        font_size = min(70, video_size[0] // 12)
        
        txt_clip = TextClip(formatted_text,
                           fontsize=font_size,
                           color='white',
                           stroke_color='black',
                           stroke_width=3,
                           font='Liberation-Sans-Bold',
                           method='caption',
                           size=(video_size[0] * 0.9, None))
        
        y_position = video_size[1] * 0.82
        txt_clip = txt_clip.set_position(('center', y_position)).set_duration(duration).set_start(start_time)
        
        return [txt_clip]

def add_interactive_subtitles_with_timing(video_path, srt_path, clip_path, output_path):
    """Add interactive subtitles to video with clip timing adjustment"""
    print(f"🎬 Loading video: {video_path}")
    
    try:
        # Load clip timing
        with open(clip_path, 'r') as f:
            clip_data = json.load(f)
        
        # Convert clip start/end to seconds
        def time_to_seconds(time_str):
            """Convert HH:MM:SS format to seconds"""
            h, m, s = map(int, time_str.split(':'))
            return h * 3600 + m * 60 + s
        
        clip_start = time_to_seconds(clip_data['start'])
        clip_end = time_to_seconds(clip_data['end'])
        clip_duration = clip_end - clip_start
        
        print(f"📊 Clip timing: {clip_data['start']} to {clip_data['end']} ({clip_duration:.1f}s)")
        
        # Load video
        video = VideoFileClip(video_path)
        video_size = video.size
        
        print(f"📊 Video size: {video_size}, Duration: {video.duration:.2f}s")
        
        # Parse subtitles
        print(f"📝 Parsing subtitles: {srt_path}")
        all_subtitles = parse_srt_file(srt_path)
        
        if not all_subtitles:
            print("⚠️  No subtitles found, saving video without subtitles")
            video.write_videofile(output_path, codec='libx264', audio_codec='aac')
            video.close()
            return
        
        # Filter subtitles to only those within the clip timerange
        clip_subtitles = []
        for sub in all_subtitles:
            # Check if subtitle overlaps with clip timing
            if sub['end'] > clip_start and sub['start'] < clip_end:
                # Adjust timing relative to clip start
                adjusted_start = max(0, sub['start'] - clip_start)
                adjusted_end = min(clip_duration, sub['end'] - clip_start)
                
                # Only add if there's meaningful duration
                if adjusted_end > adjusted_start and adjusted_end > 0:
                    clip_subtitles.append({
                        'start': adjusted_start,
                        'end': adjusted_end,
                        'text': sub['text']
                    })
        
        print(f"📚 Found {len(clip_subtitles)} subtitle entries within clip timerange")
        
        # Create subtitle clips with word highlighting
        subtitle_clips = []
        for i, sub in enumerate(clip_subtitles):
            # Only add subtitles that fall within video duration
            if sub['start'] < video.duration and sub['end'] <= video.duration:
                # Create background subtitle clips
                bg_clips = create_subtitle_clip(sub['text'], sub['start'], sub['end'], video_size)
                subtitle_clips.extend(bg_clips)
                
                # Create word highlighting clips
                highlight_clips = create_word_highlighting_clips(sub['text'], sub['start'], sub['end'], video_size)
                subtitle_clips.extend(highlight_clips)
                
                print(f"✅ Added subtitle {i+1}: {sub['start']:.1f}s - {sub['end']:.1f}s")
        
        if not subtitle_clips:
            print("⚠️  No valid subtitle clips created, saving video without subtitles")
            video.write_videofile(output_path, codec='libx264', audio_codec='aac')
            video.close()
            return
        
        # Composite video with subtitles
        print("🎭 Compositing video with subtitles...")
        final_video = CompositeVideoClip([video] + subtitle_clips)
        
        # Write final video with ULTRA HIGH QUALITY settings
        print(f"💾 Writing final video: {output_path}")
        final_video.write_videofile(output_path,
                                  codec='libx264',
                                  audio_codec='aac',
                                  bitrate='8000k',  # Ultra high bitrate for best quality
                                  audio_bitrate='320k',  # High audio quality
                                  fps=60,  # High framerate for smooth playback
                                  preset='slower',  # Best encoding quality
                                  temp_audiofile='temp-audio.m4a',
                                  remove_temp=True)
        
        # Clean up
        video.close()
        final_video.close()
        
        print(f"✅ Interactive subtitles added successfully!")
        
    except Exception as e:
        print(f"❌ Error processing video: {e}")
        raise

def add_interactive_subtitles(video_path, srt_path, output_path):
    """Add interactive subtitles to video"""
    print(f"🎬 Loading video: {video_path}")
    
    try:
        # Load video
        video = VideoFileClip(video_path)
        video_size = video.size
        
        print(f"📊 Video size: {video_size}, Duration: {video.duration:.2f}s")
        
        # Parse subtitles
        print(f"📝 Parsing subtitles: {srt_path}")
        subtitles = parse_srt_file(srt_path)
        
        if not subtitles:
            print("⚠️  No subtitles found, saving video without subtitles")
            video.write_videofile(output_path, codec='libx264', audio_codec='aac')
            video.close()
            return
        
        print(f"📚 Found {len(subtitles)} subtitle entries")
        
        # Create subtitle clips
        subtitle_clips = []
        for i, sub in enumerate(subtitles):
            # Only add subtitles that fall within video duration
            if sub['start'] < video.duration and sub['end'] <= video.duration:
                clip = create_subtitle_clip(sub['text'], sub['start'], sub['end'], video_size)
                subtitle_clips.append(clip)
                print(f"✅ Added subtitle {i+1}: {sub['start']:.1f}s - {sub['end']:.1f}s")
        
        if not subtitle_clips:
            print("⚠️  No valid subtitle clips created, saving video without subtitles")
            video.write_videofile(output_path, codec='libx264', audio_codec='aac')
            video.close()
            return
        
        # Composite video with subtitles
        print("🎭 Compositing video with subtitles...")
        final_video = CompositeVideoClip([video] + subtitle_clips)
        
        # Write final video with higher quality settings
        print(f"💾 Writing final video: {output_path}")
        final_video.write_videofile(output_path,
                                  codec='libx264',
                                  audio_codec='aac',
                                  bitrate='2000k',  # Higher bitrate
                                  audio_bitrate='192k',
                                  fps=30,
                                  temp_audiofile='temp-audio.m4a',
                                  remove_temp=True)
        
        # Clean up
        video.close()
        final_video.close()
        
        print(f"✅ Interactive subtitles added successfully!")
        
    except Exception as e:
        print(f"❌ Error processing video: {e}")
        raise

def process_short_video(video_path):
    """Process a single short video to add interactive subtitles"""
    video_name = Path(video_path).stem
    
    # Remove _short suffix to get original name
    if video_name.endswith('_short'):
        base_name = video_name[:-6]  # Remove '_short'
    else:
        base_name = video_name
    
    print(f"🎯 Processing: {base_name}")
    
    # Find corresponding SRT file
    srt_file = os.path.join(SUBTITLES_DIR, f"{base_name}.srt")
    
    if not os.path.exists(srt_file):
        print(f"⚠️  SRT file not found: {srt_file}")
        print("Skipping subtitle overlay...")
        return
    
    # Find corresponding clip timing JSON file
    clip_file = os.path.join(SUBTITLES_DIR, f"{base_name}.clip.json")
    
    if not os.path.exists(clip_file):
        print(f"⚠️  Clip timing file not found: {clip_file}")
        print("Skipping subtitle overlay...")
        return
    
    # Create output filename
    output_path = os.path.join(SHORTS_DIR, f"{base_name}_with_subtitles.mp4")
    
    print(f"📄 SRT file: {srt_file}")
    print(f"� Clip file: {clip_file}")
    print(f"�💾 Output: {output_path}")
    
    add_interactive_subtitles_with_timing(video_path, srt_file, clip_file, output_path)

def main():
    """Main function to process all short videos"""
    print("🎬 Starting interactive subtitle creation...")
    
    # Note: check_for_packages() removed for compatibility with MoviePy 1.0.3
    
    if not os.path.exists(SHORTS_DIR):
        print(f"❌ Shorts directory not found: {SHORTS_DIR}")
        sys.exit(1)
    
    # Find all short video files (ending with _short.mp4)
    short_files = list(Path(SHORTS_DIR).glob("*_short.mp4"))
    
    if not short_files:
        print(f"❌ No short videos found in {SHORTS_DIR}")
        print("Please run create_short.sh first")
        sys.exit(1)
    
    print(f"🎥 Found {len(short_files)} short videos to process")
    
    for video_file in short_files:
        try:
            process_short_video(str(video_file))
            print("-" * 60)
        except Exception as e:
            print(f"❌ Failed to process {video_file}: {e}")
            continue
    
    print("🎉 Interactive subtitle creation complete!")
    print(f"📁 Check output in: {SHORTS_DIR}")

if __name__ == "__main__":
    main()
