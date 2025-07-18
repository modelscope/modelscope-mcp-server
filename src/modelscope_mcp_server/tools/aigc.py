"""
ModelScope MCP Server AIGC tools.

Provides MCP tools for text-to-image generation, etc.
"""

import json
from typing import Annotated

import requests
from fastmcp import FastMCP
from fastmcp.utilities import logging
from pydantic import Field

from ..settings import settings
from ..types import GenerationType, ImageGenerationResult

logger = logging.get_logger(__name__)


def register_aigc_tools(mcp: FastMCP) -> None:
    """
    Register all AIGC-related tools with the MCP server.

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
                description="The prompt of the image to be generated, containing the desired elements and visual features."
            ),
        ],
        model: Annotated[
            str | None,
            Field(
                description="The model ID from ModelScope to be used for image generation. If not provided, uses the default model provided in server settings."
            ),
        ] = None,
        image_url: Annotated[
            str | None,
            Field(
                description="The URL of the source image for image-to-image generation. If not provided, performs text-to-image generation."
            ),
        ] = None,
    ) -> ImageGenerationResult:
        """
        Generate an image based on the given text prompt and ModelScope AIGC model ID.
        Supports both text-to-image and image-to-image generation.
        """

        generation_type = (
            GenerationType.IMAGE_TO_IMAGE if image_url else GenerationType.TEXT_TO_IMAGE
        )

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

        url = f"{settings.api_inference_base_url}/images/generations"

        payload = {
            "model": model,
            "prompt": prompt,
        }

        if generation_type == GenerationType.IMAGE_TO_IMAGE and image_url:
            payload["image_url"] = image_url

        headers = {
            "Authorization": f"Bearer {settings.api_token}",
            "Content-Type": "application/json",
            "User-Agent": "modelscope-mcp-server",
        }

        logger.info(
            f"Sending {generation_type.value} generation request with model '{model}' and prompt '{prompt}'"
        )

        try:
            response = requests.post(
                url,
                data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                headers=headers,
                timeout=300,
            )
        except requests.exceptions.Timeout:
            raise TimeoutError("Request timeout - please try again later")

        if response.status_code != 200:
            raise Exception(
                f"Server returned non-200 status code: {response.status_code} {response.text}"
            )

        response_data = response.json()

        if "images" in response_data and response_data["images"]:
            generated_image_url = response_data["images"][0]["url"]
            logger.info(f"Successfully generated image URL: {generated_image_url}")
            return ImageGenerationResult(
                type=generation_type,
                model=model,
                image_url=generated_image_url,
            )
        raise Exception(f"Server returned error: {response_data}")
