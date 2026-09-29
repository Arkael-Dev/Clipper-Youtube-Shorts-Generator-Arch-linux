#!/usr/bin/env bash
set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

export DENO_INSTALL="${DENO_INSTALL:-$HOME/.deno}"
export PATH="$DENO_INSTALL/bin:$PATH"

echo "=========================================="
echo " AI YouTube Shorts Generator"
echo " Developer: Arkael-Dev"
echo " Arch Linux / DroidSpaces Installer"
echo "=========================================="
echo

echo "[1/8] Installing system dependencies..."

sudo pacman -S --needed --noconfirm \
    python \
    python-pip \
    ffmpeg \
    git \
    curl \
    unzip \
    fontconfig \
    ttf-dejavu \
    ollama

echo
echo "[2/8] Preparing Deno JavaScript runtime..."

if command -v deno >/dev/null 2>&1; then
    DENO_BIN="$(command -v deno)"
elif [ -x "$DENO_INSTALL/bin/deno" ]; then
    DENO_BIN="$DENO_INSTALL/bin/deno"
else
    echo "Deno not found. Installing local Deno runtime..."
    curl -fsSL https://deno.land/install.sh | sh
    DENO_BIN="$DENO_INSTALL/bin/deno"
fi

if [ ! -x "$DENO_BIN" ]; then
    echo "ERROR: Deno installation failed."
    exit 1
fi

export PATH="$(dirname "$DENO_BIN"):$PATH"

echo "Deno:"
"$DENO_BIN" --version | head -n 1

echo
echo "[3/8] Creating Python environment..."

if [ ! -d "$ROOT/venv" ]; then
    python -m venv "$ROOT/venv"
fi

source "$ROOT/venv/bin/activate"

echo
echo "[4/8] Installing Python dependencies..."

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -r requirements-local.txt
python -m pip install -U "yt-dlp[default]" yt-dlp-ejs

echo
echo "[5/8] Checking FFmpeg subtitle support..."

if ! ffmpeg -filters 2>/dev/null | grep -Eq '(^|[[:space:]])ass([[:space:]]|$)'; then
    echo "ERROR: FFmpeg was built without ASS/libass subtitle support."
    exit 1
fi

if ! fc-match "DejaVu Sans" >/dev/null 2>&1; then
    echo "ERROR: DejaVu Sans font is not available."
    exit 1
fi

echo "FFmpeg ASS/libass: OK"
echo "DejaVu Sans: OK"

echo
echo "[6/8] Preparing Ollama..."

if ! pgrep -x ollama >/dev/null 2>&1; then
    nohup ollama serve >/tmp/ollama.log 2>&1 &
    sleep 3
fi

if ! curl -fsS http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
    echo "WARNING: Ollama server did not respond."
    echo "Check /tmp/ollama.log if needed."
fi

echo
echo "[7/8] Installing Ollama model..."

ollama pull llama3.2:3b

echo
echo "[8/8] Creating configuration..."

if [ ! -f "$ROOT/.env" ]; then
cat > "$ROOT/.env" <<'ENV'
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://127.0.0.1:11434/v1
OLLAMA_MODEL=llama3.2:3b
LOCAL_WHISPER_MODEL=base
LOCAL_WHISPER_DEVICE=cpu
LOCAL_OUTPUT_DIR=output
ENV
fi

if [ -d "/storage/emulated/0" ]; then
    OUTPUT_DIR="/storage/emulated/0/CLIPPER"
else
    OUTPUT_DIR="$HOME/CLIPPER"
fi

mkdir -p "$OUTPUT_DIR"

chmod +x "$ROOT/run.sh" "$ROOT/install.sh"

echo
echo "=========================================="
echo " INSTALLATION COMPLETE"
echo "=========================================="
echo "Developer : Arkael-Dev"
echo "Output    : $OUTPUT_DIR"
echo "Deno      : $DENO_BIN"
echo "Ollama    : llama3.2:3b"
echo "Whisper   : faster-whisper / base"
echo "Font      : DejaVu Sans"
echo "=========================================="
echo
echo "Run:"
echo "  ./run.sh"
