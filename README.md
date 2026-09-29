# AI YouTube Shorts Generator — Arch Linux

A local AI-powered YouTube Shorts generator designed specifically for **Arch Linux Desktop**.

Automatically turns YouTube videos into vertical Shorts using local AI processing with **Ollama**, **Faster-Whisper**, and **FFmpeg**.

## Features

* 🎬 YouTube video → Shorts
* 🤖 Local AI highlight detection with Ollama
* 🧠 Ollama `llama3.2:3b`
* 🎤 Local speech-to-text with Faster-Whisper
* ✂️ Automatic highlight selection and video cutting
* 📱 Automatic 9:16 vertical reframing
* 💬 Automatic subtitles
* 🎨 Subtitle color selection
* 🌫️ Blurred subtitle background
* ⚡ 720×1280 or 1080×1920 output
* 🖥️ Modern Arch Linux GUI
* ⌨️ CLI mode also available
* 📦 Automatic dependency installation
* 📁 Automatic output to `~/CLIPPER`

## Requirements

* Arch Linux
* x86_64 or compatible Arch Linux system
* Internet connection for YouTube downloads
* Sufficient storage for video processing
* `sudo` access for system package installation

The installer automatically prepares the required software and Python environment.

## Installation

Clone the repository:

```bash
git clone https://github.com/Arkael-Dev/Clipper-Youtube-Shorts-Generator-Arch-linux.git
cd Clipper-Youtube-Shorts-Generator-Arch-linux
```

Run the automatic installer:

```bash
./install.sh
```

The installer prepares:

* Python virtual environment
* Python dependencies
* FFmpeg
* DejaVu Sans
* Deno JavaScript runtime
* yt-dlp
* yt-dlp-ejs
* Ollama
* Ollama `llama3.2:3b`
* Faster-Whisper
* Required local configuration

No manual Python dependency installation is required.

## GUI

Start the modern Arch Linux GUI:

```bash
./gui/run-gui.sh
```

The GUI provides:

* YouTube URL input
* Output resolution selection
* Subtitle color selection
* Custom subtitle color
* Generate Shorts button
* Real-time generator output
* Generation status
* Open `CLIPPER` output directory
* Clear generator log

The interface uses a modern **Tokyo Night-inspired** dark design.

## CLI

The command-line generator is still available:

```bash
./run.sh
```

Then select:

1. Output resolution
2. Subtitle color
3. YouTube URL

Example:

```text
https://youtu.be/VIDEO_ID
```

## Output

Generated Shorts are automatically copied to:

```text
~/CLIPPER
```

Example:

```text
~/CLIPPER/short_01.mp4
```

Output formats:

```text
720 × 1280
1080 × 1920
```

Aspect ratio:

```text
9:16
```

## Local AI

This project is designed to run AI processing locally.

Default Ollama configuration:

```text
Provider : Ollama
Model    : llama3.2:3b
API      : http://127.0.0.1:11434/v1
```

The project does not require OpenAI or other cloud AI APIs for the local generation pipeline.

## Processing Pipeline

The generator processes videos through the following pipeline:

```text
YouTube
   ↓
yt-dlp
   ↓
Video Download
   ↓
Faster-Whisper
   ↓
Transcript
   ↓
Ollama
   ↓
AI Highlight Detection
   ↓
Clip Selection
   ↓
9:16 Reframing
   ↓
Subtitles
   ↓
Blurred Subtitle Background
   ↓
FFmpeg
   ↓
~/CLIPPER
```

## Supported Input

Currently optimized for:

* YouTube videos
* YouTube URLs
* Local Ollama processing

Example:

```text
https://youtu.be/VIDEO_ID
```

## Project Structure

```text
Clipper-Youtube-Shorts-Generator-Arch-linux/
├── gui/
│   ├── app.py
│   └── run-gui.sh
├── shorts_generator/
│   ├── local/
│   │   ├── downloader.py
│   │   └── llm.py
│   ├── highlights.py
│   └── pipeline.py
├── install.sh
├── run.sh
├── main.py
├── requirements.txt
├── requirements-local.txt
├── README.md
└── LICENSE
```

## Credits

This project is an adaptation of:

https://github.com/SamurAIGPT/AI-Youtube-Shorts-Generator

Original authors and contributors remain credited according to the upstream project's license.

This repository is maintained by **Arkael-Dev** and adapted specifically for local AI video generation on Arch Linux Desktop.

## Repository

https://github.com/Arkael-Dev/Clipper-Youtube-Shorts-Generator-Arch-linux

## License

This project follows the applicable license of the original upstream project.

See the included `LICENSE` file and the upstream repository for the applicable license terms.

---

Maintained by **Arkael-Dev**
