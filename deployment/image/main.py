#!/usr/bin/env python3
import os
import json
import argparse
from datetime import datetime
from sd import StableDiffusionGenerator

def ensure_directory_exists(directory):
    """Create directory if it doesn't exist."""
    os.makedirs(directory, exist_ok=True)

def process_group_files(date_str):
    """Process all group JSON files for the given date."""
    # Setup paths
    article_dir = os.path.join('data', 'output', 'article', date_str)
    image_dir = os.path.join('data', 'output', 'image', date_str)
    
    # Create image output directory
    ensure_directory_exists(image_dir)
    
    # Initialize Stable Diffusion generator with explicit API URL
    generator = StableDiffusionGenerator(api_url="http://127.0.0.1:7860")
    
    # Check API connection
    print("Checking connection to Stable Diffusion WebUI API at http://127.0.0.1:7860...")
    if not generator.check_api_connection():
        print("Error: Cannot connect to Stable Diffusion WebUI API")
        print("Please ensure:")
        print("1. Stable Diffusion WebUI is running")
        print("2. WebUI was started with --api flag")
        print("3. You can access the WebUI at http://127.0.0.1:7860")
        return False
    
    print("Successfully connected to Stable Diffusion WebUI API!")
    
    # Get all group JSON files (excluding group_categories.json)
    json_files = [f for f in os.listdir(article_dir) 
                 if f.startswith('group_') and f.endswith('.json') 
                 and f != 'group_categories.json']
    
    success_count = 0
    total_files = len(json_files)
    
    for json_file in json_files:
        try:
            # Extract group_id from filename
            group_id = json_file.replace('group_', '').replace('.json', '')
            
            # Read JSON file
            with open(os.path.join(article_dir, json_file), 'r') as f:
                data = json.load(f)
            
            # Get cover image prompt
            prompt = data.get('cover_image_prompt')
            if not prompt:
                print(f"Warning: No cover_image_prompt found in {json_file}")
                continue
            
            # Generate output path
            output_path = os.path.join(image_dir, f'group_{group_id}.jpg')
            
            # Generate image
            print(f"\nProcessing group {group_id}...")
            print(f"Prompt: {prompt}")
            
            success = generator.generate_image(
                prompt=prompt,
                output_path=output_path,
                width=1024,  # Using larger size for better quality
                height=576,  # 16:9 aspect ratio
                steps=30,    # More steps for better quality
                cfg_scale=7.5,
                sampler_name="DPM++ 2M Karras"
            )
            
            if success:
                success_count += 1
                print(f"Successfully generated image for group {group_id}")
            else:
                print(f"Failed to generate image for group {group_id}")
                
        except Exception as e:
            print(f"Error processing {json_file}: {str(e)}")
            continue
    
    print(f"\nSummary: Generated {success_count} out of {total_files} images")
    return success_count > 0

def main():
    parser = argparse.ArgumentParser(description="Generate cover images for article groups")
    parser.add_argument("--date", required=True, help="Date in YYYY-MM-DD format")
    parser.add_argument("--api-url", default="http://127.0.0.1:7860",
                       help="Stable Diffusion WebUI API URL (default: http://127.0.0.1:7860)")
    
    args = parser.parse_args()
    
    # Validate date format
    try:
        datetime.strptime(args.date, "%Y-%m-%d")
    except ValueError:
        print("Error: Invalid date format. Please use YYYY-MM-DD")
        return 1
    
    success = process_group_files(args.date)
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())

