"""
PrintPal Python Client

A Python client library for the PrintPal 3D Generation API.
Transform images into high-quality 3D models using AI.

Website: https://printpal.io
Documentation: https://printpal.io/api/documentation
"""

from printpal.client import PrintPalClient
from printpal.models import (
    GenerationRequest,
    GenerationStatus,
    GenerationResult,
    CreditsInfo,
    PricingInfo,
    UsageStats,
)
from printpal.exceptions import (
    PrintPalError,
    AuthenticationError,
    InsufficientCreditsError,
    RateLimitError,
    GenerationError,
    NotFoundError,
    ValidationError,
)
from printpal.constants import (
    Quality,
    Format,
    CREDIT_COSTS,
    ESTIMATED_TIMES,
)

__version__ = "1.0.0"
__author__ = "PrintPal"
__email__ = "support@printpal.io"

__all__ = [
    # Client
    "PrintPalClient",
    # Models
    "GenerationRequest",
    "GenerationStatus",
    "GenerationResult",
    "CreditsInfo",
    "PricingInfo",
    "UsageStats",
    # Exceptions
    "PrintPalError",
    "AuthenticationError",
    "InsufficientCreditsError",
    "RateLimitError",
    "GenerationError",
    "NotFoundError",
    "ValidationError",
    # Constants
    "Quality",
    "Format",
    "CREDIT_COSTS",
    "ESTIMATED_TIMES",
]
