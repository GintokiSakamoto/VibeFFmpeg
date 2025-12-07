import re
import os
from rapidfuzz import process, fuzz

"""
Command Parser for FFmpeg:
Interprets natural language commands, detects file types, and ensures compatibility.
"""

class CommandParser:
    def __init__(self, raw_text, input_file=None):
        self.text = raw_text.lower()
        self.input_file = input_file
        
        # 1. Basic Validation
        if not self.text:
            raise ValueError("⚠️ Command text is required.")
        if not self.input_file:
            raise ValueError("⚠️ Input file is required.")
        
        # We perform file checks here, but mock them in tests
        if not os.path.isfile(self.input_file):
            raise ValueError(f"⚠️ Input file '{self.input_file}' does not exist.")

        self.ext = os.path.splitext(self.input_file)[1][1:].lower()
        if not self.ext:
            self.ext = "mp4" # Default fallback

        # 2. Determine File Type (The Guard Logic)
        self.file_type = "unknown"
        if self.ext in ["jpg", "jpeg", "png", "bmp", "webp", "tiff"]:
            self.file_type = "image"
        elif self.ext in ["mp3", "wav", "aac", "flac", "m4a", "ogg", "opus"]:
            self.file_type = "audio"
        elif self.ext in ["mp4", "mkv", "avi", "mov", "webm", "flv", "gif"]:
            self.file_type = "video"
        
        print(f"📂 Detected Input Type: {self.file_type.upper()} ({self.ext})")

    def parse(self):
        """
        Matches command to action and verifies compatibility with file type.
        """
        
        # ⚡ PRIORITY CHECK: Explicit Resolution (e.g. "350x500")
        # Allowed for: Video and Images. Catches "350x500" even without "resize" keyword.
        if re.search(r"\d+\s*[xX]\s*\d+", self.text):
            if self.file_type == "audio":
                raise ValueError("⚠️ You cannot resize an audio file.")
            print(f"🧠 Detected Explicit Resolution in command.")
            return self._parse_compress_resize()

        # 3. Map phrases to (Function, Allowed_Types)
        actions = {
            # Extract Audio (Video only)
            "extract audio": (self._parse_extract_audio, ["video"]),
            "save audio": (self._parse_extract_audio, ["video"]),
            "get audio": (self._parse_extract_audio, ["video"]),
            "extract": (self._parse_extract_audio, ["video"]),
            
            # Convert (Works for all)
            "convert format": (self._parse_convert_format, ["video", "audio", "image"]),
            "change format": (self._parse_convert_format, ["video", "audio", "image"]),
            "turn into": (self._parse_convert_format, ["video", "audio", "image"]),
            "convert": (self._parse_convert_format, ["video", "audio", "image"]),
            
            # Trim (Video and Audio only)
            "trim video": (self._parse_trim_crop, ["video", "audio"]),
            "cut video": (self._parse_trim_crop, ["video", "audio"]),
            "shorten video": (self._parse_trim_crop, ["video", "audio"]),
            "clip video": (self._parse_trim_crop, ["video", "audio"]),
            "trim": (self._parse_trim_crop, ["video", "audio"]),
            "cut": (self._parse_trim_crop, ["video", "audio"]),
            
            # GIF (Video only)
            "make gif": (self._parse_gif_creation, ["video"]),
            "create gif": (self._parse_gif_creation, ["video"]),
            "turn into gif": (self._parse_gif_creation, ["video"]),
            "gif": (self._parse_gif_creation, ["video"]),

            # Resize/Compress (Video and Image)
            "compress video": (self._parse_compress_resize, ["video", "image"]),
            "shrink video": (self._parse_compress_resize, ["video", "image"]),
            "reduce size": (self._parse_compress_resize, ["video", "image"]),
            "compress": (self._parse_compress_resize, ["video", "image"]),
            
            "resize video": (self._parse_compress_resize, ["video", "image"]),
            "change resolution": (self._parse_compress_resize, ["video", "image"]),
            "resize": (self._parse_compress_resize, ["video", "image"]),
            
            "1080p": (self._parse_compress_resize, ["video"]),
            "720p": (self._parse_compress_resize, ["video"]),
            "480p": (self._parse_compress_resize, ["video"]),
            "360p": (self._parse_compress_resize, ["video"]),
            "240p": (self._parse_compress_resize, ["video"]),
            
            # Audio Ops (Video and Audio)
            "mute video": (self._parse_audio_manipulation, ["video", "audio"]),
            "remove audio": (self._parse_audio_manipulation, ["video", "audio"]),
            "silent video": (self._parse_audio_manipulation, ["video", "audio"]),
            "mute": (self._parse_audio_manipulation, ["video", "audio"]),
            
            "boost volume": (self._parse_audio_manipulation, ["video", "audio"]),
            "increase volume": (self._parse_audio_manipulation, ["video", "audio"]),
            "make louder": (self._parse_audio_manipulation, ["video", "audio"]),
            "louder": (self._parse_audio_manipulation, ["video", "audio"]),
            "volume": (self._parse_audio_manipulation, ["video", "audio"]),
        }

        # 4. Fuzzy Match
        best_match = process.extractOne(self.text, actions.keys(), scorer=fuzz.token_set_ratio)
        
        if best_match:
            matched_phrase, score, _ = best_match
            
            if score >= 80:
                action_func, allowed_types = actions[matched_phrase]
                
                # 🛡️ THE SECURITY CHECK
                if self.file_type not in allowed_types:
                    raise ValueError(f"⚠️ Action '{matched_phrase}' is NOT valid for {self.file_type} files.")
                
                print(f"🧠 Detected Intent: '{matched_phrase}' (Confidence: {score}%)")
                return action_func()
        
        raise ValueError(f"⚠️ Could not understand command '{self.text}'.")

    # --- Feature Handlers ---

    def _parse_extract_audio(self):
        target_ext = "mp3"
        supported = {"mp3": "libmp3lame", "wav": "pcm_s16le", "aac": "aac", "flac": "flac"}
        for fmt in supported:
            if fmt in self.text:
                target_ext = fmt
                break
        output_file = f"extracted_audio.{target_ext}"
        args = ["-vn", "-acodec", supported[target_ext]]
        return args, output_file

    def _parse_convert_format(self):
        formats = ["mp4", "mkv", "avi", "mov", "mp3", "wav", "flac", "jpg", "png"]
        target_ext = None
        for fmt in formats:
            if re.search(r'\b' + fmt + r'\b', self.text):
                target_ext = fmt
                break
        
        if not target_ext:
            raise ValueError("⚠️ Target format not found.")

        # Guard: Image -> Audio
        if self.file_type == "image" and target_ext in ["mp3", "wav", "flac"]:
            raise ValueError("⚠️ Cannot convert an image to an audio format.")

        filename_wo_ext = os.path.splitext(self.input_file)[0]
        output_file = f"{filename_wo_ext}_converted.{target_ext}"
        
        args = []
        if target_ext in ["mp3", "wav", "flac"]:
             args = ["-vn"]
        elif self.file_type == "image":
             args = [] 
        else:
             args = ["-c", "copy"] 
        return args, output_file

    def _parse_trim_crop(self):
        start_time = None
        duration = None
        end_time = None
        
        range_match = re.search(r"from\s+([\d:]+)\s+to\s+([\d:]+)", self.text)
        if range_match:
            start_time = range_match.group(1)
            end_time = range_match.group(2)
        
        first_match = re.search(r"first\s+(\d+)\s*sec", self.text)
        if first_match:
            start_time = "00:00:00"
            duration = first_match.group(1)
            
        if not start_time:
             raise ValueError("⚠️ Found 'trim' command but no time range.")

        output_file = f"trimmed_{self.input_file}"
        args = ["-ss", start_time]
        
        if duration:
            args += ["-t", duration]
        elif end_time:
            args += ["-to", end_time]
            
        if self.file_type == "video" or self.file_type == "audio":
             args += ["-c", "copy"]
             
        return args, output_file

    def _parse_gif_creation(self):
        filter_chain = "fps=15,scale=480:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse"
        args = ["-vf", filter_chain, "-loop", "0"]
        
        start_time = None
        duration = None
        end_time = None
        
        # Check for simple duration
        first_match = re.search(r"first\s+(\d+)\s*sec", self.text)
        if first_match:
            start_time = "00:00:00"
            duration = first_match.group(1)
        
        # Check range as well
        range_match = re.search(r"from\s+([\d:]+)\s+to\s+([\d:]+)", self.text)
        if range_match:
            start_time = range_match.group(1)
            end_time = range_match.group(2) # <--- FIXED: Captured End Time
            
        if start_time:
             args = ["-ss", start_time] + args
        else:
             args = ["-ss", "00:00:00", "-t", "5"] + args
             
        if duration:
             args += ["-t", duration]
        elif end_time:
             args += ["-to", end_time] # <--- FIXED: Added -to argument

        output_file = f"{os.path.splitext(self.input_file)[0]}.gif"
        return args, output_file

    def _parse_compress_resize(self):
        # 1. Custom Resolution Logic
        res_match = re.search(r"(\d+)\s*[xX]\s*(\d+)", self.text)
        scale_filter = None
        crf_value = "23" 

        if res_match:
            width = res_match.group(1)
            height = res_match.group(2)
            if "stretch" in self.text:
                scale_filter = f"scale={width}:{height}"
            else:
                scale_filter = f"scale=w={width}:h={height}:force_original_aspect_ratio=decrease"
        elif "1080p" in self.text:
            scale_filter = "scale=-2:1080"
        elif "720p" in self.text:
            scale_filter = "scale=-2:720"
        elif "480p" in self.text:
            scale_filter = "scale=-2:480"
        elif "360p" in self.text:
            scale_filter = "scale=-2:360"
        elif "240p" in self.text:
             scale_filter = "scale=-2:240"
        
        # Compression logic
        if any(k in self.text for k in ["compress", "shrink"]):
            crf_value = "28"

        args = []
        if self.file_type == "video":
            args = ["-c:v", "libx264", "-preset", "fast", "-crf", crf_value]
            if scale_filter:
                args += ["-vf", scale_filter]
        
        elif self.file_type == "image":
            if scale_filter:
                args += ["-vf", scale_filter]
        
        output_label = "resized" if scale_filter else "compressed" # <--- FIXED: Back to 'compressed'
        # FIXED: Enforce .mp4 for video ops to match test and ensure libx264 compatibility
        output_ext = "mp4" if self.file_type == "video" else self.ext
        output_file = f"{os.path.splitext(self.input_file)[0]}_{output_label}.{output_ext}"
        return args, output_file

    def _parse_audio_manipulation(self):
        args = []
        output_suffix = ""
        
        if any(k in self.text for k in ["mute", "remove", "silent"]):
            args = ["-an"]
            output_suffix = "muted"
        elif any(k in self.text for k in ["volume", "boost", "loud"]):
            args = ["-filter:a", "volume=1.5"]
            output_suffix = "boosted"
        
        if self.file_type == "video":
             args = ["-c:v", "copy"] + args
             
        output_file = f"{os.path.splitext(self.input_file)[0]}_{output_suffix}.{self.ext}"
        return args, output_file