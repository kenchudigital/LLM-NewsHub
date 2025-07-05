# Update the merge_video.py script to use the resource directory
#!/usr/bin/env python3
"""
Script to merge logo intro and news report videos
Usage: python merge_video.py
Input: resource/logo_intro.mp4 + resource/news_report.mp4
Output: resource/merge.mp4
"""

import os
import sys
from pathlib import Path
import subprocess

def check_input_files():
    """Check if input files exist"""
    
    script_dir = Path(__file__).parent
    resource_dir = script_dir / "resource"
    logo_video = resource_dir / "logo_intro.mp4"
    news_video = resource_dir / "news_report.mp4"
    
    if not logo_video.exists():
        print(f"Error: Logo video not found: {logo_video}")
        return False, None, None
    
    if not news_video.exists():
        print(f"Error: News video not found: {news_video}")
        return False, None, None
    
    return True, logo_video, news_video

def get_video_info(video_path):
    """Get video information"""
    
    try:
        cmd = [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", "-show_streams", str(video_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        import json
        info = json.loads(result.stdout)
        
        video_stream = None
        audio_stream = None
        
        for stream in info['streams']:
            if stream['codec_type'] == 'video':
                video_stream = stream
            elif stream['codec_type'] == 'audio':
                audio_stream = stream
        
        if video_stream:
            return {
                'width': video_stream.get('width'),
                'height': video_stream.get('height'),
                'fps': eval(video_stream.get('r_frame_rate', '30/1')),
                'duration': float(info['format'].get('duration', 0)),
                'has_audio': audio_stream is not None,
                'sample_rate': audio_stream.get('sample_rate') if audio_stream else None
            }
        
    except Exception:
        pass
    
    return None

def normalize_videos():
    """Normalize both videos to have identical properties"""
    
    script_dir = Path(__file__).parent
    resource_dir = script_dir / "resource"
    logo_video = resource_dir / "logo_intro.mp4"
    news_video = resource_dir / "news_report.mp4"
    
    logo_info = get_video_info(logo_video)
    news_info = get_video_info(news_video)
    
    if not logo_info or not news_info:
        return False, None, None
    
    target_width = news_info['width']
    target_height = news_info['height']
    target_fps = news_info['fps']
    target_sample_rate = news_info['sample_rate'] or 44100
    
    normalized_logo = resource_dir / "normalized_logo.mp4"
    logo_cmd = [
        "ffmpeg",
        "-i", str(logo_video),
        "-f", "lavfi",
        "-i", f"anullsrc=channel_layout=stereo:sample_rate={target_sample_rate}",
        "-filter_complex",
        f"[0:v]scale={target_width}:{target_height}:force_original_aspect_ratio=decrease,"
        f"pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2:black,"
        f"fps={target_fps},format=yuv420p[v]",
        "-map", "[v]",
        "-map", "1:a",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-preset", "medium",
        "-crf", "23",
        "-t", str(logo_info['duration']),
        "-y",
        str(normalized_logo)
    ]
    
    normalized_news = resource_dir / "normalized_news.mp4"
    news_cmd = [
        "ffmpeg",
        "-i", str(news_video),
        "-vf", f"scale={target_width}:{target_height}:force_original_aspect_ratio=decrease,"
               f"pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2:black,"
               f"fps={target_fps},format=yuv420p",
        "-af", f"aresample={target_sample_rate}",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-preset", "medium",
        "-crf", "23",
        "-y",
        str(normalized_news)
    ]
    
    try:
        subprocess.run(logo_cmd, check=True, capture_output=True, text=True)
        subprocess.run(news_cmd, check=True, capture_output=True, text=True)
        return True, normalized_logo, normalized_news
    except subprocess.CalledProcessError:
        return False, None, None

def merge_normalized_videos(logo_path, news_path):
    """Merge the normalized videos"""
    
    resource_dir = logo_path.parent
    output_video = resource_dir / "merge.mp4"
    
    filelist_path = resource_dir / "concat_list.txt"
    with open(filelist_path, 'w') as f:
        f.write(f"file '{logo_path.name}'\n")
        f.write(f"file '{news_path.name}'\n")
    
    concat_cmd = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", str(filelist_path),
        "-c", "copy",
        "-avoid_negative_ts", "make_zero",
        "-fflags", "+genpts",
        "-y",
        str(output_video)
    ]
    
    try:
        subprocess.run(concat_cmd, check=True, capture_output=True, text=True, cwd=resource_dir)
        
        filelist_path.unlink()
        logo_path.unlink()
        news_path.unlink()
        
        return True, output_video
    except subprocess.CalledProcessError:
        if filelist_path.exists():
            filelist_path.unlink()
        if logo_path.exists():
            logo_path.unlink()
        if news_path.exists():
            news_path.unlink()
        return False, None

def merge_with_re_encoding():
    """Fallback method: merge with full re-encoding"""
    
    script_dir = Path(__file__).parent
    resource_dir = script_dir / "resource"
    logo_video = resource_dir / "logo_intro.mp4"
    news_video = resource_dir / "news_report.mp4"
    output_video = resource_dir / "merge.mp4"
    
    news_info = get_video_info(news_video)
    if not news_info:
        return False, None
    
    target_width = news_info['width']
    target_height = news_info['height']
    target_fps = news_info['fps']
    
    merge_cmd = [
        "ffmpeg",
        "-i", str(logo_video),
        "-i", str(news_video),
        "-f", "lavfi",
        "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
        "-filter_complex",
        f"[0:v]scale={target_width}:{target_height}:force_original_aspect_ratio=decrease,"
        f"pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2:black,"
        f"fps={target_fps}[logo_v];"
        f"[1:v]scale={target_width}:{target_height}:force_original_aspect_ratio=decrease,"
        f"pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2:black,"
        f"fps={target_fps}[news_v];"
        "[logo_v][2:a][news_v][1:a]concat=n=2:v=1:a=1[outv][outa]",
        "-map", "[outv]",
        "-map", "[outa]",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-preset", "medium",
        "-crf", "23",
        "-y",
        str(output_video)
    ]
    
    try:
        subprocess.run(merge_cmd, check=True, capture_output=True, text=True)
        return True, output_video
    except subprocess.CalledProcessError:
        return False, None

def main():
    """Main function"""
    print("Merging videos...")
    
    files_ok, logo_video, news_video = check_input_files()
    if not files_ok:
        sys.exit(1)
    
    success, logo_norm, news_norm = normalize_videos()
    if success:
        success, output_path = merge_normalized_videos(logo_norm, news_norm)
        if success and output_path and output_path.exists():
            print(f"Success: {output_path}")
            return
    
    success, output_path = merge_with_re_encoding()
    if success and output_path and output_path.exists():
        print(f"Success: {output_path}")
        return
    
    print("Error: All merge methods failed")
    sys.exit(1)

if __name__ == "__main__":
    main()