#!/usr/bin/env python3

"""
romanize_subtitles.py
Detects language in subtitle files and romanizes Urdu/Hindi text using OpenRouter API
Usage: python3 romanize_subtitles.py
"""

import os
import sys
import json
import requests
import re
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

def detect_language(text):
    """Simple language detection based on script"""
    # Check for Urdu/Hindi/Arabic scripts
    urdu_hindi_chars = set('آابپتٹثجچحخدڈذرڑزژسشصضطظعغفقکگلمنوہھءیےअआइईउऊएऐओऔकखगघचछजझञटठडढणतथदधनपफबभमयरलवशषसहक्षत्रज्ञ')
    
    char_count = 0
    urdu_hindi_count = 0
    
    for char in text:
        if char.isalpha():
            char_count += 1
            if char in urdu_hindi_chars:
                urdu_hindi_count += 1
    
    if char_count == 0:
        return "unknown"
    
    ratio = urdu_hindi_count / char_count
    if ratio > 0.3:  # If more than 30% of characters are Urdu/Hindi
        return "urdu_hindi"
    else:
        return "english"

def romanize_text_with_api(text):
    """Romanize text using OpenRouter API"""
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""Please romanize the following Urdu/Hindi text into Roman script (English letters). 
Keep the meaning intact and use commonly accepted romanization conventions.
Only return the romanized text, nothing else.

Text to romanize:
{text}"""
    
    data = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 4000,
        "temperature": 0.1
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        romanized_text = result["choices"][0]["message"]["content"].strip()
        return romanized_text
        
    except Exception as e:
        print(f"❌ Error calling OpenRouter API: {e}")
        return None

def process_subtitle_file(file_path):
    """Process a single subtitle file"""
    print(f"📄 Processing: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        if not content:
            print(f"⚠️  File is empty: {file_path}")
            return
        
        # Detect language
        language = detect_language(content)
        print(f"🔍 Detected language: {language}")
        
        if language == "urdu_hindi":
            print("🔄 Romanizing text...")
            romanized_content = romanize_text_with_api(content)
            
            if romanized_content:
                # Save romanized version
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(romanized_content)
                print(f"✅ Romanized and saved: {file_path}")
            else:
                print(f"❌ Failed to romanize: {file_path}")
        else:
            print(f"ℹ️  No romanization needed for: {file_path}")
            
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")

def main():
    """Main function to process all subtitle files"""
    print("🌐 Starting subtitle romanization...")
    
    if not os.path.exists(SUBTITLES_DIR):
        print(f"❌ Subtitles directory not found: {SUBTITLES_DIR}")
        sys.exit(1)
    
    # Find all .txt files in subtitles directory
    txt_files = list(Path(SUBTITLES_DIR).glob("*.txt"))
    
    if not txt_files:
        print(f"❌ No .txt files found in {SUBTITLES_DIR}")
        sys.exit(1)
    
    print(f"📚 Found {len(txt_files)} subtitle files to process")
    
    for txt_file in txt_files:
        process_subtitle_file(str(txt_file))
    
    print("🎉 Romanization complete!")

if __name__ == "__main__":
    main()
