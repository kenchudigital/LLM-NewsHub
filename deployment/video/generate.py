# https://github.com/MiniMax-AI/MiniMax-MCP
import requests
import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import dotenv
dotenv.load_dotenv()

# Your MiniMax API key
API_KEY = os.getenv('MINIMAX_API_KEY')

# Debug: Print API key (first few characters) to verify it's loaded
if API_KEY:
    print(f"API Key loaded (first 8 chars): {API_KEY[:8]}...")
else:
    print("Warning: API Key not found in environment variables!")

# Endpoint URL for video generation
url = 'https://api.minimax.io/v1/video_generation'

# The text prompt describing the video you want to generate
prompt_text = """
A professional beautiful  western young female news reporter in a formal suit stands confidently behind a long glass desk, delivering a report with steady gestures. 
The modern studio backdrop displays "AI NEWS" in bold, glowing letters, illuminated by bright, even lighting. 
The camera remains motionless, capturing a straight-on medium shot that emphasizes the reporter's consistent posture and the clean, minimalist aesthetic of the set.
"""

# Request headers including authorization and content type
headers = {
    'authorization': f'Bearer {API_KEY}',  # Changed to match demo format
    'Content-Type': 'application/json'
}

# Debug: Print the actual header being sent (first few characters)
print(f"Authorization header (first 8 chars): {headers['authorization'][:8] if headers['authorization'] else 'None'}...")

# Request body with required parameters
data = {
    "model": "T2V-01-Director",
    "prompt": prompt_text,
    "prompt_optimizer": True  # Optional, defaults to True
}

# Send POST request to MiniMax video generation API
response = requests.post(url, headers=headers, json=data)

# Check if request was successful
if response.status_code == 200:
    result = response.json()
    if result.get('base_resp', {}).get('status_code') == 0:
        task_id = result.get('task_id')
        print(f"Video generation task submitted successfully. Task ID: {task_id}")
    else:
        print(f"API returned error: {result.get('base_resp', {}).get('status_msg')}")
else:
    print(f"Request failed with status code {response.status_code}: {response.text}")
