# 🎵 VibeFFmpeg

> **FFmpeg made simple. Just type what you want.**

VibeFFmpeg is an intelligent, open-source Python wrapper that democratizes media processing. Instead of memorizing complex CLI flags, users interact with media files using natural language.

---

## 🚀 Features

* **🧠 Natural Language Parsing:** Understands commands like *"Extract audio as mp3"* or *"Trim first 10 seconds"*.
* **🛡️ Smart Validation:** Automatically detects codecs, file extensions, and prevents destructive overwrites.
* **🔌 Modular Architecture:** Built with decoupled command parsing and execution logic for easy extensibility.
* **⚡ Lightweight:** Zero heavy dependencies, designed for speed.

## 🛠️ Installation

* bash
# Clone the repository
git clone [https://github.com/gintokisakamoto/VibeFFmpeg.git](https://github.com/gintokisakamoto/VibeFFmpeg.git)
cd VibeFFmpeg

# Install dependencies
pip install -r requirements.txt

# Ensure FFmpeg is installed (Ubuntu/Debian)
sudo apt install ffmpeg


## 📖 Usage
# Trim a video
python main.py --input video.mp4 --cmd "Trim first 10 sec"

# Convert format
python main.py --input video.mov --cmd "Convert to mp4"

# Extract audio
python main.py --input lecture.mp4 --cmd "Extract audio as wav"


## 🏗️ Architecture
app/cmd_parser.py: Core NLP engine. Uses regex and pattern matching to translate intent into FFmpeg arguments.

app/wrapper.py: Safe execution layer handling subprocess calls and error management.

ui/cli.py: Command-line interface logic.

## 🤝 Contributing
Contributions are welcome!

1. Fork the repo.

2. Create a feature branch (git checkout -b feature/AmazingFeature).

3. Commit your changes (git commit -m 'Add some AmazingFeature').

4. Push to the branch.

5. Open a Pull Request.

Built with ❤️ by GintokiSakamoto
