# PrintPal Python Client

The official Python client for the PrintPal 3D Generation API. Transform images into high-quality 3D models using AI.

**Website:** https://printpal.io  
**API Documentation:** https://printpal.io/api/documentation  
**API Dashboard:** https://printpal.io/api-keys

## Installation

```bash
pip install printpal
```

Or install from source:

```bash
git clone https://github.com/printpal-io/printpal-python.git
cd printpal-python
pip install -e .
```

## Quick Start

### 1. Get Your API Key

Sign up at [printpal.io](https://printpal.io) and get your API key from the [API Keys dashboard](https://printpal.io/api-keys).

### 2. Set Your API Key

Set your API key as an environment variable:

```bash
export PRINTPAL_API_KEY="pp_live_your_api_key_here"
```

Or pass it directly to the client:

```python
from printpal import PrintPalClient

client = PrintPalClient(api_key="pp_live_your_api_key_here")
```

### 3. Generate a 3D Model

```python
from printpal import PrintPalClient

# Initialize client
client = PrintPalClient()

# Generate a 3D model from an image (simplest method)
output_path = client.generate_and_download(
    image_path="my_image.png",
    output_path="my_model.stl"
)

print(f"3D model saved to: {output_path}")
```

## Features

- Image to 3D model generation
- Text to 3D model generation
- Multiple quality levels (default, high, ultra, super, superplus)
- Multiple output formats (STL, GLB, OBJ, PLY, FBX)
- Texture support for high-resolution models
- Async/polling-based workflow for long-running generations
- Credit balance and usage tracking
- Comprehensive error handling

## Usage Examples

### Basic Image to 3D

```python
from printpal import PrintPalClient, Quality, Format

client = PrintPalClient()

# One-liner: generate and download
path = client.generate_and_download("image.png", "model.stl")
```

### Step-by-Step Generation

For more control over the process:

```python
from printpal import PrintPalClient, Quality, Format

client = PrintPalClient()

# Step 1: Submit generation request
result = client.generate_from_image(
    image_path="my_image.png",
    quality=Quality.DEFAULT,
    format=Format.STL,
)

print(f"Generation UID: {result.generation_uid}")
print(f"Estimated time: {result.estimated_time_seconds} seconds")

# Step 2: Wait for completion
status = client.wait_for_completion(result.generation_uid)

# Step 3: Download the model
if status.is_completed:
    path = client.download(result.generation_uid, "my_model.stl")
    print(f"Downloaded to: {path}")
```

### High-Resolution Generation

Generate ultra-high-quality models with super resolution:

```python
from printpal import PrintPalClient, Quality, Format

client = PrintPalClient()

# Super resolution (768 cubed) - geometry only
result = client.generate_from_image(
    image_path="my_image.png",
    quality=Quality.SUPER,
    format=Format.STL,
)

# Super+ resolution (1024 cubed) - highest quality
result = client.generate_from_image(
    image_path="my_image.png",
    quality=Quality.SUPERPLUS,
    format=Format.STL,
)

# With textures (GLB or OBJ only)
result = client.generate_from_image(
    image_path="my_image.png",
    quality=Quality.SUPERPLUS_TEXTURE,
    format=Format.GLB,
)
```

### Text to 3D

Generate 3D models from text descriptions:

```python
from printpal import PrintPalClient, Quality, Format

client = PrintPalClient()

result = client.generate_from_prompt(
    prompt="a cute robot toy",
    quality=Quality.HIGH,
    format=Format.GLB,
)

path = client.wait_and_download(result.generation_uid, "robot.glb")
```

Note: Text to 3D is only available for default, high, and ultra quality levels.

### Check Credits

```python
from printpal import PrintPalClient

client = PrintPalClient()

# Get credit balance
credits = client.get_credits()
print(f"Available credits: {credits.credits}")

# Get pricing info
pricing = client.get_pricing()
for name, tier in pricing.credits.items():
    print(f"{name}: {tier.cost} credits")
```

### Async/Polling Workflow

For long-running generations or web applications:

```python
from printpal import PrintPalClient, Quality

client = PrintPalClient()

# Submit and get the UID
result = client.generate_from_image("image.png", quality=Quality.SUPER)
uid = result.generation_uid

# Save UID somewhere (database, file, etc.)
print(f"Started generation: {uid}")

# Later, check status
status = client.get_status(uid)
if status.is_completed:
    client.download(uid, "model.stl")
elif status.is_processing:
    print("Still processing...")
elif status.is_failed:
    print("Generation failed")
```

### With Progress Callback

```python
from printpal import PrintPalClient

client = PrintPalClient()

def on_status(status):
    print(f"Status: {status.status}")

result = client.generate_from_image("image.png")
path = client.wait_and_download(
    result.generation_uid,
    output_path="model.stl",
    callback=on_status,
)
```

### Context Manager

```python
from printpal import PrintPalClient

with PrintPalClient() as client:
    credits = client.get_credits()
    print(f"Credits: {credits.credits}")
```

## Quality Levels

| Quality | Resolution | Credits | Est. Time | Texture Support |
|---------|-----------|---------|-----------|-----------------|
| default | 256 cubed | 4 | 20 sec | No |
| high | 384 cubed | 6 | 30 sec | No |
| ultra | 512 cubed | 8 | 60 sec | No |
| super | 768 cubed | 20 | 3 min | No |
| super_texture | 768 cubed | 40 | 6 min | Yes |
| superplus | 1024 cubed | 30 | 4 min | No |
| superplus_texture | 1024 cubed | 50 | 12 min | Yes |

## Output Formats

| Format | Extension | Description | Availability |
|--------|-----------|-------------|--------------|
| STL | .stl | 3D printing format | All quality levels |
| GLB | .glb | Binary glTF (web/games) | All quality levels |
| OBJ | .obj | Wavefront OBJ | All quality levels |
| PLY | .ply | Polygon file format | default, high, ultra |
| FBX | .fbx | Autodesk FBX | super, superplus only |

Note: Texture generation (super_texture, superplus_texture) only supports GLB and OBJ formats. OBJ with texture returns as a ZIP archive containing the .obj, .mtl, and texture files.

## Error Handling

```python
from printpal import (
    PrintPalClient,
    AuthenticationError,
    InsufficientCreditsError,
    ValidationError,
    GenerationError,
    NotFoundError,
    RateLimitError,
)

client = PrintPalClient()

try:
    result = client.generate_from_image("image.png")
except AuthenticationError:
    print("Invalid API key")
except InsufficientCreditsError as e:
    print(f"Not enough credits. Need {e.credits_required}, have {e.credits_available}")
except ValidationError as e:
    print(f"Invalid parameters: {e}")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
except GenerationError as e:
    print(f"Generation failed: {e}")
except NotFoundError:
    print("Resource not found")
```

## API Reference

### PrintPalClient

The main client class for interacting with the PrintPal API.

#### Constructor

```python
PrintPalClient(
    api_key: str = None,      # API key (or set PRINTPAL_API_KEY env var)
    base_url: str = "https://printpal.io",  # API base URL
    timeout: int = 60,        # Request timeout in seconds
)
```

#### Methods

| Method | Description |
|--------|-------------|
| `get_credits()` | Get current credit balance |
| `get_pricing()` | Get API pricing information |
| `get_usage()` | Get API usage statistics |
| `health_check()` | Check API health status |
| `generate_from_image()` | Submit image for 3D generation |
| `generate_from_prompt()` | Submit text prompt for 3D generation |
| `get_status()` | Get generation status |
| `get_download_url()` | Get presigned download URL |
| `download()` | Download completed model |
| `wait_for_completion()` | Poll until generation completes |
| `wait_and_download()` | Wait and download in one call |
| `generate_and_download()` | Generate and download in one call |

### Quality Enum

```python
from printpal import Quality

Quality.DEFAULT        # 256 cubed, 4 credits
Quality.HIGH           # 384 cubed, 6 credits
Quality.ULTRA          # 512 cubed, 8 credits
Quality.SUPER          # 768 cubed, 20 credits
Quality.SUPER_TEXTURE  # 768 cubed + texture, 40 credits
Quality.SUPERPLUS      # 1024 cubed, 30 credits
Quality.SUPERPLUS_TEXTURE  # 1024 cubed + texture, 50 credits
```

### Format Enum

```python
from printpal import Format

Format.STL  # .stl
Format.GLB  # .glb
Format.OBJ  # .obj
Format.PLY  # .ply
Format.FBX  # .fbx (super/superplus only)
```

## Example Scripts

The `examples/` directory contains ready-to-run scripts:

| Script | Description |
|--------|-------------|
| `basic_generation.py` | Simple image to 3D |
| `high_quality_generation.py` | Super resolution generation |
| `batch_generation.py` | Process multiple images |
| `text_to_3d.py` | Generate from text prompts |
| `check_credits.py` | Check balance and pricing |
| `async_generation.py` | Submit/check/download workflow |

Run any example:

```bash
export PRINTPAL_API_KEY="pp_live_your_api_key_here"
python examples/basic_generation.py path/to/image.png
```

## Rate Limits

- 50 requests per minute per API key
- 10,000 requests per day per account
- 5 concurrent generations maximum

## Support

- Email: support@printpal.io
- Documentation: https://printpal.io/api/documentation
- Issues: https://github.com/printpal-io/printpal-python/issues

## License

MIT License. See [LICENSE](LICENSE) for details.
