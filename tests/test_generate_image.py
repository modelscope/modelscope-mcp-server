"""
Tests for ModelScope MCP Server AIGC image generation functionality.

Uses mocking to avoid actual API calls and speed up testing.
"""

import json
from unittest.mock import patch

import pytest
import requests
from fastmcp import Client

from modelscope_mcp_server import settings
from modelscope_mcp_server.types import GenerationType


class MockResponse:
    """Mock response class for requests.post calls."""

    def __init__(self, json_data, status_code=200):
        self.json_data = json_data
        self.status_code = status_code
        self.text = (
            json.dumps(json_data) if isinstance(json_data, dict) else str(json_data)
        )

    def json(self):
        return self.json_data


@pytest.mark.asyncio
async def test_text_to_image_generation_success(mcp_server):
    """Test successful text-to-image generation."""
    mock_response_data = {
        "images": [{"url": "https://example.com/generated_image.jpg"}]
    }

    with patch("requests.post") as mock_post:
        mock_post.return_value = MockResponse(mock_response_data, 200)

        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "generate_image",
                {
                    "prompt": "A beautiful landscape with mountains and lake",
                    "model": "iic/text-to-image-7b",
                },
            )

            assert hasattr(result, "data"), "Result should have data attribute"
            image_result = result.data

            print(f"✅ Generated text-to-image result: {image_result}")

            assert image_result.type == GenerationType.TEXT_TO_IMAGE.value, (
                "Should be text-to-image generation"
            )
            assert image_result.model == "iic/text-to-image-7b", (
                "Model should match input"
            )
            assert (
                image_result.image_url == "https://example.com/generated_image.jpg"
            ), "Image URL should match mock response"

            mock_post.assert_called_once()


@pytest.mark.asyncio
async def test_image_to_image_generation_success(mcp_server):
    """Test successful image-to-image generation."""
    mock_response_data = {"images": [{"url": "https://example.com/modified_image.jpg"}]}

    with patch("requests.post") as mock_post:
        mock_post.return_value = MockResponse(mock_response_data, 200)

        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "generate_image",
                {
                    "prompt": "Transform this image into a cartoon style",
                    "model": "iic/image-to-image-7b",
                    "image_url": "https://example.com/source_image.jpg",
                },
            )

            assert hasattr(result, "data"), "Result should have data attribute"
            image_result = result.data

            print(f"✅ Generated image-to-image result: {image_result}")

            assert image_result.type == GenerationType.IMAGE_TO_IMAGE.value, (
                "Should be image-to-image generation"
            )
            assert image_result.model == "iic/image-to-image-7b", (
                "Model should match input"
            )
            assert image_result.image_url == "https://example.com/modified_image.jpg", (
                "Image URL should match mock response"
            )

            mock_post.assert_called_once()


@pytest.mark.asyncio
async def test_generate_image_with_default_model(mcp_server):
    """Test image generation with default model when no model is specified."""
    mock_response_data = {
        "images": [{"url": "https://example.com/default_model_image.jpg"}]
    }

    with patch("requests.post") as mock_post:
        mock_post.return_value = MockResponse(mock_response_data, 200)

        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "generate_image",
                {
                    "prompt": "A futuristic city at sunset",
                    # No model specified - should use default
                },
            )

            assert hasattr(result, "data"), "Result should have data attribute"
            image_result = result.data

            print(f"✅ Generated text-to-image with default model: {image_result}")

            assert image_result.model == settings.default_text_to_image_model, (
                "Model should match default text-to-image model"
            )


@pytest.mark.asyncio
async def test_generate_image_empty_prompt_error(mcp_server):
    """Test error handling for empty prompt."""
    async with Client(mcp_server) as client:
        with pytest.raises(Exception) as exc_info:
            await client.call_tool(
                "generate_image",
                {"prompt": "", "model": "iic/text-to-image-7b"},
            )

        print(f"✅ Empty prompt error handled correctly: {exc_info.value}")
        assert "Prompt cannot be empty" in str(exc_info.value)


@pytest.mark.asyncio
async def test_generate_image_api_error_response(mcp_server):
    """Test handling of API error response."""
    error_response_data = {"error": "Model not found", "code": "MODEL_NOT_FOUND"}

    with patch("requests.post") as mock_post:
        mock_post.return_value = MockResponse(error_response_data, 404)

        async with Client(mcp_server) as client:
            with pytest.raises(Exception) as exc_info:
                await client.call_tool(
                    "generate_image",
                    {"prompt": "A test image", "model": "non-existent-model"},
                )

            print(f"✅ API error handled correctly: {exc_info.value}")
            assert "Server returned non-200 status code: 404" in str(exc_info.value)


@pytest.mark.asyncio
async def test_generate_image_timeout_error(mcp_server):
    """Test handling of request timeout."""
    with patch("requests.post") as mock_post:
        mock_post.side_effect = requests.exceptions.Timeout("Request timeout")

        async with Client(mcp_server) as client:
            with pytest.raises(Exception) as exc_info:
                await client.call_tool(
                    "generate_image",
                    {
                        "prompt": "A test image",
                        "model": "iic/text-to-image-7b",
                    },
                )

            print(f"✅ Timeout error handled correctly: {exc_info.value}")
            assert "Request timeout" in str(exc_info.value)


@pytest.mark.asyncio
async def test_generate_image_malformed_response(mcp_server):
    """Test handling of malformed API response."""
    malformed_response_data = {
        "result": "success",
        # Missing 'images' field
    }

    with patch("requests.post") as mock_post:
        mock_post.return_value = MockResponse(malformed_response_data, 200)

        async with Client(mcp_server) as client:
            with pytest.raises(Exception) as exc_info:
                await client.call_tool(
                    "generate_image",
                    {
                        "prompt": "A test image",
                        "model": "iic/text-to-image-7b",
                    },
                )

            print(f"✅ Malformed response error handled correctly: {exc_info.value}")
            assert "Server returned error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_generate_image_request_parameters(mcp_server):
    """Test that the correct parameters are sent in the request."""
    mock_response_data = {"images": [{"url": "https://example.com/test_image.jpg"}]}

    with patch("requests.post") as mock_post:
        mock_post.return_value = MockResponse(mock_response_data, 200)

        async with Client(mcp_server) as client:
            await client.call_tool(
                "generate_image",
                {
                    "prompt": "Test prompt",
                    "model": "test-model",
                    "image_url": "https://example.com/input.jpg",
                },
            )

            # Verify the request was called with correct parameters
            mock_post.assert_called_once()
            call_args = mock_post.call_args

            # Check URL
            assert "images/generations" in call_args.args[0]

            # Check headers
            headers = call_args.kwargs["headers"]
            assert headers["Content-Type"] == "application/json"
            assert "Authorization" in headers
            assert headers["User-Agent"] == "modelscope-mcp-server"

            # Check payload
            payload_bytes = call_args.kwargs["data"]
            payload = json.loads(payload_bytes.decode("utf-8"))
            assert payload["model"] == "test-model"
            assert payload["prompt"] == "Test prompt"
            assert payload["image_url"] == "https://example.com/input.jpg"

            print("✅ Request parameters verified correctly")
