#!/usr/bin/env bash
set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log()  { echo -e "${GREEN}✓${NC} $1"; }
warn() { echo -e "${YELLOW}⚠${NC} $1"; }
err()  { echo -e "${RED}✗${NC} $1"; }

# --- Bun ---
if command -v bun &>/dev/null; then
  log "Bun $(bun --version) already installed"
else
  log "Installing Bun..."
  curl -fsSL https://bun.sh/install | bash
  export PATH="$HOME/.bun/bin:$PATH"
  log "Bun $(bun --version) installed"
fi

# --- FFmpeg ---
if command -v ffmpeg &>/dev/null; then
  log "FFmpeg already installed"
elif command -v brew &>/dev/null; then
  log "Installing FFmpeg via Homebrew..."
  brew install ffmpeg
  log "FFmpeg installed"
else
  err "FFmpeg not found. Install it manually: https://ffmpeg.org/download.html"
  exit 1
fi

# --- yt-dlp ---
if command -v yt-dlp &>/dev/null; then
  log "yt-dlp already installed"
elif command -v pip3 &>/dev/null; then
  log "Installing yt-dlp..."
  pip3 install --user yt-dlp
  log "yt-dlp installed"
else
  warn "yt-dlp not found — YouTube/TikTok downloads won't work. Install manually: pip3 install yt-dlp"
fi

# --- Python packages ---
if command -v pip3 &>/dev/null; then
  log "Installing Python packages..."
  pip3 install --user edge-tts opencv-python openai-whisper rembg 2>/dev/null || {
    warn "Some Python packages failed — install manually:"
    warn "  pip3 install edge-tts opencv-python openai-whisper rembg"
  }
  log "Python packages installed"
else
  warn "pip3 not found — Python packages not installed. Install Python 3 first."
fi

# --- Bun dependencies ---
log "Installing Bun workspace dependencies..."
bun install
log "Dependencies installed"

# --- YuNet face detection model ---
MODEL_DIR="packages/ai/src"
MODEL_FILE="$MODEL_DIR/face_detection_yunet_2023mar.onnx"
if [ ! -f "$MODEL_FILE" ]; then
  log "Downloading YuNet face detection model..."
  curl -fsSL -o "$MODEL_FILE" \
    "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx"
  log "YuNet model downloaded"
else
  log "YuNet model already present"
fi

# --- Assets directories ---
mkdir -p assets/stocks assets/styles assets/fonts assets/voices
log "Asset directories ready"

echo ""
echo -e "${GREEN}Setup complete!${NC}"
echo ""
echo "Run:  bun run dev"
echo "Then: open http://localhost:3000"
