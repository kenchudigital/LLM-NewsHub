#!/usr/bin/env python3
"""
Script to add background music to a video with reduced volume
Usage: python add_bg.py
"""

import os
import sys
from pathlib import Path
import subprocess

def add_background_music():
    """Add background music to video with reduced volume"""
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    
    # Define file paths
    video_file = script_dir / "resource/merge.mp4"
    bg_music_file = script_dir / "resource/bg.mp3"
    output_file = script_dir / "resource/summary.mp4"
    
    # Check if input files exist
    if not video_file.exists():
        print(f"Error: Video file not found: {video_file}")
        return False
        
    if not bg_music_file.exists():
        print(f"Error: Background music file not found: {bg_music_file}")
        return False
    
    print(f"Input video: {video_file}")
    print(f"Background music: {bg_music_file}")
    print(f"Output file: {output_file}")
    
    # FFmpeg command to combine video with background music
    # -i: input files
    # -filter_complex: complex audio filter
    # [1:a]volume=0.1: reduce background music volume to 10%
    # amix=inputs=2: mix two audio streams
    # -c:v copy: copy video stream without re-encoding (faster)
    # -c:a aac: encode audio as AAC
    # -shortest: finish when the shortest input ends
    # -y: overwrite output file if it exists
    
    ffmpeg_cmd = [
        "ffmpeg",
        "-i", str(video_file),           # Input video with original audio
        "-i", str(bg_music_file),        # Input background music
        "-filter_complex",
        "[1:a]volume=0.1[bg]; [0:a][bg]amix=inputs=2:duration=first[audio]",
        "-map", "0:v",                   # Map video from first input
        "-map", "[audio]",               # Map mixed audio
        "-c:v", "copy",                  # Copy video codec (no re-encoding)
        "-c:a", "aac",                   # Encode audio as AAC
        "-shortest",                     # End when shortest input ends
        "-y",                            # Overwrite output file
        str(output_file)
    ]
    
    print("Running FFmpeg command...")
    print(" ".join(ffmpeg_cmd))
    
    # Execute the command
    try:
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, check=True)
        print("Successfully created video with background music!")
        print(f"Output saved to: {output_file}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error running FFmpeg:")
        print(f"Return code: {e.returncode}")
        print(f"Error output: {e.stderr}")
        return False
        
    except FileNotFoundError:
        print(" Error: FFmpeg not found. Please install FFmpeg:")
        print(" macOS: brew install ffmpeg")
        print(" Ubuntu/Debian: sudo apt-get install ffmpeg")
        print(" Windows: Download from https://ffmpeg.org/download.html")
        return False

def main():
    """Main function"""
    print("Adding background music to video...")
    success = add_background_music()
    
    if success:
        print("\nDone! Your video with background music is ready.")
    else:
        print("\nFailed to create video with background music.")
        sys.exit(1)

if __name__ == "__main__":
    main()
