# Crayo Local

AI-powered short-form video generator. Generate viral TikToks, Reels, and YouTube Shorts from text, Reddit posts, or YouTube URLs — fully local, no cloud required.

## Quick Start

```bash
git clone <your-repo-url> crayo-local
cd crayo-local
./setup.sh    # install dependencies (Bun, ffmpeg, Python packages)
bun run dev   # start API on :3001, Web UI on :3000
```

Open **http://localhost:3000** in your browser.

## Features

### 15 Video Templates

| Template      | Description                                                               |
| ------------- | ------------------------------------------------------------------------- |
| Reddit Story  | Scrape a Reddit post, TTS voiceover, gameplay background                  |
| AI Story      | Paste a topic, AI generates a hook + script                               |
| Fake Text     | iMessage-style conversation with animated bubbles                         |
| Split Screen  | Two-panel layout with gameplay + captions                                 |
| Quiz / Trivia | Multiple choice with countdown timer                                      |
| Scary Story   | Horror narration with dark atmosphere                                     |
| Life Advice   | Motivational quote over gameplay                                          |
| POV Story     | First-person scenario videos                                              |
| Auto Clip     | Paste a YouTube URL → auto-detect highlights → generate clips             |
| Sermon Clip   | YouTube sermon → auto-detect highlights → captioned clips with hook intro |
| Sermon Quote  | Single powerful quote with dramatic text reveal                           |
| Testimony     | Personal testimony with emotional captions + dramatic music               |
| Podcast Clip  | YouTube podcast → auto-detect highlights → captioned clips                |
| Reaction      | React to a video — picture-in-picture commentary layout                   |
| Top 5 / List  | Countdown list with dramatic reveals — "Top 5 reasons..."                 |

### AI Script Writer

Generate viral scripts from any topic. Enter a topic, choose a style (Church, Motivational, Storytelling, Educational, Entertainment, News), set target duration, and get a complete script with hook, body, call-to-action, and hashtags. One-click apply to any template.

Requires DeepSeek API key — set `DEEPSEEK_API_KEY` in `.env` or environment.

### Hook Scorer

Rate your script hooks before rendering. Scores hooks 0-100 based on length, power words, curiosity triggers, specificity, urgency, and emotion. Get an S/A/B/C/D/F grade with actionable suggestions to improve retention.

### Script Variations

One topic → 5 unique script angles. Each variation uses a different approach (contrarian, personal story, expert authority, emotional appeal, shock value) with hook scores. Click "Use This" to instantly swap in a better-performing variation.

### Analytics Dashboard

Track total views, likes, comments, shares, and saves across all posted clips. See performance by platform (TikTok, Instagram Reels, YouTube Shorts). Data feeds back into future script generation.

### Post Queue & One-Click Posting

Queue renders for posting to TikTok, Instagram Reels, or YouTube Shorts. One-click post from the render complete screen. Posting queue shows status (queued/posting/posted/failed) with scheduled times.

> **Note**: Direct platform posting requires API keys. Set `INSTAGRAM_ACCESS_TOKEN`, `TIKTOK_ACCESS_TOKEN`, or `YOUTUBE_API_KEY` in `.env`. Without keys, posts are queued with placeholder URLs for manual upload.

### 10 Animated Subtitle Styles

Bold Pop, Word by Word, Colorful, Minimal, Typewriter, Bounce, Zoom, Glow, Neon, Shake — all rendered as ASS (Advanced SubStation Alpha) for smooth, native animations.

### Smart Zoom

YuNet DNN face detection + FFmpeg dynamic crop for face-tracking zoom on any video.

### Multi-Track Audio

Mix up to 5 background music tracks + ambient SFX with per-track volume and fade controls.

### Platform Formatting

Auto-format for TikTok/Reels (9:16), Instagram (1:1), or YouTube (16:9).

### Quality Presets

| Preset   | Resolution | FPS | CRF |
| -------- | ---------- | --- | --- |
| Draft    | 720x1280   | 24  | 32  |
| Standard | 1080x1920  | 30  | 26  |
| High     | 1080x1920  | 60  | 20  |
| Ultra    | 2160x3840  | 60  | 16  |

### Scene Transitions

Crossfade and zoom-cut transitions between clips.

### Custom Caption Editor

Edit auto-generated captions or write your own with precise timing control.

### Batch Renderer

Paste a YouTube URL → auto-detect N highlights → render all clips in one go with a live progress bar. Works with Sermon Clip and Podcast Clip templates.

### Silence Removal

