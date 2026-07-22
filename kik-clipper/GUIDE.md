# Kik Clipper - Ultimate Guide

## What it does

Automatically generates short-form clips from CSGORoll stream recordings. It downloads the VOD, transcribes it, finds the best gambling moments, and outputs numbered clips with text overlays ready to upload.

**Output:**

```
output/
├── 001_clip.mp4
├── 002_clip.mp4
├── 003_clip.mp4
└── caption_001-003.txt
```

## Prerequisites

| Item             | Install                       |
| ---------------- | ----------------------------- |
| Python 3.11+     | `brew install python`         |
| FFmpeg           | `brew install ffmpeg`         |
| yt-dlp           | `pip3 install yt-dlp`         |
| Whisper          | `pip3 install openai-whisper` |
| DeepSeek API key | platform.deepseek.com         |

## Setup

```bash
cd kik-clipper
pip3 install -e .
export DEEPSEEK_API_KEY="your-key"
```

## Usage

**Basic:**

```bash
python3 pipeline.py --vod https://kick.com/streamer/video/abc123 --streamer streamername --game CS2
```

**With options:**

```bash
python3 pipeline.py \
  --vod https://kick.com/streamer/video/abc123 \
  --streamer streamername \
  --game CS2 \
  --tone hype \
  --duration 40 \
  --clips 3
```

**Local VOD:**

```bash
python3 pipeline.py --vod /path/to/vod.mp4 --streamer name --game CS2
```

## Options

| Flag           | Default  | Description                      |
| -------------- | -------- | -------------------------------- |
| `--vod`        | required | Kick URL or local file           |
| `--streamer`   | required | Streamer name                    |
| `--game`       | required | Game name                        |
| `--tone`       | hype     | hype, chill, funny               |
| `--duration`   | 40       | Clip length in seconds           |
| `--clips`      | 3        | Number of clips to generate      |
| `--transcript` | none     | Skip transcription with own file |

## How it works

1. **Download** - yt-dlp pulls the VOD from Kick
2. **Transcribe** - Whisper converts speech to text
3. **Analyze** - DeepSeek finds the best gambling moments
4. **Cut** - FFmpeg extracts clips from the VOD
5. **Overlay** - Adds text (hook, overlay, outro)
6. **Output** - Numbered MP4s + caption file

## Moving to another computer

**Copy the project:**

```bash
cp -r /path/to/kik-clipper ~/Desktop/kik-clipper
# or
zip -r kik-clipper.zip /path/to/kik-clipper
```

**On new computer:**

```bash
# Install prereqs
brew install ffmpeg
pip3 install yt-dlp openai-whisper pydantic rich httpx openai

# Set API key
export DEEPSEEK_API_KEY="your-key"

# Run
cd kik-clipper
python3 pipeline.py --vod your-vod --streamer name --game CS2
```

**To make API key permanent:**

```bash
echo 'export DEEPSEEK_API_KEY="your-key"' >> ~/.zshrc
source ~/.zshrc
```

## Troubleshooting

**"ffmpeg not found"**

```bash
export PATH="/opt/homebrew/bin:$PATH"
```

**"DEEPSEEK_API_KEY not set"**

```bash
export DEEPSEEK_API_KEY="your-key"
```

**"SSL certificate verify failed"**

```bash
open "/Applications/Python 3.13/Install Certificates.command"
```

**"dquote>" prompt**
You have an unclosed quote. Press Ctrl+C and retype the command on one line.

**Whisper is slow**
Normal on CPU. First run downloads the model (~150MB). Subsequent runs are faster.

**Kick download fails**
Make sure you're logged into Chrome (cookies are used to bypass Kick's block).

## File structure

```
kik-clipper/
├── pyproject.toml       # Dependencies
├── schema.py            # Data models
├── script_gen.py        # DeepSeek prompts
├── ffmpeg_compose.py    # FFmpeg editing
├── fetch.py             # VOD download
├── pipeline.py          # Main entry point
└── output/              # Clips go here
```

## Tips

- **Duration:** 30-40 seconds works best for Shorts/TikTok
- **Clips:** Start with 3, increase if quality is good
- **Tone:** "hype" for wins, "funny" for rage moments
- **Caption:** Copy from `caption_XXX-XXX.txt` for posting
- **Audio:** Add trending audio yourself after downloading clips
