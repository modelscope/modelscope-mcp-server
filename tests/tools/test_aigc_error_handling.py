"""Error handling tests for AIGC image generation tools."""

import asyncio

import pytest
from fastmcp import Client

from modelscope_mcp_server import settings


class TestImageGenerationPollingErrors:
    """Test error handling in image generation polling."""

    async def test_polling_timeout_exceeded(self, mcp_server, mocker):
        """Test that polling times out after max attempts."""
        # Mock initial submission success
        _ = mocker.patch(
            "modelscope_mcp_server.client.ModelScopeClient.post",
            new_callable=mocker.AsyncMock,
            return_value={"task_id": "timeout-task"},
        )

        # Mock polling to always return PENDING status
        mock_get = mocker.patch(
            "modelscope_mcp_server.client.ModelScopeClient.get",
            new_callable=mocker.AsyncMock,
            return_value={
                "task_status": "PENDING",
                "message": "Still processing...",
            },
        )

        # Reduce max attempts for faster test
        original_max_attempts = settings.max_poll_attempts
        settings.max_poll_attempts = 3

        # Mock asyncio.sleep to speed up test
        mock_sleep = mocker.patch("modelscope_mcp_server.tools.aigc.asyncio.sleep", new_callable=mocker.AsyncMock)

        try:
            async with Client(mcp_server) as client:
                with pytest.raises(Exception) as exc_info:
                    await client.call_tool(
                        "generate_image",
                        {
                            "prompt": "Test image that will timeout",
                            "model": "test-model",
                        },
                    )

            # Verify timeout error message
            assert "timeout" in str(exc_info.value).lower()

            # Verify polling was attempted multiple times
            assert mock_get.call_count >= settings.max_poll_attempts

            # Verify sleep was called
            assert mock_sleep.called

        finally:
            settings.max_poll_attempts = original_max_attempts

    async def test_polling_task_failed_status(self, mcp_server, mocker):
        """Test handling of FAILED task status during polling."""
        _ = mocker.patch(
            "modelscope_mcp_server.client.ModelScopeClient.post",
            new_callable=mocker.AsyncMock,
            return_value={"task_id": "failed-task"},
        )

        # Mock polling to return FAILED status
        _ = mocker.patch(
            "modelscope_mcp_server.client.ModelScopeClient.get",
            new_callable=mocker.AsyncMock,
            return_value={
                "task_status": "FAILED",
                "errors": {
                    "message": "Model inference failed: Out of memory",
                },
                "request_id": "req-12345",
            },
        )

        async with Client(mcp_server) as client:
            with pytest.raises(Exception) as exc_info:
                await client.call_tool(
                    "generate_image",
                    {
                        "prompt": "Test image that will fail",
                        "model": "test-model",
                    },
                )

        # Verify error contains failure details
        error_msg = str(exc_info.value)
        assert "Image generation failed" in error_msg
        assert "Out of memory" in error_msg
        assert "failed-task" in error_msg
        assert "req-12345" in error_msg

    async def test_polling_status_transitions(self, mcp_server, mocker):
        """Test handling of various status transitions during polling."""
        _ = mocker.patch(
            "modelscope_mcp_server.client.ModelScopeClient.post",
            new_callable=mocker.AsyncMock,
            return_value={"task_id": "status-transition-task"},
        )

        # Mock status transitions: PENDING -> RUNNING -> SUCCEED
        mock_get = mocker.patch(
            "modelscope_mcp_server.client.ModelScopeClient.get",
            new_callable=mocker.AsyncMock,
        )
        mock_get.side_effect = [
            {"task_status": "PENDING", "message": "Task queued"},
            {"task_status": "RUNNING", "message": "Processing image"},
            {"task_status": "RUNNING", "progress": 50},
            {
                "task_status": "SUCCEED",
                "output_images": ["https://example.com/final.jpg"],
            },
        ]

        mocker.patch("asyncio.sleep", new_callable=mocker.AsyncMock)

        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "generate_image",
                {
                    "prompt": "Test status transitions",
                    "model": "test-model",
                },
            )

        assert result.data.image_url == "https://example.com/final.jpg"
        assert mock_get.call_count == 4


class TestImageGenerationValidationErrors:
    """Test input validation and error handling."""

    async def test_missing_api_token(self, mcp_server, mocker):
        """Test error when API token is not configured."""
        # Temporarily remove API token
        original_token = settings.api_token
        settings.api_token = None

        try:
            async with Client(mcp_server) as client:
                with pytest.raises(Exception) as exc_info:
                    await client.call_tool(
                        "generate_image",
                        {
                            "prompt": "Test without token",
                            "model": "test-model",
                        },
                    )

            assert "API token is not set" in str(exc_info.value)
        finally:
            settings.api_token = original_token

    async def test_empty_prompt_validation(self, mcp_server):
        """Test validation of empty prompt."""
        async with Client(mcp_server) as client:
            with pytest.raises(Exception) as exc_info:
                await client.call_tool(
                    "generate_image",
                    {
                        "prompt": "",  # Empty prompt
                        "model": "test-model",
                    },
                )

        assert "Prompt cannot be empty" in str(exc_info.value)

    async def test_whitespace_only_prompt(self, mcp_server):
        """Test validation of whitespace-only prompt."""
        async with Client(mcp_server) as client:
            with pytest.raises(Exception) as exc_info:
                await client.call_tool(
                    "generate_image",
                    {
                        "prompt": "   \n\t  ",  # Only whitespace
                        "model": "test-model",
                    },
                )

        assert "Prompt cannot be empty" in str(exc_info.value)

    async def test_missing_model_with_no_default(self, mcp_server, mocker):
        """Test error when model is not specified and no default is configured."""
        # Temporarily clear default model
        original_default = settings.default_text_to_image_model
        settings.default_text_to_image_model = ""

        try:
            async with Client(mcp_server) as client:
                with pytest.raises(Exception) as exc_info:
                    await client.call_tool(
                        "generate_image",
                        {
                            "prompt": "Test without model",
                            # No model specified
                        },
                    )

            assert "Model name cannot be empty" in str(exc_info.value)
        finally:
            settings.default_text_to_image_model = original_default


