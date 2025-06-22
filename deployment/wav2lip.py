import os
import sys
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
import asyncio

# Add the deployment directory to Python path
deployment_dir = Path(__file__).parent
sys.path.append(str(deployment_dir))

from audio.tts import SimpleNewsTTS

def validate_date(date_str):
    """Validate date format YYYY-MM-DD"""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def process_audio_files(date_str: str):
    """Process audio files for a given date and generate videos using Wav2Lip"""
    # Setup paths
    base_dir = Path('data/output')
    audio_dir = base_dir / 'audio' / date_str
    video_dir = base_dir / 'video' / date_str
    
    # Create video output directory if it doesn't exist
    video_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if audio directory exists
    if not audio_dir.exists():
        raise FileNotFoundError(f"Audio directory not found: {audio_dir}")
    
    # Get all audio files
    audio_files = list(audio_dir.glob('group_*.mp3'))
    
    if not audio_files:
        raise FileNotFoundError(f"No audio files found in {audio_dir}")
    
    print(f"Found {len(audio_files)} audio files to process")
    
    # Path to Wav2Lip inference script
    wav2lip_script = Path('deployment/Wav2Lip/inference.py')
    if not wav2lip_script.exists():
        raise FileNotFoundError(f"Wav2Lip inference script not found at {wav2lip_script}")
    
    # Path to face video
    face_video = Path('deployment/Wav2Lip/samples/face.mp4')
    if not face_video.exists():
        raise FileNotFoundError(f"Face video not found at {face_video}")
    
    async def process_file(audio_file):
        try:
            # Extract group_id from filename
            group_id = audio_file.stem.replace('group_', '')
            
            # Generate output video path
            output_video = video_dir / f"group_{group_id}.mp4"
            
            print(f"\n🎯 Processing group {group_id}")
            print(f"🎵 Audio file: {audio_file}")
            
            # Run Wav2Lip inference
            cmd = [
                'python', str(wav2lip_script),
                '--face', str(face_video),
                '--audio', str(audio_file),
                '--outfile', str(output_video),
                '--pads', '0 20 0 0',  # Add some padding
                '--resize_factor', '1',  # Keep original size
                '--no_smooth'  # Disable smoothing for better lip sync
            ]
            
            print(f"🎬 Running Wav2Lip with command: {' '.join(cmd)}")
            
            # Run the command
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                print(f"Generated video: {output_video}")
            else:
                print(f"Error generating video for {audio_file.name}")
                print(f"Error output: {stderr.decode()}")
            
        except Exception as e:
            print(f"Error processing {audio_file.name}: {str(e)}")
    
    async def process_all_files():
        tasks = [process_file(f) for f in audio_files]
        await asyncio.gather(*tasks)
    
    # Run the processing
    asyncio.run(process_all_files())

def main():
    parser = argparse.ArgumentParser(
        description='Generate videos from audio files using Wav2Lip',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
  python wav2lip.py --date 2024-03-20
        """
    )
    
    parser.add_argument('--date', type=str, required=True,
                      help='Date in YYYY-MM-DD format')
    
    args = parser.parse_args()
    
    if not validate_date(args.date):
        print("Error: Invalid date format. Please use YYYY-MM-DD")
        return
    
    try:
        process_audio_files(args.date)
        print("\n✨ All files processed successfully!")
    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    main()
