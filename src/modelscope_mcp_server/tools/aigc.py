"""ModelScope MCP Server AIGC tools.

Provides MCP tools for text-to-image generation, etc.
"""

from typing import Annotated

from fastmcp import FastMCP
from fastmcp.utilities import logging
from pydantic import Field

from ..client import default_client
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
                "If not provided, the default model for the corresponding generation type (text-to-image or image-to-image) is used."
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

        url = f"{settings.api_inference_domain}/v1/images/generations"

        payload = {
            "model": model,
            "prompt": prompt,
        }

        if generation_type == GenerationType.IMAGE_TO_IMAGE and image_url:
            payload["image_url"] = image_url

        response = default_client.post(
            url, json_data=payload, timeout=settings.default_image_generation_timeout_seconds
        )

        images_data = response.get("images", [])

        if len(images_data) == 0:
            raise Exception(f"No images found in response: {response}")

        generated_image_url = images_data[0].get("url", "")
        if len(generated_image_url) == 0:
            raise Exception(f"No image URL found in response: {response}")

        return ImageGenerationResult(
            type=generation_type,
            model=model,
            image_url=generated_image_url,
        )
