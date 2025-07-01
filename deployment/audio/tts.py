import asyncio
import os
import argparse
import time
from pathlib import Path
import sys

# Try to import packages
try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

class SimpleNewsTTS:
    def __init__(self):
        # Professional female news voices (simplified)
        self.news_voices = {
            'us': 'en-US-AriaNeural',
            'gb': 'en-GB-SoniaNeural',
            'au': 'en-AU-NatashaNeural',
            'ca': 'en-CA-ClaraNeural',
        }
    
    def read_text_file(self, file_path: str) -> str:
        """Read text from file"""
        try:
            print(f"Reading file: {file_path}")
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read().strip()
            
            if not text:
                raise ValueError("Text file is empty")
            return text
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Text file not found: {file_path}")
        except Exception as e:
            raise Exception(f"Error reading file: {str(e)}")
    
    async def edge_tts_simple(self, text: str, output_file: str, voice: str):
        """Simple Edge TTS without complex SSML"""
        try:     
            # Simple communication without complex SSML
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_file)

            return True
            
        except Exception as e:
            return False
    
    def gtts_simple(self, text: str, output_file: str):
        """Simple Google TTS"""
        try:
            
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(output_file)
            
            print(f"Google TTS completed successfully")
            return True
            
        except Exception as e:
            return False
    
    def macos_say(self, text: str, output_file: str):
        """macOS say command"""
        try:
            # Escape quotes in text
            safe_text = text.replace('"', '\\"')
            
            # Create AIFF first, then convert to MP3
            temp_aiff = output_file.replace('.mp3', '.aiff')
            
            # Use say command with female voice
            say_command = f'say "{safe_text}" -o "{temp_aiff}" -v "Samantha"'
            result = os.system(say_command)
            
            if result != 0:
                raise Exception("say command failed")
            
            if os.path.exists(temp_aiff):
                # Try to convert to MP3 with ffmpeg
                if os.system('which ffmpeg > /dev/null 2>&1') == 0:
                    convert_command = f'ffmpeg -y -i "{temp_aiff}" "{output_file}" 2>/dev/null'
                    os.system(convert_command)
                    os.remove(temp_aiff)
                else:
                    # Just rename if no ffmpeg
                    os.rename(temp_aiff, output_file)
                
                print(f"macOS say completed successfully")
                return True
            
            return False
            
        except Exception as e:
            return False
    
    async def convert_file(self, input_file: str, output_file: str = None, voice_type: str = 'us'):
        """Convert text file to speech with fallbacks"""
        
        # Read the text
        text = self.read_text_file(input_file)
        
        # Generate output filename if not provided
        if output_file is None:
            input_path = Path(input_file)
            output_file = f"{input_path.stem}_audio.mp3"
        
        # Method 1: Try Edge TTS
        if EDGE_TTS_AVAILABLE:
            voice = self.news_voices.get(voice_type, self.news_voices['us'])
            success = await self.edge_tts_simple(text, output_file, voice)
            if success and os.path.exists(output_file) and os.path.getsize(output_file) > 1000:
                return output_file
            else:
                print("Edge TTS output seems invalid, trying fallback...")
        
        # Method 2: Try Google TTS
        if GTTS_AVAILABLE:
            success = self.gtts_simple(text, output_file)
            if success and os.path.exists(output_file) and os.path.getsize(output_file) > 1000:
                return output_file
            else:
                print("Google TTS output seems invalid, trying fallback...")
        
        # Method 3: Try macOS say
        if sys.platform == 'darwin':
            success = self.macos_say(text, output_file)
            if success and os.path.exists(output_file) and os.path.getsize(output_file) > 1000:
                return output_file
        
        raise Exception("All TTS methods failed or produced invalid output")
    
    def list_methods(self):
        """List available methods"""
        print("Available TTS Methods:")
        
        if EDGE_TTS_AVAILABLE:
            print("  Edge TTS (Microsoft)")
            for key, voice in self.news_voices.items():
                print(f"    --voice {key}: {voice}")
        else:
            print("  Edge TTS (install: pip install edge-tts)")
        
        if GTTS_AVAILABLE:
            print("  Google TTS")
        else:
            print("  Google TTS (install: pip install gtts)")
        
        if sys.platform == 'darwin':
            print("  macOS Say (Samantha voice)")
        else:
            print("  macOS Say (macOS only)")

def main():
    parser = argparse.ArgumentParser(
        description='Simple Text-to-Speech converter',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --speech sample_news.txt
  python main.py --speech news.txt --output my_audio.mp3
  python main.py --speech text.txt --voice gb
  python main.py --list-methods
        """
    )
    
    parser.add_argument('--speech', type=str, help='Input text file')
    parser.add_argument('--output', '-o', type=str, help='Output MP3 file')
    parser.add_argument('--voice', type=str, choices=['us', 'gb', 'au', 'ca'], default='us', help='Voice accent')
    parser.add_argument('--list-methods', action='store_true', help='List available methods')
    
    args = parser.parse_args()
    
    tts = SimpleNewsTTS()
    
    async def run():
        if args.list_methods:
            tts.list_methods()
            return
        
        if not args.speech:
            parser.print_help()
            print("\nError: --speech argument is required")
            return
        
        try:
            result_file = await tts.convert_file(args.speech, args.output, args.voice)
            
            if os.path.exists(result_file):
                
                # Test play the first few seconds to verify content
                if sys.platform == 'darwin':
                    print(f"Testing audio (first 3 seconds)...")
                    os.system(f'afplay "{result_file}" &')
                    await asyncio.sleep(3)
                    os.system('killall afplay 2>/dev/null')
 
        except Exception as e:
            print(f"\nError: {str(e)}")
    
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("\nCancelled by user")

if __name__ == "__main__":
    main()