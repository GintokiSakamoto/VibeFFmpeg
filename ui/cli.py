import argparse
from app.cmd_parser import CommandParser
from app.wrapper import run_ffmpeg_cmd

def run_cli():
    parser = argparse.ArgumentParser(description="VibeFFmpeg CLI")
    parser.add_argument('--input', required=True, help="Input file path or just filename if in the same directory")
    parser.add_argument('--cmd', required=True, help="Command to execute (e.g., 'extract audio', 'convert video')")
    args = parser.parse_args()

    ffmpeg_args, output_file = CommandParser(args.cmd).parse()
    if not ffmpeg_args:
        print("Invalid command or unsupported format.")
        return

    full_cmd = ["ffmpeg", "-i", args.input] + ffmpeg_args + [output_file]
    run_ffmpeg_cmd(full_cmd)