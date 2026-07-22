# Kik Clipper

AI-powered tool that turns Twitch/Kick stream VODs into short-form clips ready for TikTok, YouTube Shorts, and Instagram Reels.

**What it does:** Give it a VOD link → it downloads, transcribes, finds the best moments with AI, and outputs vertical clips with text overlays and pro video effects.

```
Output:
output/
├── 001_clip.mp4        ← ready to upload
├── 002_clip.mp4
├── 003_clip.mp4
└── caption_001-003.txt ← copy-paste captions
```

---

## Features

- **AI highlight detection** — DeepSeek finds the most engaging moments automatically
- **Word-by-word captions** — synced subtitles that pop as the streamer talks
- **17 text overlay styles** — bold, minimal, neon, fire, ice, gaming, and more
- **15 video editing styles** — cinematic, dramatic, retro, viral, sports, etc.
- **9:16 vertical format** — auto-crops horizontal VODs for mobile platforms
- **Ken Burns zoom** — subtle auto-zoom for visual interest
- **Pro post-processing** — color grading, vignette, film grain, sharpening

---

## Quick Start

### 1. Install prerequisites

```bash
# macOS
brew install ffmpeg python3
pip3 install yt-dlp openai-whisper pydantic rich httpx openai

# Ubuntu/Debian
sudo apt install ffmpeg python3-pip
pip3 install yt-dlp openai-whisper pydantic rich httpx openai
```

### 2. Get a DeepSeek API key