Auto-detect and trim dead air from clips using ffmpeg's `silencedetect`. When enabled, silent pauses are removed and speaking segments are concatenated with smooth transitions. Configurable threshold (dB) and minimum silence duration.

### Media Library

Manage stock footage, background music, and fonts directly from the UI. Add your own clips to `assets/stocks/` and music to `assets/styles/` — the library works with any content type (sermons, podcasts, tutorials, gaming, etc.).

## Architecture

```
crayo-local/
├── packages/
│   ├── core/     # FFmpeg wrapper, DB, templates, ASS subtitle generator
│   ├── api/      # Hono REST API server
│   ├── web/      # SolidJS + Tailwind web UI
│   └── ai/       # TTS (Edge-TTS), STT (Whisper), face detection, bg removal
├── assets/
│   ├── stocks/   # Your video clips (sermons, podcasts, tutorials, gaming, etc.)
│   ├── styles/   # Background music
│   └── fonts/    # Custom fonts (optional)
└── data/
    ├── crayo.db  # SQLite database
    └── renders/  # Generated videos
```

## Tech Stack

- **Runtime**: Bun
- **Backend**: Hono
- **Frontend**: SolidJS + Tailwind CSS
- **Database**: SQLite + Drizzle ORM
- **Video**: FFmpeg
- **TTS**: Edge-TTS (free Microsoft voices)
- **STT**: Whisper (OpenAI)
- **Face Detection**: OpenCV + YuNet DNN
- **Background Removal**: rembg

## API Endpoints

| Method          | Path                        | Description                           |
| --------------- | --------------------------- | ------------------------------------- |
| GET             | `/api/health`               | Health check                          |
| GET/POST/DELETE | `/api/projects`             | Project CRUD                          |
| GET             | `/api/projects/:id/renders` | Get project renders                   |
| POST            | `/api/renders`              | Start render                          |
| GET             | `/api/renders/:id`          | Get render status                     |
| DELETE          | `/api/renders/:id`          | Delete render                         |
| GET             | `/api/voices`               | List TTS voices                       |
| POST            | `/api/tts`                  | Generate TTS audio                    |
| POST            | `/api/stt`                  | Transcribe audio                      |
| POST            | `/api/generate-script`      | AI script generation (DeepSeek)       |
| POST            | `/api/score-hook`           | Score a script hook (0-100)           |
| POST            | `/api/generate-variations`  | Generate 5 script variations          |
| POST            | `/api/auto-clip`            | YouTube URL → highlight clips         |
| POST            | `/api/sermon-clip`          | Sermon URL → captioned clips          |
| POST            | `/api/podcast-clip`         | Podcast URL → captioned clips         |
| POST            | `/api/reaction`             | PiP reaction video compositing        |
| POST            | `/api/top-list`             | Countdown list video generation       |
| POST            | `/api/batch-clip`           | Batch clip processing (with progress) |
| GET             | `/api/batch/:id/status`     | Get batch job progress                |
| POST            | `/api/remove-silence`       | Detect & trim silence from video      |
| POST            | `/api/remove-bg`            | Remove background from image          |
| POST            | `/api/audio/remove-vocals`  | Separate vocals from music            |
| POST            | `/api/audio/enhance`        | Enhance audio quality                 |
| POST            | `/api/post-now`             | Queue clip for platform posting       |
| GET             | `/api/analytics`            | Get all analytics data                |
| POST            | `/api/analytics`            | Add analytics data for a clip         |
| GET             | `/api/analytics/summary`    | Get analytics summary by platform     |
| GET             | `/api/post-queue`           | Get post queue                        |
| DELETE          | `/api/post-queue/:id`       | Remove from post queue                |
| POST            | `/api/download`             | Download YouTube/TikTok video         |
| POST            | `/api/reddit`               | Scrape Reddit post                    |
| GET/DELETE      | `/api/stocks`               | List/delete stock clips               |
| GET/DELETE      | `/api/music`                | List/delete background music          |

## Commands

```bash
bun run dev          # start API + web dev servers
bun run dev:api      # start API server only
bun run dev:web      # start web dev server only
bun run test         # run all tests
bun run typecheck    # typecheck all packages
```

## Requirements

- [Bun](https://bun.sh) >= 1.0
- FFmpeg (`brew install ffmpeg` on macOS)
- Python 3.10+ with pip
- OpenCV (`pip3 install opencv-python`)
- Edge-TTS (`pip3 install edge-tts`)
- Whisper (`pip3 install openai-whisper`)

Run `./setup.sh` to install everything automatically.

## License

MIT
