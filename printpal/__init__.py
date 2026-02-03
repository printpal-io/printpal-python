"""
PrintPal Python Client

A Python client library for the PrintPal 3D Generation API.
Transform images into high-quality 3D models using AI.

Website: https://printpal.io
Documentation: https://printpal.io/api/documentation

Usage:
    from printpal import PrintPal
    client = PrintPal(api_key="pp_live_your_api_key")
    
    # Or use any of these aliases:
    from printpal import PrintPalClient  # Same as PrintPal
    from printpal import printpal        # Same as PrintPal (lowercase)
"""

from printpal.client import PrintPal, PrintPalClient, printpal
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
    GENERATION_TIMEOUTS,
)

__version__ = "1.0.3"
__author__ = "PrintPal"
__email__ = "support@printpal.io"

__all__ = [
    # Client (main class and aliases)
    "PrintPal",
    "PrintPalClient",
    "printpal",
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
    "GENERATION_TIMEOUTS",
]