1. Go to [platform.deepseek.com](https://platform.deepseek.com)
2. Create an account and add credits ($5 lasts hundreds of clips)
3. Create an API key

### 3. Set your API key

```bash
export DEEPSEEK_API_KEY="sk-your-key-here"

# Make it permanent (persists across terminal sessions):
echo 'export DEEPSEEK_API_KEY="sk-your-key-here"' >> ~/.zshrc
source ~/.zshrc
```

### 4. Run it

```bash
cd kik-clipper
python3 pipeline.py --vod https://kick.com/streamer/video/abc123 --streamer xQc --game Overwatch
```

That's it. Clips appear in `output/`.

---

## Usage Examples

**Basic — just give it a VOD:**

```bash
python3 pipeline.py --vod https://kick.com/xqc/video/abc123 --streamer xQc --game Overwatch
```

**With style options:**

```bash
python3 pipeline.py \
  --vod https://kick.com/xqc/video/abc123 \
  --streamer xQc \
  --game Overwatch \
  --style bold \
  --editing-style cinematic \
  --clips 5 \
  --duration 30
```

**Local file (already downloaded VOD):**

```bash
python3 pipeline.py --vod /path/to/vod.mp4 --streamer xQc --game Overwatch
```

**With your own transcript (skip Whisper):**

```bash
python3 pipeline.py --vod vod.mp4 --streamer xQc --game Overwatch --transcript transcript.json
```

**See all available styles:**

```bash
python3 pipeline.py --list-styles
python3 pipeline.py --list-editing-styles
```

---

## CLI Options

| Flag                    | Default      | Description                            |
| ----------------------- | ------------ | -------------------------------------- |
| `--vod`                 | **required** | Kick/Twitch URL or local file path     |
| `--streamer`            | **required** | Streamer name                          |
| `--game`                | **required** | Game being played                      |
| `--style`               | `bold`       | Text overlay style (see below)         |
| `--editing-style`       | `clean`      | Video effects style (see below)        |
| `--clips`               | `3`          | Number of clips to generate            |
| `--duration`            | `40`         | Target clip length in seconds          |
| `--tone`                | `hype`       | `hype`, `chill`, or `funny`            |
| `--transcript`          | none         | Pre-made transcript file (JSON or TXT) |
| `--horizontal`          | off          | Output 16:9 instead of 9:16 vertical   |
| `--no-zoom`             | off          | Disable Ken Burns zoom effect          |
| `--list-styles`         | —            | Show all overlay styles and exit       |
| `--list-editing-styles` | —            | Show all editing styles and exit       |

---

## Text Overlay Styles

These control the **text look** — font size, colors, stroke, etc.

| Style      | Description                                   |
| ---------- | --------------------------------------------- |
| `bold`     | Large white text with black outline (default) |
| `minimal`  | Smaller text, clean look, no outline          |
| `gambling` | Gold/green theme for casino content           |
| `dramatic` | Red/white for intense moments                 |
| `gaming`   | Neon cyan/purple for gaming                   |
| `sports`   | Bold orange/blue for sports                   |
| `podcast`  | Clean white on dark for podcasts              |
| `reaction` | Fun yellow/pink for reaction videos           |
| `news`     | Professional blue/white                       |
| `viral`    | Trendy fuchsia/cyan for viral content         |
| `horror`   | Dark red/black for spooky content             |
| `retro`    | Pixel-art green/amber for nostalgia           |
| `neon`     | Bright neon pink/cyan/yellow                  |
| `pastel`   | Soft pastel colors for lifestyle              |
| `fire`     | Orange/red gradient for hype moments          |
| `ice`      | Blue/cyan for cool/calm moments               |
| `gold`     | Premium gold/black for luxury content         |

---

## Video Editing Styles

These control the **video effects** — color grading, grain, vignette, etc. Applied via FFmpeg after the clip is composed.

| Style        | Description                                          |
| ------------ | ---------------------------------------------------- |
| `none`       | No effects, raw output                               |
| `minimal`    | Clean output, no effects                             |
| `clean`      | Subtle grade, light sharpen                          |
| `cinematic`  | S-curve contrast, warm tones, vignette, subtle grain |
| `dramatic`   | High contrast, desaturated, heavy vignette           |
| `film`       | Film emulation: contrast, grain, vignette            |
| `viral_hype` | High contrast, saturated, sharpened                  |
| `gaming`     | Neon boost, high saturation, edge enhance            |
| `retro`      | VHS look: color shift, grain, soft focus             |
| `sports`     | High contrast, saturated, sharp                      |
| `podcast`    | Warm tones, subtle grain                             |
| `reaction`   | Bright, saturated, energetic                         |
| `dark`       | Desaturated, high contrast, moody                    |
| `vintage`    | Faded, warm, grain, light leak feel                  |
| `neon`       | High saturation, color boost, glow                   |

---

## How It Works

```
VOD URL
  ↓
1. DOWNLOAD — yt-dlp pulls the video from Kick/Twitch
  ↓
2. TRANSCRIBE — Whisper converts speech to text with word-level timestamps
  ↓
3. ANALYZE — DeepSeek AI finds the most engaging highlight moments
  ↓
4. COMPOSE — MoviePy builds each clip with text overlays and effects
  ↓
5. POST-PROCESS — FFmpeg applies color grading, vignette, sharpening
  ↓
Numbered MP4 clips + caption text file
```

---

## Project Structure

```
kik-clipper/
├── pipeline.py          # Main entry point (CLI)
├── schema.py            # Data models and style definitions
├── script_gen.py        # DeepSeek AI integration
├── ffmpeg_compose.py    # Video composition and effects
├── fetch.py             # VOD download and audio extraction
├── pyproject.toml       # Python dependencies
├── GUIDE.md             # Detailed guide
└── output/              # Generated clips (git-ignored)
```

---

## Troubleshooting

**"ffmpeg not found"**

```bash
export PATH="/opt/homebrew/bin:$PATH"
```

**"DEEPSEEK_API_KEY not set"**

```bash
export DEEPSEEK_API_KEY="sk-your-key"
```

**"SSL certificate verify failed" (macOS)**

```bash
open "/Applications/Python 3.13/Install Certificates.command"
```

**"dquote>" prompt appears**
You have an unclosed quote. Press `Ctrl+C` and retype the command on one line.

**Whisper is slow**
First run downloads the ~150MB model. Subsequent runs are faster. On CPU it takes a few minutes per hour of video — this is normal.

**Kick download fails**
Make sure you're logged into Chrome. The tool uses your browser cookies to bypass Kick's authentication.

**Wrong Python version**
Make sure you're using Python 3.11+:

```bash
python3 --version
```

---

## Tips

- **Duration:** 30-40 seconds works best for Shorts/TikTok/Reels
- **Clips:** Start with 3, increase if quality is good
- **Tone:** `hype` for wins, `funny` for rage/fail moments, `chill` for casual
- **Captions:** Copy from `output/caption_XXX-XXX.txt` for your posts
- **Audio:** Add trending audio yourself after downloading clips
- **Batch processing:** Run it multiple times — clips are numbered sequentially (001, 002, 003...)
- **Best results:** Use VODs with clear audio and minimal background noise

---

## Moving to Another Computer

```bash
# Copy the project
cp -r /path/to/kik-clipper ~/Desktop/kik-clipper

# On new computer — install prereqs
brew install ffmpeg python3
pip3 install yt-dlp openai-whisper pydantic rich httpx openai

# Set API key
export DEEPSEEK_API_KEY="sk-your-key"

# Run
cd ~/Desktop/kik-clipper
python3 pipeline.py --vod your-vod --streamer name --game CS2
```

---

## Requirements

- Python 3.11+
- FFmpeg
- yt-dlp
- OpenAI Whisper
- DeepSeek API key (~$5 for hundreds of clips)

---

## License

MIT
