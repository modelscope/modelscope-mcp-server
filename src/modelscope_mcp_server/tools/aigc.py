"""
ModelScope MCP Server AIGC tools.

Provides MCP tools for image generation, etc.
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

    @mcp.tool()
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

        # Validate input parameters
        if not description or not description.strip():
            error_msg = "Error: Description cannot be empty"
            logger.error(error_msg)
            return ImageGenerationResult(
                success=False, error=error_msg, model_used=None, image_url=None
            )

        if not model or not model.strip():
            error_msg = "Error: Model name cannot be empty"
            logger.error(error_msg)
            return ImageGenerationResult(
                success=False, error=error_msg, model_used=None, image_url=None
            )

        # Check if API key is configured
        if not settings.is_api_key_configured():
            error_msg = "Error: MODELSCOPE_API_KEY environment variable is not set"
            logger.error(error_msg)
            return ImageGenerationResult(
                success=False, error=error_msg, model_used=None, image_url=None
            )

        # API endpoint and request configuration
        url = settings.images_endpoint

        payload = {
            "model": model,  # ModelScope Model-Id, required field
            "prompt": description,  # Required field
        }

        headers = {
            "Authorization": f"Bearer {settings.api_key}",
            "Content-Type": "application/json",
        }

        try:
            logger.info(
                f"Sending image generation request for model: {model}, with description: {description}"
            )

            # Send POST request to ModelScope API
            response = requests.post(
                url,
                data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                headers=headers,
                timeout=300,
            )

            # Check HTTP status code
            if response.status_code != 200:
                error_msg = f"Error: HTTP {response.status_code} - {response.text}"
                logger.error(error_msg)
                return ImageGenerationResult(
                    success=False, error=error_msg, model_used=None, image_url=None
                )

            # Parse response JSON
            response_data = response.json()

            # Extract image URL from response
            if "images" in response_data and response_data["images"]:
                image_url = response_data["images"][0]["url"]
                logger.info(f"Successfully generated image URL: {image_url}")
                return ImageGenerationResult(
                    success=True, model_used=model, image_url=image_url, error=None
                )
            else:
                # Return full response data if no image URL found
                error_msg = f"Error: No image URL in response - {str(response_data)}"
                logger.error(error_msg)
                return ImageGenerationResult(
                    success=False, error=error_msg, model_used=None, image_url=None
                )

        except requests.exceptions.Timeout:
            error_msg = "Error: Request timeout - please try again later"
            logger.error(error_msg)
            return ImageGenerationResult(
                success=False, error=error_msg, model_used=None, image_url=None
            )

        except requests.exceptions.ConnectionError:
            error_msg = (
                "Error: Connection failed - please check your internet connection"
            )
            logger.error(error_msg)
            return ImageGenerationResult(
                success=False, error=error_msg, model_used=None, image_url=None
            )

        except requests.exceptions.RequestException as e:
            error_msg = f"Error: Request failed - {str(e)}"
            logger.error(error_msg)
            return ImageGenerationResult(
                success=False, error=error_msg, model_used=None, image_url=None
            )

        except json.JSONDecodeError:
            error_msg = "Error: Invalid JSON response from API"
            logger.error(error_msg)
            return ImageGenerationResult(
                success=False, error=error_msg, model_used=None, image_url=None
            )

        except Exception as e:
            error_msg = f"Error: Unexpected error - {str(e)}"
            logger.error(error_msg)
            return ImageGenerationResult(
                success=False, error=error_msg, model_used=None, image_url=None
            )
