#!/usr/bin/env python3

"""
suggest_clip.py
Analyzes romanized transcripts and suggests viral/important clip segments using OpenRouter API
Usage: python3 suggest_clip.py
"""

import os
import sys
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    print("❌ OPENROUTER_API_KEY not found in .env file!")
    print("Please add your OpenRouter API key to the .env file")
    sys.exit(1)

MODEL_NAME = "deepseek/deepseek-chat"  # DeepSeek v3 (free) model
SUBTITLES_DIR = os.path.expanduser("~/automation/subtitles")

def suggest_clip_with_api(transcript):
    """Use OpenRouter API to suggest a clip segment"""
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""Analyze the following video transcript and suggest ONE short clip segment (30-90 seconds) that would be most viral or engaging for social media.

Please provide your response in this exact JSON format:
{{
    "start": "HH:MM:SS",
    "end": "HH:MM:SS",
    "reason": "Brief explanation why this segment is viral/engaging"
}}

Look for:
- Emotional moments
- Key insights or revelations
- Funny or surprising content
- Actionable advice
- Dramatic moments
- Quotable statements

Transcript:
{transcript}"""
    
    data = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 500,
        "temperature": 0.3
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        suggestion_text = result["choices"][0]["message"]["content"].strip()
        
        # Try to extract JSON from the response
        start_idx = suggestion_text.find('{')
        end_idx = suggestion_text.rfind('}') + 1
        
        if start_idx != -1 and end_idx != -1:
            json_str = suggestion_text[start_idx:end_idx]
            suggestion = json.loads(json_str)
            return suggestion
        else:
            print(f"❌ Could not parse JSON from API response: {suggestion_text}")
            return None
        
    except Exception as e:
        print(f"❌ Error calling OpenRouter API: {e}")
        return None

def convert_time_to_seconds(time_str):
    """Convert HH:MM:SS to seconds"""
    parts = time_str.split(':')
    if len(parts) == 3:
        hours, minutes, seconds = map(int, parts)
        return hours * 3600 + minutes * 60 + seconds
    elif len(parts) == 2:
        minutes, seconds = map(int, parts)
        return minutes * 60 + seconds
    else:
        return int(parts[0])

def validate_timestamps(start_time, end_time):
    """Validate that timestamps are reasonable"""
    start_seconds = convert_time_to_seconds(start_time)
    end_seconds = convert_time_to_seconds(end_time)
    
    if start_seconds >= end_seconds:
        return False, "Start time must be before end time"
    
    duration = end_seconds - start_seconds
    if duration < 15:
        return False, "Clip too short (minimum 15 seconds)"
    
    if duration > 120:
        return False, "Clip too long (maximum 120 seconds)"
    
    return True, "Valid"

def extract_text_from_srt(srt_content):
    """Extract just the text content from SRT format"""
    import re
    
    # Split by double newlines to get subtitle blocks
    blocks = re.split(r'\n\s*\n', srt_content.strip())
    text_lines = []
    
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 3:
            # Skip sequence number and timestamp, get text (lines 2+)
            text = ' '.join(lines[2:]).strip()
            if text:
                text_lines.append(text)
    
    return ' '.join(text_lines)

def process_transcript_file(file_path):
    """Process a single transcript file and generate clip suggestion"""
    print(f"📄 Processing: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        if not content:
            print(f"⚠️  File is empty: {file_path}")
            return
        
        # Check if this is an SRT file and extract text content
        if file_path.endswith('.srt'):
            print("📝 Processing SRT file - extracting text content")
            transcript = extract_text_from_srt(content)
        else:
            transcript = content
        
        if not transcript:
            print(f"⚠️  No text content found in: {file_path}")
            return
        
        if len(transcript) < 100:
            print(f"⚠️  Transcript too short for analysis: {file_path}")
            return
        
        print("🤖 Analyzing transcript for viral moments...")
        suggestion = suggest_clip_with_api(transcript)
        
        if suggestion:
            # Validate timestamps
            start_time = suggestion.get("start", "00:00:00")
            end_time = suggestion.get("end", "00:01:00")
            
            is_valid, message = validate_timestamps(start_time, end_time)
            
            if is_valid:
                # Save suggestion as JSON
                base_name = Path(file_path).stem
                clip_file = os.path.join(SUBTITLES_DIR, f"{base_name}.clip.json")
                
                with open(clip_file, 'w', encoding='utf-8') as f:
                    json.dump(suggestion, f, indent=2, ensure_ascii=False)
                
                print(f"✅ Clip suggestion saved: {clip_file}")
                print(f"🎬 Suggested clip: {start_time} - {end_time}")
                print(f"💡 Reason: {suggestion.get('reason', 'No reason provided')}")
            else:
                print(f"❌ Invalid timestamps: {message}")
                print(f"   Start: {start_time}, End: {end_time}")
        else:
            print(f"❌ Failed to generate clip suggestion for: {file_path}")
            
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")

def main():
    """Main function to process all transcript files"""
    print("🎯 Starting clip suggestion analysis...")
    
    if not os.path.exists(SUBTITLES_DIR):
        print(f"❌ Subtitles directory not found: {SUBTITLES_DIR}")
        sys.exit(1)
    
    # Find transcript files - prioritize SRT (from YouTube) over TXT (from whisper)
    srt_files = list(Path(SUBTITLES_DIR).glob("*.srt"))
    txt_files = list(Path(SUBTITLES_DIR).glob("*.txt"))
    
    # Use SRT files if available, otherwise fall back to TXT files
    if srt_files:
        transcript_files = srt_files
        print(f"📝 Using {len(srt_files)} SRT files (YouTube subtitles)")
    elif txt_files:
        transcript_files = txt_files
        print(f"📝 Using {len(txt_files)} TXT files (whisper transcripts)")
    else:
        print(f"❌ No subtitle files found in {SUBTITLES_DIR}")
        sys.exit(1)
    
    print(f"📚 Found {len(transcript_files)} transcript files to analyze")
    
    for transcript_file in transcript_files:
        process_transcript_file(str(transcript_file))
        print("-" * 50)
    
    print("🎉 Clip suggestion analysis complete!")

if __name__ == "__main__":
    main()
