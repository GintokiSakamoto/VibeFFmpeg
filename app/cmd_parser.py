import re
import os

"""
Command Parser for FFmpeg:
Interpret natural language commands to generate FFmpeg command arguments.
Intentionally designed to handle several ffmpeg commands in a natural language way.
Supports:
- Extracting audio from video files
- Converting formats
- Cropping or trimming audio/video files
"""

class CommandParser:
    def __init__(self, raw_text, input_file=None):
        self.text = raw_text.lower()
        self.input_file = input_file.lower() if input_file else None
        self.ext = os.path.splitext(self.input_file)[1][1:] if self.input_file else None
        if not self.input_file:
            raise ValueError("⚠️ Input file is required. Please provide a valid input file path or name.")
        if not self.text:
            raise ValueError("⚠️ Command text is required. Please provide a valid command to parse.")
        if not os.path.isfile(self.input_file):
            raise ValueError(f"⚠️ Input file '{self.input_file}' does not exist. Please provide a valid file path.")
        if not self.ext:
            raise ValueError("⚠️ Input file extension is required. Please provide a valid input file with an extension.")

    def parse(self):
        if "extract audio" in self.text:
            return self._parse_extract_audio()
        elif any(keyword in self.text for keyword in ["convert format", "change audio format", "convert video format", "convert audio format", "change video format", "convert to", "change to"]):
            return self._parse_convert_format()
        elif any(keyword in self.text for keyword in ["crop", "trim", "cut"]):
            return self._parse_trim_crop()
        else:
            raise ValueError("⚠️ Unsupported command or format. Please provide a valid command.")

    def _parse_extract_audio(self):
        #default output format is mp3
        ext = "mp3"
        codec_map = {
            "mp3": "libmp3lame",
            "wav": "pcm_s16le",
            "aac": "aac",
            "flac": "flac",
            "ogg": "libvorbis",
            "m4a": "aac",
            "opus": "libopus"
        }

        #detect extension
        ext_match = re.search(r'\b(mp3|wav|aac|flac|ogg|m4a|opus)\b', self.text)
        if ext_match:
            ext = ext_match.group(1)
        
        if ext not in codec_map:
            raise ValueError(f"⚠️ Unsupported audio format: {ext}. Supported formats are: {', '.join(codec_map.keys())}.")
        
        output_file = f"extracted_audio.{ext}"
        args = [
            "-vn",
            "-acodec", codec_map[ext],
            output_file
        ]

        return args, output_file
        

    def _parse_convert_format(self):
        #find the target format in the text
        format_match = re.search(r'\b(mp4|mp3|m4a|wav|flac|aac|ogg|opus|avi|mkv|mov)\b', self.text)
        if not format_match:
            raise ValueError("⚠️ No valid target format found in the command. Please specify a valid format (e.g., mp4, mp3, wav, etc.).")
            return None, None
        target_ext = format_match.group(0)
        filename_wo_ext = os.path.splitext(self.input_file)[0]
        output_file = f"{filename_wo_ext}_converted.{target_ext}"
        args = ["-c", "copy"] # Copy codec to avoid re-encoding
        return args, output_file

    def _parse_trim_crop(self):
        #Handle patterns: "from X to Y", "start at X", "end at Y", "cut from X to Y", "first N seconds", "last N seconds"
        start_time = None
        end_time = None
        duration = None

        #from X to Y
        range_match = re.search(r"from\s+([\d:]+)\s+to\s+([\d:]+)", self.text)
        if range_match:
            start_time = range_match.group(1)
            end_time = range_match.group(2)

        #first N seconds
        first_match = re.search(r"first\s+(\d+)\s*sec", self.text)
        if first_match:
            duration = first_match.group(1)
            start_time = "00:00:00"

        #last N seconds, etc are not implemented yet

        if not (range_match or first_match):
            raise ValueError("⚠️ Unsupported crop/trim command. Please specify a valid time range or duration.")
            return None, None
        
        #fallback default
        ext = self.ext if self.ext else "mp4"  # Default to mp4 if no extension is provided

        output_file = f"trimmed_{self.input_file}"

        args = []
        if start_time:
            args += ["-ss", start_time]
        if end_time:
            args += ["-to", end_time]
        elif duration:
            args += ["-t", duration]
        
        args += ["-c", "copy"]

        return args, output_file
        