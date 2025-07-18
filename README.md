# YouTube to Shorts Automation System

Complete Bash + Python automation system to convert YouTube videos into viral short clips with interactive subtitles.

## 📁 Directory Structure

```
~/automation/
├── scripts/              # All automation scripts
│   ├── download_video.sh           # Download YouTube videos
│   ├── transcribe_video.sh         # Transcribe videos using whisper.cpp
│   ├── romanize_subtitles.py       # Convert Urdu/Hindi to Roman script
│   ├── suggest_clip.py             # AI-powered viral clip suggestions
│   ├── create_short.sh             # Create short clips using ffmpeg
│   ├── create_interactive_subtitles.py  # Add interactive subtitles
│   └── process_all.sh              # Complete pipeline
├── download/             # Raw downloaded videos (MP4)
├── transcribe/           # [Optional] Audio files (WAV)
├── subtitles/            # Generated subtitles (.srt/.txt) and clip suggestions (.json)
├── shorts/               # Final short videos with interactive subtitles
├── requirements.txt      # Python dependencies
├── setup.sh             # Installation script
└── README.md            # This file
```

## 🚀 Quick Start

### 1. Setup Dependencies
```bash
cd ~/automation
./setup.sh
```

### 2. Process a YouTube Video (Complete Pipeline)
```bash
# First activate the virtual environment (if using Arch Linux)
source ~/automation/venv/bin/activate

./scripts/process_all.sh "https://www.youtube.com/watch?v=YOUR_VIDEO_ID"
```

That's it! The system will:
1. Download the video
2. Transcribe it using Whisper
3. Romanize non-English text
4. Suggest viral clip segments using AI
5. Create short clips
6. Add interactive subtitles

## 📋 Individual Script Usage

### Download Video Only
```bash
./scripts/download_video.sh "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Transcribe Videos Only
```bash
./scripts/transcribe_video.sh
```

### Romanize Subtitles Only
```bash
# Activate virtual environment first (Arch Linux)
source ~/automation/venv/bin/activate
./scripts/run_python.sh romanize_subtitles.py
```

### Suggest Viral Clips Only
```bash
# Activate virtual environment first (Arch Linux)
source ~/automation/venv/bin/activate
./scripts/run_python.sh suggest_clip.py
```

### Create Short Clips Only
```bash
./scripts/create_short.sh
```

### Add Interactive Subtitles Only
```bash
# Activate virtual environment first (Arch Linux)
source ~/automation/venv/bin/activate
./scripts/run_python.sh create_interactive_subtitles.py
```

## 🔧 Configuration

### OpenRouter API
The system uses DeepSeek v3 (free) model via OpenRouter for:
- Language detection and romanization
- Viral clip suggestions

API key is configured in:
- `scripts/romanize_subtitles.py`
- `scripts/suggest_clip.py`

### Whisper Model
The system automatically detects and uses the best available model:
- **medium** (1.5 GB) - Best accuracy (if available)
- **base.en** (74 MB) - Good accuracy, English only
- **base** (74 MB) - Good accuracy, multilingual

Priority order: medium → base.en → base

You already have both `ggml-medium.bin` and `ggml-base.en.bin` models, so the system will use the medium model for better transcription accuracy!

## 📊 Output Files

### Download Directory
- `Video Title.mp4` - Original downloaded video

### Subtitles Directory
- `Video Title.txt` - Text transcript (romanized if needed)
- `Video Title.srt` - SRT subtitle file with timestamps
- `Video Title.clip.json` - AI-suggested clip with timestamps and reason

### Shorts Directory
- `Video Title_short.mp4` - Short clip without subtitles
- `Video Title_with_subtitles.mp4` - Final video with interactive subtitles

## 🎯 Features

### Smart Language Detection
- Automatically detects Urdu/Hindi scripts
- Romanizes non-English text for better accessibility
- Preserves English content unchanged

### AI-Powered Clip Suggestions
- Analyzes transcript content for viral potential
- Suggests optimal 30-90 second segments
- Provides reasoning for each suggestion
- Looks for emotional moments, insights, and quotable content

### Interactive Subtitles
- Word-level timing (when available)
- Highlighted current words
- Professional styling with stroke borders
- Optimized for mobile viewing

### Error Handling
- Comprehensive logging with timestamps
- Graceful failure handling
- Detailed error messages
- Progress tracking

## 🛠️ Dependencies

### System Requirements
- Arch Linux (or other Linux distributions)
- Python 3.8+
- FFmpeg
- Git

### Installed by Setup Script
- `yt-dlp` - YouTube video downloader
- `whisper.cpp` - Fast speech recognition
- `ffmpeg` - Video processing
- Python packages: `requests`, `moviepy`, `langdetect`

## ⚡ Performance Tips

### For Faster Processing
1. Use smaller Whisper models for speed
2. Process shorter videos (< 30 minutes)
3. Use SSD storage for faster I/O

### For Better Quality
1. Use larger Whisper models (`medium` or `large`)
2. Ensure good audio quality in source videos
3. Review AI suggestions before creating clips

## 🐛 Troubleshooting

### Common Issues

#### "whisper.cpp not found"
```bash
cd ~
git clone https://github.com/ggerganov/whisper.cpp.git
cd whisper.cpp
make
bash ./models/download-ggml-model.sh base.en
```

#### "No MP4 files found"
Ensure videos are downloaded to `~/automation/download/` directory.

#### "MoviePy import error"
```bash
pip install --user moviepy
```

#### "OpenRouter API error"
Check your internet connection and API key in the Python scripts.

### Logs
All scripts provide detailed logging with timestamps. Check console output for specific error messages.

## 📈 Optimization for Different Content Types

### Educational Content
- Longer clips (60-90s) for complete thoughts
- Focus on key insights and actionable advice

### Entertainment Content
- Shorter clips (30-60s) for quick engagement
- Highlight funny or surprising moments

### Interview Content
- Find quotable statements and revelations
- Look for emotional or controversial moments

## 🔒 Security Notes

- API key is stored in script files (consider environment variables for production)
- Downloaded content respects YouTube's terms of service
- No personal data is transmitted to AI services

## 📱 Social Media Ready

Output videos are optimized for:
- TikTok (vertical format compatible)
- YouTube Shorts
- Instagram Reels
- Twitter/X videos

## 🤝 Contributing

Feel free to enhance the scripts:
1. Add support for more languages
2. Improve subtitle styling
3. Add more AI models
4. Optimize performance

## 📄 License

This automation system is for personal and educational use. Respect YouTube's terms of service and content creators' rights.