class TestImageGenerationResponseErrors:
    """Test handling of malformed API responses."""

    async def test_missing_task_id_in_response(self, mcp_server, mocker):
        """Test handling when task_id is missing from submission response."""
        _ = mocker.patch(
            "modelscope_mcp_server.client.ModelScopeClient.post",
            new_callable=mocker.AsyncMock,
            return_value={
                "success": True,
                # Missing task_id
            },
        )

        async with Client(mcp_server) as client:
            with pytest.raises(Exception) as exc_info:
                await client.call_tool(
                    "generate_image",
                    {
                        "prompt": "Test missing task_id",
                        "model": "test-model",
                    },
                )

        assert "No task_id found in response" in str(exc_info.value)

    async def test_missing_output_images_in_success(self, mcp_server, mocker):
        """Test handling when output_images is missing from successful task."""
        _ = mocker.patch(
            "modelscope_mcp_server.client.ModelScopeClient.post",
            new_callable=mocker.AsyncMock,
            return_value={"task_id": "no-images-task"},
        )

        _ = mocker.patch(
            "modelscope_mcp_server.client.ModelScopeClient.get",
            new_callable=mocker.AsyncMock,
            return_value={
                "task_status": "SUCCEED",
                # Missing output_images
            },
        )

        async with Client(mcp_server) as client:
            with pytest.raises(Exception) as exc_info:
                await client.call_tool(
                    "generate_image",
                    {
                        "prompt": "Test missing images",
                        "model": "test-model",
                    },
                )

        assert "No output images found" in str(exc_info.value)

    async def test_empty_output_images_array(self, mcp_server, mocker):
        """Test handling when output_images is an empty array."""
        _ = mocker.patch(
            "modelscope_mcp_server.client.ModelScopeClient.post",
            new_callable=mocker.AsyncMock,
            return_value={"task_id": "empty-images-task"},
        )

        _ = mocker.patch(
            "modelscope_mcp_server.client.ModelScopeClient.get",
            new_callable=mocker.AsyncMock,
            return_value={
                "task_status": "SUCCEED",
                "output_images": [],  # Empty array
            },
        )

        async with Client(mcp_server) as client:
            with pytest.raises(Exception) as exc_info:
                await client.call_tool(
                    "generate_image",
                    {
                        "prompt": "Test empty images array",
                        "model": "test-model",
                    },
                )

        assert "No output images found" in str(exc_info.value)


class TestConcurrentImageGeneration:
    """Test error handling with concurrent image generation requests."""

    async def test_concurrent_requests_with_mixed_results(self, mcp_server, mocker):
        """Test handling multiple concurrent requests with different outcomes."""
        # Mock different outcomes for each request
        post_counter = 0
        post_results = [
            {"task_id": "task-1"},
            {"task_id": "task-2"},
            {"task_id": "task-3"},
        ]

        async def mock_post_side_effect(*args, **kwargs):
            nonlocal post_counter
            result = post_results[post_counter]
            post_counter += 1
            return result

        _ = mocker.patch(
            "modelscope_mcp_server.client.ModelScopeClient.post",
            new_callable=mocker.AsyncMock,
            side_effect=mock_post_side_effect,
        )

        # Mock different polling outcomes
        get_responses = {
            "task-1": [
                {"task_status": "SUCCEED", "output_images": ["https://example.com/image1.jpg"]},
            ],
            "task-2": [
                {"task_status": "FAILED", "errors": {"message": "Task 2 failed"}},
            ],
            "task-3": [
                {"task_status": "PENDING"},
                {"task_status": "SUCCEED", "output_images": ["https://example.com/image3.jpg"]},
            ],
        }

        async def mock_get_side_effect(url, *args, **kwargs):
            task_id = url.split("/")[-1]
            responses = get_responses.get(task_id, [])
            if responses:
                return responses.pop(0)
            return {"task_status": "PENDING"}

        _ = mocker.patch(
            "modelscope_mcp_server.client.ModelScopeClient.get",
            new_callable=mocker.AsyncMock,
            side_effect=mock_get_side_effect,
        )

        mocker.patch("asyncio.sleep", new_callable=mocker.AsyncMock)

        async with Client(mcp_server) as client:
            # Create concurrent requests
            tasks = [
                client.call_tool(
                    "generate_image",
                    {"prompt": f"Test {i}", "model": "test-model"},
                )
                for i in range(3)
            ]

            # Gather results with exceptions
            results = await asyncio.gather(*tasks, return_exceptions=True)

        # Verify outcomes
        from typing import Any, cast

        assert not isinstance(results[0], Exception)  # First succeeded
        result0 = cast(Any, results[0])
        assert result0.data.image_url == "https://example.com/image1.jpg"

        assert isinstance(results[1], Exception)  # Second failed
        assert "Task 2 failed" in str(results[1])

        assert not isinstance(results[2], Exception)  # Third succeeded
        result2 = cast(Any, results[2])
        assert result2.data.image_url == "https://example.com/image3.jpg"
