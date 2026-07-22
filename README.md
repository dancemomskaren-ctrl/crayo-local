# Crayo Local — Make Viral Videos With AI (No Experience Needed)

This tool makes TikToks, Reels, and YouTube Shorts for you. You type what you want, it makes the video. That's it.

**What it does:**

- You give it a topic → it writes a script → it makes the video with voiceover, captions, and gameplay background
- You give it a YouTube link → it finds the best moments → it makes clips automatically
- You give it a Reddit post → it reads it out loud with a cool background

**What you DON'T need:**

- No video editing skills
- No coding experience
- No paid software
- No cloud account

---

## Before You Start — Install These 3 Things

You need to install 3 programs first. Don't worry, it's easy.

### Step 1: Install Bun (the engine that runs this tool)

Open **Terminal** (press `Cmd + Space`, type "Terminal", hit Enter).

Copy and paste this line, then press Enter:

```bash
curl -fsSL https://bun.sh/install | bash
```

Wait for it to finish. If it asks you to restart Terminal, close it and open it again.

**Did it work?** Type `bun --version` and press Enter. If you see a number (like `1.3.14`), you're good.

### Step 2: Install FFmpeg (the video making tool)

Copy and paste this line into Terminal, then press Enter:

```bash
brew install ffmpeg
```

If you see "command not found", you need to install Homebrew first:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Then run `brew install ffmpeg` again.

**Did it work?** Type `ffmpeg -version` and press Enter. If you see version info, you're good.

### Step 3: Install Python packages (for AI features)

Copy and paste this entire block into Terminal, then press Enter:

```bash
pip3 install edge-tts openai-whisper opencv-python rembg
```

**Did it work?** Type `pip3 show edge-tts` and press Enter. If you see package info, you're good.

---

## Install Crayo Local

Now that you have Bun, FFmpeg, and Python packages installed:

```bash
# 1. Download the tool
git clone https://github.com/dancemomskaren-ctrl/crayo-local.git

# 2. Go into the folder
cd crayo-local

# 3. Install everything else it needs
bun install
```

**Done.** That's the installation.

---

## How to Use It

### Start the tool

Every time you want to use it, open Terminal and run:

```bash
cd crayo-local
bun run dev
```

You'll see some text scrolling. That's normal. When it says "running on http://localhost:3000", it's ready.

### Open the website

Open your web browser (Chrome, Safari, whatever) and go to:

```
http://localhost:3000
```

You'll see the Crayo interface. This is where you make videos.

### Make your first video

1. **Click "New Project"** (or whatever button starts a new project)
2. **Pick a template** — for your first time, pick "AI Story"
3. **Type a topic** — like "Why dogs are better than cats" or "Crazy facts about space"
4. **Click "Generate Script"** — the AI writes a script for you
5. **Click "Render"** — it makes the video

Wait 30-60 seconds. Your video is now in the `data/renders/` folder.

### Find your video

Your finished video is saved here:

```
crayo-local/data/renders/
```

Just open that folder in Finder and you'll see your `.mp4` file. Drag it anywhere — social media, text messages, wherever.

---

## Other Cool Stuff You Can Do

### Make a clip from a YouTube video

1. Find a YouTube video you like
2. Copy the URL (the link in the address bar)
3. In Crayo, paste it where it says "YouTube URL"
4. Click "Auto Clip"
5. It finds the best moments and makes clips for you

### Make a clip from a Twitch/Kick stream

1. Copy the stream URL
2. Paste it in the same YouTube URL box
3. Same process — it downloads and clips automatically

### Add your own gameplay footage

Put any `.mp4` video files in this folder:

```
crayo-local/assets/stocks/
```

The tool will use them as backgrounds automatically.

### Add your own music

Put any `.mp3` files in this folder:

```
crayo-local/assets/styles/
```

It'll play in the background of your videos.

---

## Troubleshooting (When Things Go Wrong)

### "Command not found: bun"

You didn't install Bun, or Terminal didn't restart. Close Terminal completely and open it again. Then run `bun --version` to check.

### "Command not found: ffmpeg"

You didn't install FFmpeg. Run `brew install ffmpeg`.

### "Python package not found"

Run `pip3 install edge-tts openai-whisper opencv-python rembg` again.

### Video is black / no captions

The tool might still be processing. Check Terminal for error messages. If you see red text, something broke — copy the error and search it online.

### Audio sounds weird / no audio

Make sure you have background music in `assets/styles/`. Put any `.mp3` file there.

### "Port 3000 already in use"

Something else is using that port. Run this to stop it:

```bash
lsof -ti:3000 | xargs kill
```

Then try `bun run dev` again.

---

## FAQ

**Do I need to know how to code?**
No. You just need to know how to open Terminal and paste commands.

**Does it cost money?**
No. Everything runs on your computer. No cloud, no subscriptions.

**Can I use it on Windows?**
Not yet. It's built for Mac. (Linux might work but hasn't been tested.)

**Can I use it without internet?**
Mostly yes. The AI script writer needs internet (it uses DeepSeek API). Everything else works offline.

**Where are my videos saved?**
In `crayo-local/data/renders/`. They're regular `.mp4` files you can share anywhere.

**Can I edit the captions?**
Yes. In the web interface, there's a caption editor where you can change the text and timing.

**How do I make it stop?**
Press `Ctrl + C` in Terminal. That kills the server.

---

## Quick Reference

| What you want        | What to type in Terminal                         |
| -------------------- | ------------------------------------------------ |
| Start the tool       | `cd crayo-local && bun run dev`                  |
| Stop the tool        | `Ctrl + C`                                       |
| Find your videos     | Open `crayo-local/data/renders/` in Finder       |
| Add background clips | Put `.mp4` files in `crayo-local/assets/stocks/` |
| Add background music | Put `.mp3` files in `crayo-local/assets/styles/` |
| Update the tool      | `git pull && bun install`                        |

---

## Need Help?

If something doesn't work:

1. Read the Troubleshooting section above
2. Search the error message online
3. Ask someone who knows computers to help

That's it. Go make some viral videos.
