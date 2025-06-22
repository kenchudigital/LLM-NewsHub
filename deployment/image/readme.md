# Stable Diffusion Image Generation

This guide will help you set up and use Stable Diffusion locally to generate images from text prompts.

## Prerequisites

- Python 3.8 or higher
- CUDA-compatible GPU (recommended) or CPU
- At least 8GB of RAM (16GB+ recommended for GPU usage)

## Installation

### 1. Install AUTOMATIC1111 Stable Diffusion WebUI

First, install the popular AUTOMATIC1111 Stable Diffusion WebUI:

```bash
# Clone the repository
git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git
cd stable-diffusion-webui

# For Linux/Mac
./webui.sh

# For Windows
webui-user.bat
```

**Alternative: Install via pip (for API usage)**

If you prefer to use Stable Diffusion programmatically without the web interface:

```bash
pip install diffusers transformers accelerate torch torchvision
```

### 2. Launch Stable Diffusion WebUI with API

To use the Python script (`sd.py`), you need to launch the WebUI with API enabled:

```bash
./webui.sh --api --listen
```

This will:
- Enable the API endpoint
- Make it accessible from other applications
- Default URL: `http://localhost:7860`

### 3. Install Python Dependencies

Install the required Python packages for the `sd.py` script:

```bash
pip install requests pillow
```

## Using the sd.py Script

The `sd.py` script allows you to generate images programmatically using text prompts.

### Basic Usage

```bash
python sd.py "a beautiful sunset over mountains" ./output/sunset.png
```

### Parameters

- **text_prompt** (required): The text description of the image you want to generate
- **output_path** (required): The file path where the generated image will be saved

### Examples

```bash
# Generate a landscape
python sd.py "a serene lake surrounded by autumn trees" ./images/lake.png

# Generate a portrait
python sd.py "a professional headshot of a person in business attire" ./portraits/headshot.jpg

# Generate abstract art
python sd.py "abstract digital art with vibrant colors and geometric shapes" ./art/abstract.png

# Generate animals
python sd.py "a majestic lion in the African savanna during golden hour" ./animals/lion.png
```

## Configuration

### WebUI Settings

1. **Model Selection**: Choose your preferred model in the WebUI interface
2. **Sampling Method**: DPM++ 2M Karras (recommended)
3. **Steps**: 20-50 (higher = better quality, slower generation)
4. **CFG Scale**: 7-12 (how closely to follow the prompt)

### Script Configuration

You can modify the `sd.py` script to adjust default parameters:

- Image dimensions (default: 512x512)
- Sampling steps (default: 20)
- CFG scale (default: 7.5)
- Sampling method

## Troubleshooting

### Common Issues

1. **"Connection refused" error**
   - Ensure WebUI is running with `--api --listen` flags
   - Check that the URL in `sd.py` matches your WebUI address

2. **Out of memory errors**
   - Reduce image dimensions
   - Lower the number of sampling steps
   - Use `--medvram` or `--lowvram` flags when launching WebUI

3. **Slow generation**
   - Ensure you're using a CUDA-compatible GPU
   - Consider using fewer sampling steps
   - Use efficient sampling methods like DPM++ 2M Karras

### Performance Tips

- **GPU Acceleration**: Ensure CUDA is properly installed
- **Model Management**: Keep frequently used models in the WebUI models folder
- **Batch Processing**: Generate multiple images by calling the script multiple times
- **Memory Optimization**: Use `--opt-split-attention` flag for lower memory usage

## Advanced Usage

### Custom Models

1. Download models from [Hugging Face](https://huggingface.co/models) or [Civitai](https://civitai.com/)
2. Place `.safetensors` or `.ckpt` files in `stable-diffusion-webui/models/Stable-diffusion/`
3. Restart WebUI and select the model from the dropdown

### LoRA and Embeddings

- **LoRA**: Place in `stable-diffusion-webui/models/Lora/`
- **Embeddings**: Place in `stable-diffusion-webui/embeddings/`
- **VAE**: Place in `stable-diffusion-webui/models/VAE/`

## API Documentation

For advanced users, the full API documentation is available at:
`http://localhost:7860/docs` (when WebUI is running with --api)

## Support

- [AUTOMATIC1111 GitHub](https://github.com/AUTOMATIC1111/stable-diffusion-webui)
- [Stable Diffusion Community](https://www.reddit.com/r/StableDiffusion/)
- [Official Documentation](https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki)