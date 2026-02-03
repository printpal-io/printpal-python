"""
Data models for the PrintPal API client.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from printpal.constants import Quality, Format


@dataclass
class GenerationRequest:
    """Request parameters for 3D model generation."""
    
    quality: Quality = Quality.DEFAULT
    """Quality level for generation."""
    
    format: Format = Format.STL
    """Output format for the 3D model. Defaults to STL for 3D printing."""
    
    num_inference_steps: int = 20
    """Number of inference steps (1-50). Higher values may improve quality but take longer.
    Not used for super/superplus quality levels."""
    
    guidance_scale: float = 5.0
    """Guidance scale (0.5-10.0). Controls how closely the output matches the input.
    Not used for super/superplus quality levels."""
    
    octree_resolution: int = 256
    """Octree resolution (128, 256, or 512). Higher values produce more detailed geometry.
    Not used for super/superplus quality levels."""
    
    def validate(self):
        """Validate request parameters."""
        from printpal.constants import VALID_FORMATS
        from printpal.exceptions import ValidationError
        
        # Validate quality
        if not isinstance(self.quality, Quality):
            try:
                self.quality = Quality(self.quality)
            except ValueError:
                raise ValidationError(f"Invalid quality: {self.quality}")
        
        # Validate format
        if not isinstance(self.format, Format):
            try:
                self.format = Format(self.format)
            except ValueError:
                raise ValidationError(f"Invalid format: {self.format}")
        
        # Check format is valid for quality
        valid_formats = VALID_FORMATS.get(self.quality, [])
        if self.format not in valid_formats:
            raise ValidationError(
                f"Format '{self.format.value}' is not valid for quality '{self.quality.value}'. "
                f"Valid formats: {[f.value for f in valid_formats]}"
            )
        
        # Validate parameters for non-super quality
        if self.quality not in [
            Quality.SUPER,
            Quality.SUPER_TEXTURE,
            Quality.SUPERPLUS,
            Quality.SUPERPLUS_TEXTURE,
        ]:
            if not 1 <= self.num_inference_steps <= 50:
                raise ValidationError("num_inference_steps must be between 1 and 50")
            if not 0.5 <= self.guidance_scale <= 10.0:
                raise ValidationError("guidance_scale must be between 0.5 and 10.0")
            if self.octree_resolution not in [128, 256, 512]:
                raise ValidationError("octree_resolution must be 128, 256, or 512")


@dataclass
class GenerationStatus:
    """Status of a 3D generation request."""
    
    generation_uid: str
    """Unique identifier for this generation."""
    
    status: str
    """Current status: 'pending', 'processing', 'completed', or 'failed'."""
    
    created_at: Optional[datetime] = None
    """When the generation was created."""
    
    completed_at: Optional[datetime] = None
    """When the generation was completed (if applicable)."""
    
    quality: Optional[str] = None
    """Quality level used for this generation."""
    
    format: Optional[str] = None
    """Output format for this generation."""
    
    resolution: Optional[str] = None
    """Resolution used for this generation."""
    
    download_url: Optional[str] = None
    """URL to download the completed model (if completed)."""
    
    external_state: Optional[str] = None
    """State from external processing API (for super resolution)."""
    
    @property
    def is_completed(self) -> bool:
        """Check if generation is completed."""
        return self.status == "completed"
    
    @property
    def is_failed(self) -> bool:
        """Check if generation has failed."""
        return self.status == "failed"
    
    @property
    def is_processing(self) -> bool:
        """Check if generation is still processing."""
        return self.status in ["pending", "processing"]
    
    @classmethod
    def from_response(cls, data: dict) -> "GenerationStatus":
        """Create GenerationStatus from API response."""
        created_at = None
        completed_at = None
        
        if data.get("created_at"):
            try:
                created_at = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass
        
        if data.get("completed_at"):
            try:
                completed_at = datetime.fromisoformat(data["completed_at"].replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass
        
        return cls(
            generation_uid=data.get("generation_uid", ""),
            status=data.get("status", "unknown"),
            created_at=created_at,
            completed_at=completed_at,
            quality=data.get("quality"),
            format=data.get("format"),
            resolution=data.get("resolution"),
            download_url=data.get("download_url"),
            external_state=data.get("external_state"),
        )


@dataclass
class GenerationResult:
    """Result of a completed 3D generation."""
    
    generation_uid: str
    """Unique identifier for this generation."""
    
    status: str
    """Status of the generation."""
    
    quality: str
    """Quality level used."""
    
    credits_used: int
    """Number of credits consumed."""
    
    credits_remaining: int
    """Credits remaining after this generation."""
    
    estimated_time_seconds: int
    """Estimated time for generation in seconds."""
    
    status_url: str
    """URL to check generation status."""
    
    download_url: str
    """URL to download the model when complete."""
    
    resolution: Optional[str] = None
    """Resolution used (for super resolution)."""
    
    has_texture: bool = False
    """Whether the model includes textures."""
    
    @classmethod
    def from_response(cls, data: dict) -> "GenerationResult":
        """Create GenerationResult from API response."""
        return cls(
            generation_uid=data.get("generation_uid", ""),
            status=data.get("status", ""),
            quality=data.get("quality", ""),
            credits_used=data.get("credits_used", 0),
            credits_remaining=data.get("credits_remaining", 0),
            estimated_time_seconds=data.get("estimated_time_seconds", 0),
            status_url=data.get("status_url", ""),
            download_url=data.get("download_url", ""),
            resolution=data.get("resolution"),
            has_texture=data.get("has_texture", False),
        )


@dataclass
class CreditsInfo:
    """Information about user credits."""
    
    credits: int
    """Current credit balance."""
    
    user_id: int
    """User ID."""
    
    username: str
    """Username."""
    
    @classmethod
    def from_response(cls, data: dict) -> "CreditsInfo":
        """Create CreditsInfo from API response."""
        return cls(
            credits=data.get("credits", 0),
            user_id=data.get("user_id", 0),
            username=data.get("username", ""),
        )


@dataclass
class PricingTier:
    """Pricing information for a quality tier."""
    
    cost: int
    """Credit cost for this tier."""
    
    description: str
    """Description of this tier."""
    
    resolution: str
    """Resolution for this tier."""
    
    estimated_time_seconds: int
    """Estimated generation time in seconds."""


@dataclass
class PricingInfo:
    """Pricing information for the API."""
    
    credits: Dict[str, PricingTier]
    """Credit costs per generation type."""
    
    supported_formats: List[str]
    """List of supported output formats."""
    
    rate_limits: Dict[str, int]
    """Rate limit information."""
    
    @classmethod
    def from_response(cls, data: dict) -> "PricingInfo":
        """Create PricingInfo from API response."""
        credits = {}
        for name, info in data.get("credits", {}).items():
            credits[name] = PricingTier(
                cost=info.get("cost", 0),
                description=info.get("description", ""),
                resolution=info.get("resolution", ""),
                estimated_time_seconds=info.get("estimated_time_seconds", 0),
            )
        
        return cls(
            credits=credits,
            supported_formats=data.get("supported_formats", []),
            rate_limits=data.get("rate_limits", {}),
        )


@dataclass
class APIKeyInfo:
    """Information about an API key."""
    
    name: str
    """Name of the API key."""
    
    total_requests: int
    """Total requests made with this key."""
    
    credits_used: int
    """Total credits used by this key."""
    
    last_used: Optional[datetime] = None
    """When this key was last used."""


@dataclass
class UsageStats:
    """API usage statistics."""
    
    api_key: APIKeyInfo
    """Information about the current API key."""
    
    credits_remaining: int
    """Credits remaining for the user."""
    
    recent_requests: List[Dict[str, Any]] = field(default_factory=list)
    """List of recent API requests."""
    
    @classmethod
    def from_response(cls, data: dict) -> "UsageStats":
        """Create UsageStats from API response."""
        api_key_data = data.get("api_key", {})
        last_used = None
        if api_key_data.get("last_used"):
            try:
                last_used = datetime.fromisoformat(
                    api_key_data["last_used"].replace("Z", "+00:00")
                )
            except (ValueError, AttributeError):
                pass
        
        return cls(
            api_key=APIKeyInfo(
                name=api_key_data.get("name", ""),
                total_requests=api_key_data.get("total_requests", 0),
                credits_used=api_key_data.get("credits_used", 0),
                last_used=last_used,
            ),
            credits_remaining=data.get("user", {}).get("credits_remaining", 0),
            recent_requests=data.get("recent_requests", []),
        )
