"""
Exceptions for the PrintPal API client.
"""


class PrintPalError(Exception):
    """Base exception for all PrintPal errors."""
    
    def __init__(self, message: str, status_code: int = None, response: dict = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response = response or {}
    
    def __str__(self):
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class AuthenticationError(PrintPalError):
    """Raised when API key is invalid or missing."""
    
    def __init__(self, message: str = "Invalid or missing API key", **kwargs):
        super().__init__(message, status_code=401, **kwargs)


class InsufficientCreditsError(PrintPalError):
    """Raised when user does not have enough credits for the operation."""
    
    def __init__(
        self,
        message: str = "Insufficient credits",
        credits_required: int = None,
        credits_available: int = None,
        **kwargs
    ):
        super().__init__(message, status_code=402, **kwargs)
        self.credits_required = credits_required
        self.credits_available = credits_available
    
    def __str__(self):
        if self.credits_required and self.credits_available is not None:
            return (
                f"{self.message}: requires {self.credits_required} credits, "
                f"but only {self.credits_available} available"
            )
        return super().__str__()


class RateLimitError(PrintPalError):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = None, **kwargs):
        super().__init__(message, status_code=429, **kwargs)
        self.retry_after = retry_after
    
    def __str__(self):
        if self.retry_after:
            return f"{self.message}. Retry after {self.retry_after} seconds."
        return super().__str__()


class GenerationError(PrintPalError):
    """Raised when 3D generation fails."""
    
    def __init__(self, message: str = "Generation failed", generation_uid: str = None, **kwargs):
        super().__init__(message, **kwargs)
        self.generation_uid = generation_uid


class NotFoundError(PrintPalError):
    """Raised when a resource is not found."""
    
    def __init__(self, message: str = "Resource not found", **kwargs):
        super().__init__(message, status_code=404, **kwargs)


class ValidationError(PrintPalError):
    """Raised when request validation fails."""
    
    def __init__(self, message: str = "Validation failed", **kwargs):
        super().__init__(message, status_code=400, **kwargs)


class TimeoutError(PrintPalError):
    """Raised when a request times out."""
    
    def __init__(self, message: str = "Request timed out", **kwargs):
        super().__init__(message, status_code=408, **kwargs)


class ServerError(PrintPalError):
    """Raised when the server returns an error."""
    
    def __init__(self, message: str = "Server error", **kwargs):
        super().__init__(message, status_code=500, **kwargs)
