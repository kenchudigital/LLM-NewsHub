#!/usr/bin/env python3
"""
Script to create animated AI News Sense logo intro
Usage: python add_logo.py
Output: resource/logo_intro.mp4 (1 second animated logo)
"""

import os
import sys
from pathlib import Path
import subprocess

def create_animated_logo():
    """Create 1-second animated logo intro"""
    
    script_dir = Path(__file__).parent
    resource_dir = script_dir / "resource"
    resource_dir.mkdir(exist_ok=True)
    logo_video = resource_dir / "logo_intro.mp4"
    
    print("Creating animated AI News Sense logo...")
    
    ffmpeg_cmd = [
        "ffmpeg",
        "-f", "lavfi",
        "-i", "color=c=black:size=1920x1080:duration=1",
        "-vf",
        "drawtext=text='AI News Sense':"
        "fontsize=100:"
        "fontcolor=white:"
        "x=(w-text_w)/2:"
        "y=(h-text_h)/2-30:"
        "alpha='if(lt(t,0.2),t/0.2,if(gt(t,0.8),(1-t)/0.2,1))',"
        
        "drawtext=text='Your AI-Powered News Source':"
        "fontsize=40:"
        "fontcolor=0x00BFFF:"
        "x=(w-text_w)/2:"
        "y=(h-text_h)/2+80:"
        "alpha='if(lt(t,0.4),0,if(gt(t,0.8),(1-t)/0.2,1))'"
        ,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-t", "1",
        "-y",
        str(logo_video)
    ]
    
    try:
        subprocess.run(ffmpeg_cmd, check=True, capture_output=True, text=True)
        print(f"Logo video created: {logo_video}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error creating logo: {e}")
        return False

def create_basic_logo():
    """Create basic logo that definitely works"""
    
    script_dir = Path(__file__).parent
    resource_dir = script_dir / "resource"
    resource_dir.mkdir(exist_ok=True)
    logo_video = resource_dir / "logo_intro.mp4"
    
    print("Creating basic logo...")
    
    ffmpeg_cmd = [
        "ffmpeg",
        "-f", "lavfi",
        "-i", "color=c=black:size=1920x1080:duration=1",
        "-vf",
        "drawtext=text='AI News Sense':"
        "fontsize=80:"
        "fontcolor=white:"
        "x=(w-text_w)/2:"
        "y=(h-text_h)/2",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-y",
        str(logo_video)
    ]
    
    try:
        subprocess.run(ffmpeg_cmd, check=True, capture_output=True)
        print(f"Basic logo created: {logo_video}")
        return True
    except Exception as e:
        print(f"Basic logo failed: {e}")
        return False

def main():
    """Main function"""
    print("AI News Sense Logo Creator")
    
    if create_animated_logo():
        print("Logo creation complete")
    elif create_basic_logo():
        print("Basic logo creation complete")
    else:
        print("Logo creation failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
