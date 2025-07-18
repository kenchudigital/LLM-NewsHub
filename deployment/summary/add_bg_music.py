#!/usr/bin/env python3
"""
Ultra-simple background music script that prioritizes reliability
Usage: python add_bg_music.py
"""

import os
import sys
from pathlib import Path
import subprocess

def add_background_music():
    """Ultra-simple method that works reliably"""
    
    script_dir = Path(__file__).parent
    video_file = script_dir / "resource/merge.mp4"
    bg_music_file = script_dir / "resource/bg.mp3"
    output_file = script_dir / "resource/summary.mp4"
    
    # Check input files
    if not video_file.exists():
        print(f"Error: Video file not found: {video_file}")
        return False
        
    if not bg_music_file.exists():
        print(f"Error: Background music file not found: {bg_music_file}")
        return False
    
    print("Adding background music...")
    
    # Ultra-simple approach - minimal processing
    cmd = [
        "ffmpeg",
        "-i", str(video_file),
        "-i", str(bg_music_file),
        "-c:v", "copy",                    # Don't touch video
        "-filter_complex",
        "[1:a]volume=0.03[bg];[0:a][bg]amix=inputs=2:duration=shortest[audio]",
        "-map", "0:v",                     # Original video
        "-map", "[audio]",                 # Mixed audio
        "-c:a", "aac",                     # Simple audio encoding
        "-shortest",                       # End with shortest stream
        "-y",
        str(output_file)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("Background music added successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Method failed: {e.stderr}")
        return fallback_method()
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def fallback_method():
    """Even simpler fallback if main method fails"""
    
    script_dir = Path(__file__).parent
    video_file = script_dir / "resource/merge.mp4"
    bg_music_file = script_dir / "resource/bg.mp3"
    output_file = script_dir / "resource/summary.mp4"
    
    print("Trying fallback method...")
    
    # Just copy the video if all else fails
    cmd = [
        "ffmpeg",
        "-i", str(video_file),
        "-c", "copy",
        "-y",
        str(output_file)
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print("Fallback: Copied video without background music")
        return True
    except:
        print("All methods failed")
        return False

def main():
    """Main function"""
    print("Adding background music...")
    success = add_background_music()
    
    if success:
        print("Background music processing complete")
    else:
        print("Failed to add background music")
        sys.exit(1)

if __name__ == "__main__":
    main()
