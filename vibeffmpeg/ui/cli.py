import argparse
import sys
# Note: These imports might change slightly if you restructure folders (see Step 4)
from vibeffmpeg.app.cmd_parser import CommandParser
from vibeffmpeg.app.wrapper import run_ffmpeg_cmd
def run_cli():
    parser = argparse.ArgumentParser(description="VibeFFmpeg CLI")
    
    # Change 1: Add '-i' alias to input
    parser.add_argument('-i', '--input', required=True, help="Input file path")
    
    # Change 2: Make 'cmd' a positional argument (no -- flags needed)
    parser.add_argument('cmd', help="Command to execute (e.g. 'Convert to 350x512')")
    
    args = parser.parse_args()

    try:
        cmd_parser = CommandParser(args.cmd, args.input)
        ffmpeg_args, output_file = cmd_parser.parse()

        if not ffmpeg_args:
            print("❌ Invalid command or unsupported format.")
            return

        full_cmd = ["ffmpeg", "-i", args.input] + ffmpeg_args + [output_file]
        run_ffmpeg_cmd(full_cmd)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_cli()