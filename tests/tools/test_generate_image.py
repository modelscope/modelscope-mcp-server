import pytest
import requests
from fastmcp import Client

from modelscope_mcp_server import settings
from modelscope_mcp_server.types import GenerationType


async def test_text_to_image_generation_success(mcp_server, mocker):
    """Test successful text-to-image generation."""
    mock_response_data = {"images": [{"url": "https://example.com/generated_image.jpg"}]}
    mock_post = mocker.patch("modelscope_mcp_server.client.default_client.post", return_value=mock_response_data)

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

        assert image_result.type == GenerationType.TEXT_TO_IMAGE.value, "Should be text-to-image generation"
        assert image_result.model == "iic/text-to-image-7b", "Model should match input"
        assert image_result.image_url == "https://example.com/generated_image.jpg", (
            "Image URL should match mock response"
        )

        mock_post.assert_called_once()


async def test_image_to_image_generation_success(mcp_server, mocker):
    """Test successful image-to-image generation."""
    mock_response_data = {"images": [{"url": "https://example.com/modified_image.jpg"}]}
    mock_post = mocker.patch("modelscope_mcp_server.client.default_client.post", return_value=mock_response_data)

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

        assert image_result.type == GenerationType.IMAGE_TO_IMAGE.value, "Should be image-to-image generation"
        assert image_result.model == "iic/image-to-image-7b", "Model should match input"
        assert image_result.image_url == "https://example.com/modified_image.jpg", (
            "Image URL should match mock response"
        )

        mock_post.assert_called_once()


async def test_generate_image_with_default_model(mcp_server, mocker):
    """Test image generation with default model when no model is specified."""
    mock_response_data = {"images": [{"url": "https://example.com/default_model_image.jpg"}]}
    mocker.patch("modelscope_mcp_server.client.default_client.post", return_value=mock_response_data)

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


async def test_generate_image_api_error_response(mcp_server, mocker):
    """Test handling of API error response."""
    # Mock client.post to raise an HTTPError
    mocker.patch(
        "modelscope_mcp_server.client.default_client.post",
        side_effect=requests.exceptions.HTTPError("404 Client Error: Not Found"),
    )

    async with Client(mcp_server) as client:
        with pytest.raises(Exception) as exc_info:
            await client.call_tool(
                "generate_image",
                {"prompt": "A test image", "model": "non-existent-model"},
            )

        print(f"✅ API error handled correctly: {exc_info.value}")
        assert "404 Client Error" in str(exc_info.value)


async def test_generate_image_timeout_error(mcp_server, mocker):
    """Test handling of request timeout."""
    mocker.patch(
        "modelscope_mcp_server.client.default_client.post",
        side_effect=TimeoutError("Request timeout - please try again later"),
    )

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


async def test_generate_image_malformed_response(mcp_server, mocker):
    """Test handling of malformed API response."""
    malformed_response_data = {
        "result": "success",
        # Missing 'images' field
    }
    mocker.patch("modelscope_mcp_server.client.default_client.post", return_value=malformed_response_data)

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
        assert "No images found in response" in str(exc_info.value)


async def test_generate_image_request_parameters(mcp_server, mocker):
    """Test that the correct parameters are sent in the request."""
    mock_response_data = {"images": [{"url": "https://example.com/test_image.jpg"}]}
    mock_post = mocker.patch("modelscope_mcp_server.client.default_client.post", return_value=mock_response_data)

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

        # Check URL - should contain images/generations
        url = call_args.args[0]
        assert "images/generations" in url

        # Check payload
        json_data = call_args.kwargs["json_data"]
        assert json_data["model"] == "test-model"
        assert json_data["prompt"] == "Test prompt"
        assert json_data["image_url"] == "https://example.com/input.jpg"

        # Check timeout
        assert call_args.kwargs["timeout"] == 300

        print("✅ Request parameters verified correctly")
