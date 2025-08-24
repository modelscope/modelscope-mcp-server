"""ModelScope MCP Server AIGC tools.

Provides MCP tools for text-to-image generation, etc.
"""

import asyncio
import time
from typing import Annotated

from fastmcp import FastMCP
from fastmcp.utilities import logging
from pydantic import Field

from ..client import get_client
from ..settings import settings
from ..types import GenerationType, ImageGenerationResult

logger = logging.get_logger(__name__)


def register_aigc_tools(mcp: FastMCP) -> None:
    """Register all AIGC-related tools with the MCP server.

    Args:
        mcp (FastMCP): The MCP server instance

    """

    @mcp.tool(
        annotations={
            "title": "Generate Image",
            "destructiveHint": False,
        }
    )
    async def generate_image(
        prompt: Annotated[
            str,
            Field(
                description="The prompt of the image to be generated, "
                "containing the desired elements and visual features."
            ),
        ],
        model: Annotated[
            str | None,
            Field(
                description="The model's ID to be used for image generation. "
                "If not provided, the default model for the corresponding generation type "
                "(text-to-image or image-to-image) is used."
            ),
        ] = None,
        image_url: Annotated[
            str | None,
            Field(
                description="The URL of the source image for image-to-image generation."
                "If not provided, performs text-to-image generation."
            ),
        ] = None,
    ) -> ImageGenerationResult:
        """Generate an image based on the given text prompt and ModelScope AIGC model ID.

        Supports both text-to-image and image-to-image generation.
        """
        generation_type = GenerationType.IMAGE_TO_IMAGE if image_url else GenerationType.TEXT_TO_IMAGE

        # API Doc: https://www.modelscope.cn/docs/model-service/API-Inference/intro

        # Use default model if not specified
        if model is None:
            model = (
                settings.default_text_to_image_model
                if generation_type == GenerationType.TEXT_TO_IMAGE
                else settings.default_image_to_image_model
            )

        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        if not model:
            raise ValueError("Model name cannot be empty")

        if not settings.is_api_token_configured():
            raise ValueError("API token is not set")

        # Step 1: submit async generation task
        submit_url = f"{settings.api_inference_domain}/v1/images/generations"

        payload = {
            "model": model,
            "prompt": prompt,
        }

        if generation_type == GenerationType.IMAGE_TO_IMAGE and image_url:
            payload["image_url"] = image_url

        client = get_client()
        submit_response = await client.post(
            submit_url,
            payload,
            timeout=settings.default_image_generation_timeout_seconds,
            headers={"X-ModelScope-Async-Mode": "true"},
        )

        task_id = submit_response.get("task_id")
        if not task_id:
            raise RuntimeError(f"No task_id found in response: {submit_response}")

        # Step 2: poll task result until succeed/failed or timeout
        start_time = time.time()
        task_url = f"{settings.api_inference_domain}/v1/tasks/{task_id}"
        attempt_count = 0

        while attempt_count < settings.max_poll_attempts:
            # timeout check
            if time.time() - start_time > settings.default_image_generation_timeout_seconds:
                raise TimeoutError("Image generation timed out - please try again later")

            attempt_count += 1

            task_result = await client.get(
                task_url,
                timeout=settings.default_api_timeout_seconds,
                headers={"X-ModelScope-Task-Type": "image_generation"},
            )

            status = task_result.get("task_status")

            if status == "SUCCEED":
                output_images = task_result.get("output_images") or []
                if not output_images:
                    raise RuntimeError(f"No output images found in task result: {task_result}")
                generated_image_url = output_images[0]
                return ImageGenerationResult(
                    type=generation_type,
                    model=model,
                    image_url=generated_image_url,
                )

            if status == "FAILED":
                error_msg = "Unknown error"
                if "errors" in task_result and isinstance(task_result["errors"], dict):
                    error_msg = task_result["errors"].get("message", error_msg)
                request_id = task_result.get("request_id", "N/A")
                raise RuntimeError(
                    f"Image generation failed: {error_msg}. Task ID: {task_id}, Request ID: {request_id}"
                )

            logger.info(
                f"Image generation task {task_id} is {status}, waiting for next poll... "
                f"(attempt {attempt_count}/{settings.max_poll_attempts})"
            )
            await asyncio.sleep(settings.task_poll_interval_seconds)

        # If we exit the loop without success or failure, max attempts exceeded
        raise TimeoutError(
            f"Image generation exceeded maximum polling attempts ({settings.max_poll_attempts}). Task ID: {task_id}"
        )
