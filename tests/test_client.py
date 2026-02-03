"""
Unit tests for the PrintPal client.

To run tests:
    pip install pytest
    pytest tests/
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import json

from printpal import (
    PrintPalClient,
    Quality,
    Format,
    AuthenticationError,
    InsufficientCreditsError,
    ValidationError,
    NotFoundError,
)
from printpal.models import GenerationRequest, GenerationStatus, CreditsInfo


class TestQuality:
    """Tests for Quality enum."""
    
    def test_quality_values(self):
        assert Quality.DEFAULT.value == "default"
        assert Quality.HIGH.value == "high"
        assert Quality.ULTRA.value == "ultra"
        assert Quality.SUPER.value == "super"
        assert Quality.SUPER_TEXTURE.value == "super_texture"
        assert Quality.SUPERPLUS.value == "superplus"
        assert Quality.SUPERPLUS_TEXTURE.value == "superplus_texture"
    
    def test_quality_from_string(self):
        assert Quality("default") == Quality.DEFAULT
        assert Quality("super") == Quality.SUPER


class TestFormat:
    """Tests for Format enum."""
    
    def test_format_values(self):
        assert Format.STL.value == "stl"
        assert Format.GLB.value == "glb"
        assert Format.OBJ.value == "obj"
        assert Format.PLY.value == "ply"
        assert Format.FBX.value == "fbx"


class TestGenerationRequest:
    """Tests for GenerationRequest model."""
    
    def test_default_values(self):
        request = GenerationRequest()
        assert request.quality == Quality.DEFAULT
        assert request.format == Format.GLB
        assert request.num_inference_steps == 20
        assert request.guidance_scale == 5.0
        assert request.octree_resolution == 256
    
    def test_validate_valid_request(self):
        request = GenerationRequest(
            quality=Quality.DEFAULT,
            format=Format.STL,
        )
        request.validate()  # Should not raise
    
    def test_validate_invalid_format_for_texture(self):
        request = GenerationRequest(
            quality=Quality.SUPER_TEXTURE,
            format=Format.STL,  # STL not valid for texture
        )
        with pytest.raises(ValidationError):
            request.validate()
    
    def test_validate_texture_quality_glb(self):
        request = GenerationRequest(
            quality=Quality.SUPER_TEXTURE,
            format=Format.GLB,
        )
        request.validate()  # Should not raise
    
    def test_validate_invalid_inference_steps(self):
        request = GenerationRequest(
            quality=Quality.DEFAULT,
            num_inference_steps=100,  # Invalid
        )
        with pytest.raises(ValidationError):
            request.validate()


class TestGenerationStatus:
    """Tests for GenerationStatus model."""
    
    def test_from_response(self):
        data = {
            "generation_uid": "abc123",
            "status": "completed",
            "quality": "default",
            "format": "stl",
        }
        status = GenerationStatus.from_response(data)
        assert status.generation_uid == "abc123"
        assert status.status == "completed"
        assert status.is_completed
        assert not status.is_failed
        assert not status.is_processing
    
    def test_is_processing(self):
        status = GenerationStatus(
            generation_uid="abc",
            status="processing",
        )
        assert status.is_processing
        assert not status.is_completed
        assert not status.is_failed
    
    def test_is_failed(self):
        status = GenerationStatus(
            generation_uid="abc",
            status="failed",
        )
        assert status.is_failed
        assert not status.is_completed
        assert not status.is_processing


class TestCreditsInfo:
    """Tests for CreditsInfo model."""
    
    def test_from_response(self):
        data = {
            "credits": 100,
            "user_id": 1,
            "username": "testuser",
        }
        info = CreditsInfo.from_response(data)
        assert info.credits == 100
        assert info.user_id == 1
        assert info.username == "testuser"


class TestPrintPalClient:
    """Tests for PrintPalClient."""
    
    def test_init_with_api_key(self):
        client = PrintPalClient(api_key="pp_live_test123")
        assert client.api_key == "pp_live_test123"
        assert client.base_url == "https://printpal.io"
    
    def test_init_without_api_key(self):
        with pytest.raises(AuthenticationError):
            PrintPalClient(api_key=None)
    
    def test_init_with_env_var(self, monkeypatch):
        monkeypatch.setenv("PRINTPAL_API_KEY", "pp_live_env_key")
        client = PrintPalClient()
        assert client.api_key == "pp_live_env_key"
    
    @patch("printpal.client.requests.Session")
    def test_get_credits(self, mock_session_class):
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "credits": 50,
            "user_id": 1,
            "username": "test",
        }
        mock_session.request.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        client = PrintPalClient(api_key="pp_live_test")
        credits = client.get_credits()
        
        assert credits.credits == 50
        assert credits.username == "test"
    
    @patch("printpal.client.requests.Session")
    def test_authentication_error(self, mock_session_class):
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": "Invalid API key"}
        mock_session.request.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        client = PrintPalClient(api_key="pp_live_invalid")
        
        with pytest.raises(AuthenticationError):
            client.get_credits()
    
    @patch("printpal.client.requests.Session")
    def test_insufficient_credits_error(self, mock_session_class):
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 402
        mock_response.json.return_value = {
            "error": "Insufficient credits",
            "credits_required": 20,
            "credits_available": 5,
        }
        mock_session.request.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        client = PrintPalClient(api_key="pp_live_test")
        
        with pytest.raises(InsufficientCreditsError) as exc_info:
            client._request("POST", "/api/generate")
        
        assert exc_info.value.credits_required == 20
        assert exc_info.value.credits_available == 5


class TestClientContextManager:
    """Tests for context manager functionality."""
    
    def test_context_manager(self):
        with PrintPalClient(api_key="pp_live_test") as client:
            assert client.api_key == "pp_live_test"
        # Session should be closed after context


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
