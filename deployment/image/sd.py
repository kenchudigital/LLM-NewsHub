#!/usr/bin/env python3
"""
Stable Diffusion Image Generation Script

This script connects to the AUTOMATIC1111 Stable Diffusion WebUI API
to generate images from text prompts.

Usage:
    python sd.py "your text prompt here" "/path/to/output/image.png"

Requirements:
    - AUTOMATIC1111 Stable Diffusion WebUI running with --api flag
    - Python packages: requests, pillow
"""

import sys
import os
import requests
import base64
import json
from PIL import Image
from io import BytesIO
import argparse


class StableDiffusionGenerator:
    def __init__(self, api_url="http://localhost:7860"):
        """
        Initialize the Stable Diffusion generator.
        
        Args:
            api_url (str): URL of the Stable Diffusion WebUI API
        """
        self.api_url = api_url
        self.txt2img_url = f"{api_url}/sdapi/v1/txt2img"
        
    def check_api_connection(self):
        """Check if the API is accessible."""
        try:
            response = requests.get(f"{self.api_url}/sdapi/v1/options", timeout=10)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def generate_image(self, prompt, output_path, **kwargs):
        """
        Generate an image from a text prompt.
        
        Args:
            prompt (str): Text description of the desired image
            output_path (str): Path where the generated image will be saved
            **kwargs: Additional parameters for image generation
        
        Returns:
            bool: True if successful, False otherwise
        """
        # Default parameters
        params = {
            "prompt": prompt,
            "negative_prompt": kwargs.get("negative_prompt", "low quality, blurry, distorted"),
            "steps": kwargs.get("steps", 20),
            "sampler_name": kwargs.get("sampler_name", "DPM++ 2M Karras"),
            "cfg_scale": kwargs.get("cfg_scale", 7.5),
            "width": kwargs.get("width", 512),
            "height": kwargs.get("height", 512),
            "batch_size": 1,
            "n_iter": 1,
            "restore_faces": kwargs.get("restore_faces", False),
            "seed": kwargs.get("seed", -1)
        }
        
        print(f"Generating image with prompt: '{prompt}'")
        print(f"Parameters: {json.dumps(params, indent=2)}")
        
        try:
            # Make API request
            response = requests.post(self.txt2img_url, json=params, timeout=300)
            
            if response.status_code != 200:
                print(f"Error: API request failed with status code {response.status_code}")
                print(f"Response: {response.text}")
                return False
            
            # Parse response
            result = response.json()
            
            if "images" not in result or not result["images"]:
                print("Error: No images returned from API")
                return False
            
            # Decode and save image
            image_data = base64.b64decode(result["images"][0])
            image = Image.open(BytesIO(image_data))
            
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save image
            image.save(output_path)
            print(f"Image saved successfully to: {output_path}")
            
            # Print additional info if available
            if "info" in result:
                info = json.loads(result["info"])
                print(f"Generation info: Seed={info.get('seed', 'N/A')}, "
                      f"Steps={info.get('steps', 'N/A')}, "
                      f"CFG Scale={info.get('cfg_scale', 'N/A')}")
            
            return True
            
        except requests.exceptions.Timeout:
            print("Error: API request timed out. Image generation may take longer than expected.")
            return False
        except requests.exceptions.RequestException as e:
            print(f"Error: Network request failed: {e}")
            return False
        except Exception as e:
            print(f"Error: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description="Generate images using Stable Diffusion")
    parser.add_argument("prompt", help="Text prompt for image generation")
    parser.add_argument("output_path", help="Output path for the generated image")
    parser.add_argument("--api-url", default="http://localhost:7860", 
                       help="Stable Diffusion WebUI API URL (default: http://localhost:7860)")
    parser.add_argument("--steps", type=int, default=20, 
                       help="Number of sampling steps (default: 20)")
    parser.add_argument("--cfg-scale", type=float, default=7.5, 
                       help="CFG scale (default: 7.5)")
    parser.add_argument("--width", type=int, default=512, 
                       help="Image width (default: 600)")
    parser.add_argument("--height", type=int, default=512, 
                       help="Image height (default: 400)")
    parser.add_argument("--negative-prompt", default="low quality, blurry, distorted",
                       help="Negative prompt (default: 'low quality, blurry, distorted')")
    parser.add_argument("--sampler", default="DPM++ 2M Karras",
                       help="Sampling method (default: 'DPM++ 2M Karras')")
    parser.add_argument("--seed", type=int, default=-1,
                       help="Random seed (-1 for random, default: -1)")
    parser.add_argument("--restore-faces", action="store_true",
                       help="Enable face restoration")
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.prompt.strip():
        print("Error: Prompt cannot be empty")
        return 1
    
    if not args.output_path.strip():
        print("Error: Output path cannot be empty")
        return 1
    
    # Initialize generator
    generator = StableDiffusionGenerator(args.api_url)
    
    # Check API connection
    print("Checking API connection...")
    if not generator.check_api_connection():
        print(f"Error: Cannot connect to Stable Diffusion WebUI API at {args.api_url}")
        print("Please ensure:")
        print("1. Stable Diffusion WebUI is running")
        print("2. WebUI was started with --api --listen flags")
        print("3. The API URL is correct")
        return 1
    
    print("API connection successful!")
    
    # Generate image
    success = generator.generate_image(
        prompt=args.prompt,
        output_path=args.output_path,
        steps=args.steps,
        cfg_scale=args.cfg_scale,
        width=args.width,
        height=args.height,
        negative_prompt=args.negative_prompt,
        sampler_name=args.sampler,
        seed=args.seed,
        restore_faces=args.restore_faces
    )
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
