import re

class CommandParser:
    def __init__(self, raw_text):
        self.text = raw_text.lower()

    def parse(self):
        #default extension and codec
        ext = 'mp3'
        codec = 'libmp3lame'

        #detect extension and codec
        ext_match = re.search(r"\.(mp3|aac|wav|flac)", self.text)
        if ext_match:
            ext = ext_match.group(1)
        else:
            # If no extension is found, default to mp3
            ext = 'mp3'

        #Map extension to codec
        codec_map = {
            'mp3': 'libmp3lame',
            'aac': 'aac',
            'wav': 'pcm_s16le',
            'flac': 'flac'
        }

        if "extract" in self.text and "audio" in self.text:
            if ext not in codec_map:
                raise ValueError(f"Unsupported audio format: {ext}")
            
            output_file = f"extracted_audio.{ext}"
            args = [
                "-vn",  # No video
                "-acodec", codec_map[ext]]  # Use the codec based on extension
            
            return args, output_file

        return None, None  # If no valid command is found, return None