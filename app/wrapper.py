import subprocess

def run_ffmpeg_cmd(cmd_args):
    try:
        print(f"Running command: {' '.join(cmd_args)}")
        subprocess.run(cmd_args, check=True, text=True)
        print(f"✅ Done! Output saved as {cmd_args[-1]}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        return False