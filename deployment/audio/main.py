import os
import json
import asyncio
import argparse
from pathlib import Path
from datetime import datetime
from tts import SimpleNewsTTS

def validate_date(date_str):
    """Validate date format YYYY-MM-DD"""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def process_json_files(date_str: str):
    """Process JSON files for a given date and generate audio files"""
    # Setup paths
    base_dir = Path('data/output')
    article_dir = base_dir / 'article' / date_str
    audio_dir = base_dir / 'audio' / date_str
    
    # Create audio output directory if it doesn't exist
    audio_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if article directory exists
    if not article_dir.exists():
        raise FileNotFoundError(f"Article directory not found: {article_dir}")
    
    # Get all group JSON files (excluding group_categories.json)
    json_files = [f for f in article_dir.glob('group_*.json') if f.name != 'group_categories.json']
    
    if not json_files:
        raise FileNotFoundError(f"No group JSON files found in {article_dir}")
    
    print(f"📁 Found {len(json_files)} group files to process")
    
    # Initialize TTS
    tts = SimpleNewsTTS()
    
    async def process_file(json_file):
        try:
            # Extract group_id from filename
            group_id = json_file.stem.replace('group_', '')
            
            # Read JSON file
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Get summary_speech
            if 'summary_speech' not in data:
                print(f"⚠️ No summary_speech found in {json_file.name}")
                return
            
            summary_text = data['summary_speech']
            
            # Generate output path
            output_file = audio_dir / f"group_{group_id}.mp3"
            
            print(f"\n🎯 Processing group {group_id}")
            print(f"📝 Text length: {len(summary_text)} characters")
            
            # Create a temporary text file with the summary
            temp_text_file = audio_dir / f"{group_id}_temp.txt"
            with open(temp_text_file, 'w', encoding='utf-8') as f:
                f.write(summary_text)
            
            try:
                # Convert to speech using the temporary text file
                await tts.convert_file(
                    input_file=str(temp_text_file),
                    output_file=str(output_file),
                    voice_type='us'  # Using US voice
                )
                print(f"✅ Generated audio: {output_file}")
            finally:
                # Clean up temporary file
                if temp_text_file.exists():
                    temp_text_file.unlink()
            
        except Exception as e:
            print(f"❌ Error processing {json_file.name}: {str(e)}")
    
    async def process_all_files():
        tasks = [process_file(f) for f in json_files]
        await asyncio.gather(*tasks)
    
    # Run the processing
    asyncio.run(process_all_files())

def main():
    parser = argparse.ArgumentParser(
        description='Generate audio files from article summaries',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
  python main.py --date 2024-03-20
        """
    )
    
    parser.add_argument('--date', type=str, required=True,
                      help='Date in YYYY-MM-DD format')
    
    args = parser.parse_args()
    
    if not validate_date(args.date):
        print("❌ Error: Invalid date format. Please use YYYY-MM-DD")
        return
    
    try:
        process_json_files(args.date)
        print("\n✨ All files processed successfully!")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
