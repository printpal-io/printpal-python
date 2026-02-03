"""
Constants for the PrintPal API client.
"""

from enum import Enum


class Quality(str, Enum):
    """Available quality levels for 3D generation."""
    
    DEFAULT = "default"
    """Default quality (256 cubed resolution). Fast generation, 4 credits."""
    
    HIGH = "high"
    """High quality (384 cubed resolution). Better details, 6 credits."""
    
    ULTRA = "ultra"
    """Ultra quality (512 cubed resolution). Maximum quality, 8 credits."""
    
    SUPER = "super"
    """Super resolution (768 cubed resolution). High-res geometry only, 20 credits."""
    
    SUPER_TEXTURE = "super_texture"
    """Super resolution with texture (768 cubed resolution). Includes textures, 40 credits."""
    
    SUPERPLUS = "superplus"
    """Super+ resolution (1024 cubed resolution). Highest resolution geometry, 30 credits."""
    
    SUPERPLUS_TEXTURE = "superplus_texture"
    """Super+ resolution with texture (1024 cubed resolution). Best quality with textures, 50 credits."""


class Format(str, Enum):
    """Available output formats for 3D models."""
    
    STL = "stl"
    """STL format. Universal 3D printing format."""
    
    GLB = "glb"
    """GLB format. Binary glTF, good for web and games."""
    
    OBJ = "obj"
    """OBJ format. Widely supported 3D format."""
    
    PLY = "ply"
    """PLY format. Polygon file format."""
    
    FBX = "fbx"
    """FBX format. Available only for super/superplus quality."""


# Credit costs per quality level
CREDIT_COSTS = {
    Quality.DEFAULT: 4,
    Quality.HIGH: 6,
    Quality.ULTRA: 8,
    Quality.SUPER: 20,
    Quality.SUPER_TEXTURE: 40,
    Quality.SUPERPLUS: 30,
    Quality.SUPERPLUS_TEXTURE: 50,
}

# Estimated generation times in seconds (typical values, can vary)
ESTIMATED_TIMES = {
    Quality.DEFAULT: 20,
    Quality.HIGH: 30,
    Quality.ULTRA: 50,
    Quality.SUPER: 120,
    Quality.SUPER_TEXTURE: 300,
    Quality.SUPERPLUS: 180,
    Quality.SUPERPLUS_TEXTURE: 500,
}

# Recommended timeout values in seconds (includes buffer for variability)
GENERATION_TIMEOUTS = {
    Quality.DEFAULT: 120,        # 2 minutes
    Quality.HIGH: 180,           # 3 minutes
    Quality.ULTRA: 300,          # 5 minutes
    Quality.SUPER: 360,          # 6 minutes
    Quality.SUPER_TEXTURE: 600,  # 10 minutes
    Quality.SUPERPLUS: 480,      # 8 minutes
    Quality.SUPERPLUS_TEXTURE: 600,  # 10 minutes
}

# Resolution descriptions
RESOLUTIONS = {
    Quality.DEFAULT: "256 cubed",
    Quality.HIGH: "384 cubed",
    Quality.ULTRA: "512 cubed",
    Quality.SUPER: "768 cubed",
    Quality.SUPER_TEXTURE: "768 cubed",
    Quality.SUPERPLUS: "1024 cubed",
    Quality.SUPERPLUS_TEXTURE: "1024 cubed",
}

# Valid formats per quality level
VALID_FORMATS = {
    Quality.DEFAULT: [Format.STL, Format.GLB, Format.OBJ, Format.PLY],
    Quality.HIGH: [Format.STL, Format.GLB, Format.OBJ, Format.PLY],
    Quality.ULTRA: [Format.STL, Format.GLB, Format.OBJ, Format.PLY],
    Quality.SUPER: [Format.STL, Format.GLB, Format.OBJ, Format.FBX],
    Quality.SUPER_TEXTURE: [Format.GLB, Format.OBJ],
    Quality.SUPERPLUS: [Format.STL, Format.GLB, Format.OBJ, Format.FBX],
    Quality.SUPERPLUS_TEXTURE: [Format.GLB, Format.OBJ],
}

# API base URL
DEFAULT_BASE_URL = "https://printpal.io"

# Rate limits
RATE_LIMIT_PER_MINUTE = 50
RATE_LIMIT_PER_DAY = 10000
MAX_CONCURRENT_GENERATIONS = 5

# Timeouts
DEFAULT_TIMEOUT = 60
UPLOAD_TIMEOUT = 120
DOWNLOAD_TIMEOUT = 300
