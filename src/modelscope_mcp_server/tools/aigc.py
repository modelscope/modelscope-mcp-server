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
from ..types import ImageGenerationResult

logger = logging.get_logger(__name__)


def register_aigc_tools(mcp: FastMCP) -> None:
    """
    Register all AIGC-related tools with the MCP server.

    Args:
        mcp (FastMCP): The MCP server instance
    """

    @mcp.tool(
        annotations={
            "title": "Generate Image URL from Text",
            "destructiveHint": False,
        }
    )
    async def generate_image_url_from_text(
        description: Annotated[
            str,
            Field(
                description="The description of the image to be generated, containing the desired elements and visual features."
            ),
        ],
        model: Annotated[
            str | None,
            Field(
                description="The model name to be used for image generation. If not provided, uses the default model from settings."
            ),
        ] = None,
    ) -> ImageGenerationResult:
        """Generate an image from the input description using ModelScope API."""

        # Use default model if not specified
        if model is None:
            model = settings.default_image_generation_model

        if not description or not description.strip():
            raise ValueError("Description cannot be empty")

        if not model:
            raise ValueError("Model name cannot be empty")

        if not settings.is_api_token_configured():
            raise ValueError("API token is not set")

        url = f"{settings.api_inference_base_url}/images/generations"

        payload = {
            "model": model,
            "prompt": description,
        }

        headers = {
            "Authorization": f"Bearer {settings.api_token}",
            "Content-Type": "application/json",
            "User-Agent": "modelscope-mcp-server",
        }

        logger.info(
            f"Sending image generation request with model '{model}' and description '{description}'"
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
            image_url = response_data["images"][0]["url"]
            logger.info(f"Successfully generated image URL: {image_url}")
            return ImageGenerationResult(model_used=model, image_url=image_url)

        raise Exception(f"Server returned error: {response_data}")
