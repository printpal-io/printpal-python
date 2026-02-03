"""
PrintPal API Client

Main client class for interacting with the PrintPal 3D Generation API.
"""

import os
import time
import logging
from pathlib import Path
from typing import Optional, Union, BinaryIO, Callable

import requests

from printpal.constants import (
    Quality,
    Format,
    CREDIT_COSTS,
    ESTIMATED_TIMES,
    DEFAULT_BASE_URL,
    DEFAULT_TIMEOUT,
    UPLOAD_TIMEOUT,
    DOWNLOAD_TIMEOUT,
)
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
    ServerError,
    TimeoutError,
)


logger = logging.getLogger(__name__)


class PrintPalClient:
    """
    Client for the PrintPal 3D Generation API.
    
    Example usage:
    
        from printpal import PrintPalClient, Quality, Format
        
        # Initialize the client
        client = PrintPalClient(api_key="pp_live_your_api_key_here")
        
        # Check your credit balance
        credits = client.get_credits()
        print(f"Available credits: {credits.credits}")
        
        # Generate a 3D model from an image
        result = client.generate_from_image(
            image_path="my_image.png",
            quality=Quality.DEFAULT,
            format=Format.STL
        )
        
        # Wait for completion and download
        model_path = client.wait_and_download(
            result.generation_uid,
            output_path="my_model.stl"
        )
    
    Args:
        api_key: Your PrintPal API key. Can also be set via PRINTPAL_API_KEY environment variable.
        base_url: API base URL. Defaults to https://printpal.io
        timeout: Default request timeout in seconds.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        self.api_key = api_key or os.environ.get("PRINTPAL_API_KEY")
        if not self.api_key:
            raise AuthenticationError(
                "API key is required. Pass it to the constructor or set PRINTPAL_API_KEY environment variable."
            )
        
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({
            "X-API-Key": self.api_key,
            "User-Agent": "printpal-python/1.0.0",
        })
    
    def _request(
        self,
        method: str,
        endpoint: str,
        timeout: Optional[int] = None,
        **kwargs
    ) -> dict:
        """Make an API request."""
        url = f"{self.base_url}{endpoint}"
        timeout = timeout or self.timeout
        
        try:
            response = self._session.request(method, url, timeout=timeout, **kwargs)
            return self._handle_response(response)
        except requests.exceptions.Timeout:
            raise TimeoutError(f"Request to {endpoint} timed out after {timeout} seconds")
        except requests.exceptions.ConnectionError as e:
            raise PrintPalError(f"Failed to connect to API: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise PrintPalError(f"Request failed: {str(e)}")
    
    def _handle_response(self, response: requests.Response) -> dict:
        """Handle API response and raise appropriate exceptions."""
        try:
            data = response.json()
        except ValueError:
            data = {}
        
        if response.status_code == 200 or response.status_code == 202:
            return data
        
        error_message = data.get("message") or data.get("error") or "Unknown error"
        
        if response.status_code == 401:
            raise AuthenticationError(error_message, response=data)
        elif response.status_code == 402:
            raise InsufficientCreditsError(
                error_message,
                credits_required=data.get("credits_required"),
                credits_available=data.get("credits_available"),
                response=data,
            )
        elif response.status_code == 404:
            raise NotFoundError(error_message, response=data)
        elif response.status_code == 429:
            raise RateLimitError(
                error_message,
                retry_after=response.headers.get("Retry-After"),
                response=data,
            )
        elif response.status_code == 400:
            raise ValidationError(error_message, response=data)
        elif response.status_code >= 500:
            raise ServerError(error_message, status_code=response.status_code, response=data)
        else:
            raise PrintPalError(error_message, status_code=response.status_code, response=data)
    
    # =========================================================================
    # Credit and Account Methods
    # =========================================================================
    
    def get_credits(self) -> CreditsInfo:
        """
        Get your current credit balance.
        
        Returns:
            CreditsInfo: Information about your credits and account.
        
        Example:
            credits = client.get_credits()
            print(f"You have {credits.credits} credits")
        """
        data = self._request("GET", "/api/credits")
        return CreditsInfo.from_response(data)
    
    def get_pricing(self) -> PricingInfo:
        """
        Get API pricing information.
        
        This endpoint does not require authentication.
        
        Returns:
            PricingInfo: Pricing information for all generation types.
        
        Example:
            pricing = client.get_pricing()
            for name, tier in pricing.credits.items():
                print(f"{name}: {tier.cost} credits")
        """
        data = self._request("GET", "/api/pricing")
        return PricingInfo.from_response(data)
    
    def get_usage(self) -> UsageStats:
        """
        Get your API usage statistics.
        
        Returns:
            UsageStats: Usage statistics for your API key.
        
        Example:
            usage = client.get_usage()
            print(f"Total requests: {usage.api_key.total_requests}")
            print(f"Credits used: {usage.api_key.credits_used}")
        """
        data = self._request("GET", "/api/usage")
        return UsageStats.from_response(data)
    
    def health_check(self) -> dict:
        """
        Check if the API is healthy.
        
        This endpoint does not require authentication.
        
        Returns:
            dict: Health status information.
        
        Example:
            health = client.health_check()
            print(f"API status: {health['status']}")
        """
        return self._request("GET", "/api/health")
    
    # =========================================================================
    # Generation Methods
    # =========================================================================
    
    def generate_from_image(
        self,
        image_path: Union[str, Path, BinaryIO],
        quality: Quality = Quality.DEFAULT,
        format: Format = Format.GLB,
        num_inference_steps: int = 20,
        guidance_scale: float = 5.0,
        octree_resolution: int = 256,
    ) -> GenerationResult:
        """
        Generate a 3D model from an image.
        
        Args:
            image_path: Path to the image file or file-like object.
            quality: Quality level for generation.
            format: Output format for the 3D model.
            num_inference_steps: Number of inference steps (1-50). Not used for super/superplus.
            guidance_scale: Guidance scale (0.5-10.0). Not used for super/superplus.
            octree_resolution: Octree resolution (128, 256, 512). Not used for super/superplus.
        
        Returns:
            GenerationResult: Information about the submitted generation.
        
        Raises:
            ValidationError: If parameters are invalid.
            InsufficientCreditsError: If you do not have enough credits.
            PrintPalError: For other API errors.
        
        Example:
            result = client.generate_from_image(
                image_path="my_image.png",
                quality=Quality.SUPER,
                format=Format.STL
            )
            print(f"Generation started: {result.generation_uid}")
            print(f"Estimated time: {result.estimated_time_seconds} seconds")
        """
        # Validate parameters
        request = GenerationRequest(
            quality=quality,
            format=format,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            octree_resolution=octree_resolution,
        )
        request.validate()
        
        # Prepare the image file
        if isinstance(image_path, (str, Path)):
            image_path = Path(image_path)
            if not image_path.exists():
                raise ValidationError(f"Image file not found: {image_path}")
            image_file = open(image_path, "rb")
            filename = image_path.name
            should_close = True
        else:
            image_file = image_path
            filename = getattr(image_path, "name", "image.png")
            should_close = False
        
        try:
            # Prepare form data
            files = {"image": (filename, image_file)}
            data = {
                "quality": quality.value if isinstance(quality, Quality) else quality,
                "format": format.value if isinstance(format, Format) else format,
            }
            
            # Add optional parameters for non-super quality
            if quality not in [
                Quality.SUPER,
                Quality.SUPER_TEXTURE,
                Quality.SUPERPLUS,
                Quality.SUPERPLUS_TEXTURE,
            ]:
                data["num_inference_steps"] = num_inference_steps
                data["guidance_scale"] = guidance_scale
                data["octree_resolution"] = octree_resolution
            
            response = self._request(
                "POST",
                "/api/generate",
                files=files,
                data=data,
                timeout=UPLOAD_TIMEOUT,
            )
            
            return GenerationResult.from_response(response)
        finally:
            if should_close:
                image_file.close()
    
    def generate_from_prompt(
        self,
        prompt: str,
        quality: Quality = Quality.DEFAULT,
        format: Format = Format.GLB,
        num_inference_steps: int = 20,
        guidance_scale: float = 5.0,
        octree_resolution: int = 256,
    ) -> GenerationResult:
        """
        Generate a 3D model from a text prompt.
        
        Note: Text-to-3D is only available for default, high, and ultra quality levels.
        Super resolution requires an image input.
        
        Args:
            prompt: Text description of the 3D model to generate.
            quality: Quality level (default, high, or ultra only).
            format: Output format for the 3D model.
            num_inference_steps: Number of inference steps (1-50).
            guidance_scale: Guidance scale (0.5-10.0).
            octree_resolution: Octree resolution (128, 256, 512).
        
        Returns:
            GenerationResult: Information about the submitted generation.
        
        Raises:
            ValidationError: If parameters are invalid or quality is super/superplus.
            InsufficientCreditsError: If you do not have enough credits.
            PrintPalError: For other API errors.
        
        Example:
            result = client.generate_from_prompt(
                prompt="a cute robot toy",
                quality=Quality.HIGH,
                format=Format.GLB
            )
            print(f"Generation started: {result.generation_uid}")
        """
        # Super resolution does not support text prompts
        if quality in [
            Quality.SUPER,
            Quality.SUPER_TEXTURE,
            Quality.SUPERPLUS,
            Quality.SUPERPLUS_TEXTURE,
        ]:
            raise ValidationError(
                "Text-to-3D is not supported for super resolution. Please use generate_from_image instead."
            )
        
        # Validate parameters
        request = GenerationRequest(
            quality=quality,
            format=format,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            octree_resolution=octree_resolution,
        )
        request.validate()
        
        if not prompt or not prompt.strip():
            raise ValidationError("Prompt cannot be empty")
        
        # Prepare form data
        data = {
            "prompt": prompt.strip(),
            "quality": quality.value if isinstance(quality, Quality) else quality,
            "format": format.value if isinstance(format, Format) else format,
            "num_inference_steps": num_inference_steps,
            "guidance_scale": guidance_scale,
            "octree_resolution": octree_resolution,
        }
        
        response = self._request(
            "POST",
            "/api/generate",
            data=data,
            timeout=UPLOAD_TIMEOUT,
        )
        
        return GenerationResult.from_response(response)
    
    def get_status(self, generation_uid: str) -> GenerationStatus:
        """
        Get the status of a generation request.
        
        Args:
            generation_uid: The unique identifier for the generation.
        
        Returns:
            GenerationStatus: Current status of the generation.
        
        Raises:
            NotFoundError: If the generation is not found.
        
        Example:
            status = client.get_status("abc123-def456")
            if status.is_completed:
                print("Generation complete!")
            elif status.is_processing:
                print("Still processing...")
        """
        data = self._request("GET", f"/api/generate/{generation_uid}/status")
        return GenerationStatus.from_response(data)
    
    def get_download_url(self, generation_uid: str) -> dict:
        """
        Get a presigned URL to download a completed generation.
        
        The URL expires after 1 hour. If it expires, call this method again
        to get a new URL.
        
        Args:
            generation_uid: The unique identifier for the generation.
        
        Returns:
            dict: Contains 'download_url', 'format', and 'expires_in' (seconds).
        
        Raises:
            NotFoundError: If the generation is not found.
            ValidationError: If the generation is not yet completed.
        
        Example:
            download_info = client.get_download_url("abc123-def456")
            print(f"Download URL: {download_info['download_url']}")
            print(f"Expires in: {download_info['expires_in']} seconds")
        """
        return self._request("GET", f"/api/generate/{generation_uid}/download")
    
    def download(
        self,
        generation_uid: str,
        output_path: Optional[Union[str, Path]] = None,
    ) -> Path:
        """
        Download a completed 3D model.
        
        Args:
            generation_uid: The unique identifier for the generation.
            output_path: Where to save the file. If not provided, saves to current
                directory with auto-generated filename.
        
        Returns:
            Path: Path to the downloaded file.
        
        Raises:
            NotFoundError: If the generation is not found.
            ValidationError: If the generation is not yet completed.
            PrintPalError: If download fails.
        
        Example:
            path = client.download("abc123-def456", output_path="my_model.stl")
            print(f"Downloaded to: {path}")
        """
        # Get the download URL
        download_info = self.get_download_url(generation_uid)
        download_url = download_info.get("download_url")
        file_format = download_info.get("format", "glb")
        
        if not download_url:
            raise GenerationError("No download URL available", generation_uid=generation_uid)
        
        # Determine output path
        if output_path:
            output_path = Path(output_path)
        else:
            output_path = Path(f"printpal_model_{generation_uid[:8]}.{file_format}")
        
        # Download the file
        try:
            response = requests.get(download_url, timeout=DOWNLOAD_TIMEOUT)
            response.raise_for_status()
            
            output_path.write_bytes(response.content)
            logger.info(f"Downloaded model to {output_path}")
            
            return output_path
        except requests.RequestException as e:
            raise PrintPalError(f"Failed to download model: {str(e)}")
    
    def wait_for_completion(
        self,
        generation_uid: str,
        poll_interval: int = 5,
        timeout: Optional[int] = None,
        callback: Optional[Callable[[GenerationStatus], None]] = None,
    ) -> GenerationStatus:
        """
        Wait for a generation to complete.
        
        Polls the API at regular intervals until the generation completes,
        fails, or times out.
        
        Args:
            generation_uid: The unique identifier for the generation.
            poll_interval: Seconds between status checks (default: 5).
            timeout: Maximum seconds to wait. If None, uses estimated time * 2.
            callback: Optional function called with status after each poll.
        
        Returns:
            GenerationStatus: Final status of the generation.
        
        Raises:
            GenerationError: If the generation fails.
            TimeoutError: If the timeout is exceeded.
        
        Example:
            def on_status(status):
                print(f"Status: {status.status}")
            
            status = client.wait_for_completion(
                "abc123-def456",
                callback=on_status
            )
            if status.is_completed:
                print("Done!")
        """
        start_time = time.time()
        
        # Get initial status to determine quality and timeout
        status = self.get_status(generation_uid)
        
        if timeout is None:
            # Default timeout based on quality
            quality_str = status.quality or "default"
            try:
                quality = Quality(quality_str)
                estimated = ESTIMATED_TIMES.get(quality, 60)
            except ValueError:
                estimated = 60
            timeout = estimated * 3  # 3x estimated time as default timeout
        
        while True:
            if callback:
                callback(status)
            
            if status.is_completed:
                return status
            
            if status.is_failed:
                raise GenerationError(
                    "Generation failed",
                    generation_uid=generation_uid,
                )
            
            elapsed = time.time() - start_time
            if elapsed >= timeout:
                raise TimeoutError(
                    f"Generation did not complete within {timeout} seconds"
                )
            
            time.sleep(poll_interval)
            status = self.get_status(generation_uid)
        
        return status
    
    def wait_and_download(
        self,
        generation_uid: str,
        output_path: Optional[Union[str, Path]] = None,
        poll_interval: int = 5,
        timeout: Optional[int] = None,
        callback: Optional[Callable[[GenerationStatus], None]] = None,
    ) -> Path:
        """
        Wait for generation to complete and download the result.
        
        Convenience method that combines wait_for_completion and download.
        
        Args:
            generation_uid: The unique identifier for the generation.
            output_path: Where to save the file.
            poll_interval: Seconds between status checks.
            timeout: Maximum seconds to wait.
            callback: Optional function called with status after each poll.
        
        Returns:
            Path: Path to the downloaded file.
        
        Example:
            # Generate and download in one call
            result = client.generate_from_image("image.png")
            path = client.wait_and_download(
                result.generation_uid,
                output_path="output.stl"
            )
            print(f"Model saved to: {path}")
        """
        self.wait_for_completion(
            generation_uid,
            poll_interval=poll_interval,
            timeout=timeout,
            callback=callback,
        )
        return self.download(generation_uid, output_path)
    
    def generate_and_download(
        self,
        image_path: Union[str, Path, BinaryIO],
        output_path: Optional[Union[str, Path]] = None,
        quality: Quality = Quality.DEFAULT,
        format: Format = Format.GLB,
        poll_interval: int = 5,
        timeout: Optional[int] = None,
        callback: Optional[Callable[[GenerationStatus], None]] = None,
        **kwargs,
    ) -> Path:
        """
        Generate a 3D model from an image and download when complete.
        
        This is the simplest way to go from image to 3D model in one call.
        
        Args:
            image_path: Path to the image file.
            output_path: Where to save the model.
            quality: Quality level for generation.
            format: Output format.
            poll_interval: Seconds between status checks.
            timeout: Maximum seconds to wait.
            callback: Optional status callback function.
            **kwargs: Additional parameters for generation.
        
        Returns:
            Path: Path to the downloaded 3D model.
        
        Example:
            # Simplest usage
            path = client.generate_and_download("my_image.png", "my_model.stl")
            
            # With quality setting
            path = client.generate_and_download(
                "my_image.png",
                "my_model.stl",
                quality=Quality.SUPER,
                callback=lambda s: print(f"Status: {s.status}")
            )
        """
        result = self.generate_from_image(
            image_path=image_path,
            quality=quality,
            format=format,
            **kwargs,
        )
        
        return self.wait_and_download(
            result.generation_uid,
            output_path=output_path,
            poll_interval=poll_interval,
            timeout=timeout,
            callback=callback,
        )
    
    # =========================================================================
    # Context Manager Support
    # =========================================================================
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._session.close()
    
    def close(self):
        """Close the client session."""
        self._session.close()
