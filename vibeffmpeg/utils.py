import shutil
import platform
import sys

def check_ffmpeg_installed():
    """
    Checks if ffmpeg is available. If not, prints OS-specific
    installation instructions and exits.
    """
    if shutil.which("ffmpeg"):
        return True

    print("❌ Error: FFmpeg is not installed or not in your PATH.")
    print("\nTo install FFmpeg, please run the following command for your OS:")

    os_name = platform.system()

    if os_name == "Windows":
        print("  👉 Windows (using Winget): winget install ffmpeg")
        print("  👉 Windows (using Chocolatey): choco install ffmpeg")
    elif os_name == "Darwin":  # macOS
        print("  👉 macOS (using Homebrew): brew install ffmpeg")
    elif os_name == "Linux":
        print("  👉 Ubuntu/Debian: sudo apt update && sudo apt install ffmpeg")
        print("  👉 Fedora: sudo dnf install ffmpeg")
        print("  👉 Arch: sudo pacman -S ffmpeg")
    else:
        print("  👉 Please visit: https://ffmpeg.org/download.html")

    sys.exit(1)