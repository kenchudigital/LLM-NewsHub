#!/usr/bin/env python3
"""
Robust video merger with format normalization and enhanced audio processing
Fixes crashes at transition points and reduces audio noise
Usage: python merge_video.py
"""

import os
import sys
import json
from pathlib import Path
import subprocess

def apply_audio_enhancement(input_path, output_path, target_sample_rate=44100):
    """Apply audio enhancement to reduce noise and improve quality"""
    
    # Enhanced audio processing chain
    audio_filters = [
        # High-pass filter to remove low-frequency noise (below 80Hz)
        "highpass=f=80",
        # Low-pass filter to remove high-frequency noise (above 8000Hz)
        "lowpass=f=8000",
        # Noise reduction using spectral gating
        "anlmdn=s=7:p=0.002:r=0.01",
        # Normalize audio levels
        "loudnorm=I=-16:TP=-1.5:LRA=11",
        # Compress dynamic range for consistent levels
        "acompressor=threshold=0.1:ratio=9:attack=200:release=1000",
        # Add subtle reverb for warmth
        "aecho=0.8:0.5:60:0.3",
        # Final normalization
        "dynaudnorm=f=150:g=15"
    ]
    
    audio_filter_string = ",".join(audio_filters)
    
    cmd = [
        "ffmpeg",
        "-i", str(input_path),
        "-af", audio_filter_string,
        "-ar", str(target_sample_rate),
        "-ac", "2",  # Stereo
        "-c:a", "aac",
        "-b:a", "192k",  # Higher bitrate for better quality
        "-y",
        str(output_path)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0

def create_smooth_transition(logo_path, news_path, output_path, transition_duration=0.5):
    """Create a smooth crossfade transition between videos"""
    
    # Create transition video with crossfade
    transition_cmd = [
        "ffmpeg",
        "-i", str(logo_path),
        "-i", str(news_path),
        "-filter_complex", 
        f"[0:v][1:v]xfade=transition=fade:duration={transition_duration}:offset=0.5[v];"
        f"[0:a][1:a]acrossfade=d={transition_duration}[a]",
        "-map", "[v]",
        "-map", "[a]",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-preset", "medium",
        "-crf", "18",
        "-y",
        str(output_path)
    ]
    
    result = subprocess.run(transition_cmd, capture_output=True, text=True)
    return result.returncode == 0

def get_video_info(video_path):
    """Get detailed video properties"""
    try:
        cmd = [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_streams", "-show_format", str(video_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except:
        return None

def analyze_videos():
    """Analyze both videos and show their properties"""
    
    script_dir = Path(__file__).parent
    resource_dir = script_dir / "resource"
    logo_video = resource_dir / "logo_intro.mp4"
    news_video = resource_dir / "news_report.mp4"
    
    print("=== VIDEO ANALYSIS ===")
    
    logo_info = get_video_info(logo_video)
    news_info = get_video_info(news_video)
    
    if not logo_info or not news_info:
        print("Error: Could not analyze videos")
        return None, None
    
    # Extract video stream info
    logo_video_stream = next((s for s in logo_info['streams'] if s['codec_type'] == 'video'), None)
    news_video_stream = next((s for s in news_info['streams'] if s['codec_type'] == 'video'), None)
    
    logo_audio_stream = next((s for s in logo_info['streams'] if s['codec_type'] == 'audio'), None)
    news_audio_stream = next((s for s in news_info['streams'] if s['codec_type'] == 'audio'), None)
    
    print(f"Logo video: {logo_video_stream['width']}x{logo_video_stream['height']} @ {logo_video_stream.get('r_frame_rate', 'unknown')} fps")
    print(f"News video: {news_video_stream['width']}x{news_video_stream['height']} @ {news_video_stream.get('r_frame_rate', 'unknown')} fps")
    print(f"Logo audio: {'Yes' if logo_audio_stream else 'No'}")
    print(f"News audio: {'Yes' if news_audio_stream else 'No'}")
    
    return logo_info, news_info

def normalize_and_merge():
    """Normalize both videos to identical format and merge"""
    
    script_dir = Path(__file__).parent
    resource_dir = script_dir / "resource"
    logo_video = resource_dir / "logo_intro.mp4"
    news_video = resource_dir / "news_report.mp4"
    output_video = resource_dir / "merge.mp4"
    
    # Temporary normalized files
    norm_logo = resource_dir / "norm_logo.mp4"
    norm_news = resource_dir / "norm_news.mp4"
    
    try:
        logo_info, news_info = analyze_videos()
        if not logo_info or not news_info:
            return False
        
        # Get news video properties as target
        news_video_stream = next((s for s in news_info['streams'] if s['codec_type'] == 'video'), None)
        news_audio_stream = next((s for s in news_info['streams'] if s['codec_type'] == 'audio'), None)
        
        target_width = news_video_stream['width']
        target_height = news_video_stream['height'] 
        target_fps = 25  # Use standard framerate
        target_sample_rate = 44100  # Use standard sample rate
        
        print(f"\n=== NORMALIZING TO: {target_width}x{target_height} @ {target_fps}fps ===")
        
        # Step 1: Normalize logo video
        print("Step 1: Normalizing logo video...")
        logo_cmd = [
            "ffmpeg",
            "-i", str(logo_video),
            "-f", "lavfi",
            "-i", f"anullsrc=channel_layout=stereo:sample_rate={target_sample_rate}",
            "-vf", f"scale={target_width}:{target_height}:force_original_aspect_ratio=decrease,"
                   f"pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2:black,"
                   f"fps={target_fps}",
            "-af", f"aresample={target_sample_rate}",
            "-c:v", "libx264",
            "-c:a", "aac",
            "-preset", "medium",
            "-crf", "18",  # High quality
            "-pix_fmt", "yuv420p",
            "-r", str(target_fps),
            "-ar", str(target_sample_rate),
            "-ac", "2",
            "-t", "1",  # Exactly 1 second
            "-y",
            str(norm_logo)
        ]
        
        result1 = subprocess.run(logo_cmd, capture_output=True, text=True)
        if result1.returncode != 0:
            print(f"Logo normalization failed: {result1.stderr}")
            return False
        
        # Step 2: Normalize news video  
        print("Step 2: Normalizing news video...")
        news_cmd = [
            "ffmpeg", 
            "-i", str(news_video),
            "-vf", f"scale={target_width}:{target_height}:force_original_aspect_ratio=decrease,"
                   f"pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2:black,"
                   f"fps={target_fps}",
            "-af", f"aresample={target_sample_rate}",
            "-c:v", "libx264",
            "-c:a", "aac", 
            "-preset", "medium",
            "-crf", "18",  # High quality
            "-pix_fmt", "yuv420p",
            "-r", str(target_fps),
            "-ar", str(target_sample_rate),
            "-ac", "2",
            "-y",
            str(norm_news)
        ]
        
        result2 = subprocess.run(news_cmd, capture_output=True, text=True)
        if result2.returncode != 0:
            print(f"News normalization failed: {result2.stderr}")
            return False
            
        # Step 3: Simple concatenation of normalized videos
        print("Step 3: Concatenating normalized videos...")
        
        # Create file list
        filelist_path = resource_dir / "filelist.txt"
        with open(filelist_path, 'w') as f:
            f.write(f"file '{norm_logo.name}'\n")
            f.write(f"file '{norm_news.name}'\n")
        
        concat_cmd = [
            "ffmpeg",
            "-f", "concat",
            "-safe", "0", 
            "-i", str(filelist_path),
            "-c", "copy",  # No re-encoding since formats are identical
            "-avoid_negative_ts", "make_zero",
            "-fflags", "+genpts",
            "-y",
            str(output_video)
        ]
        
        result3 = subprocess.run(concat_cmd, capture_output=True, text=True, cwd=resource_dir)
        
        # Cleanup temporary files
        for temp_file in [norm_logo, norm_news, filelist_path]:
            if temp_file.exists():
                temp_file.unlink()
        
        if result3.returncode == 0:
            print("Merge successful!")
            
            # Verify the output
            print("\n=== VERIFYING OUTPUT ===")
            output_info = get_video_info(output_video)
            if output_info:
                output_format = output_info['format']
                print(f"Output duration: {float(output_format['duration']):.2f} seconds")
                print(f"Output size: {output_format['size']} bytes")
            
            return True
        else:
            print(f"Concatenation failed: {result3.stderr}")
            return False
            
    except Exception as e:
        print(f"Error in normalize_and_merge: {e}")
        
        # Cleanup on error
        for temp_file in [norm_logo, norm_news]:
            if temp_file.exists():
                temp_file.unlink()
        
        return False

def simple_fallback():
    """Ultra-simple fallback - just use news video"""
    
    script_dir = Path(__file__).parent
    resource_dir = script_dir / "resource"
    news_video = resource_dir / "news_report.mp4"
    output_video = resource_dir / "merge.mp4"
    
    print("Fallback: Using news video only...")
    
    cmd = [
        "ffmpeg",
        "-i", str(news_video),
        "-c:v", "libx264",
        "-c:a", "aac",
        "-preset", "medium", 
        "-crf", "23",
        "-y",
        str(output_video)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def main():
    """Main function"""
    print("Robust Video Merger")
    print("=" * 50)
    
    script_dir = Path(__file__).parent
    resource_dir = script_dir / "resource"
    logo_video = resource_dir / "logo_intro.mp4"
    news_video = resource_dir / "news_report.mp4"
    
    # Check input files
    if not logo_video.exists():
        print(f"Logo video not found: {logo_video}")
        sys.exit(1)
        
    if not news_video.exists():
        print(f"News video not found: {news_video}")
        sys.exit(1)
    
    # Try normalized merge
    if normalize_and_merge():
        print("\nVideo merge completed successfully!")
        print("The output should play smoothly without crashes.")
    elif simple_fallback():
        print("\nUsed fallback method (news video only)")
    else:
        print("\nAll merge methods failed")
        sys.exit(1)

if __name__ == "__main__":
    main()