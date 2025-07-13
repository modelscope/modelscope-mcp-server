import json
import logging
from typing import Annotated

import requests
from fastmcp import FastMCP
from fastmcp.server.middleware.error_handling import ErrorHandlingMiddleware
from fastmcp.server.middleware.logging import LoggingMiddleware
from fastmcp.server.middleware.rate_limiting import RateLimitingMiddleware
from fastmcp.server.middleware.timing import TimingMiddleware
from pydantic import Field

from ._version import __version__
from .settings import settings
from .types import ImageGenerationResult

# Configure logging with settings
logging.basicConfig(level=getattr(logging, settings.log_level))
logger = logging.getLogger(__name__)

mcp = FastMCP(
    name=f"ModelScope MCP Server v{__version__}",
    instructions="""
        This server provides tools for calling ModelScope API.
    """,
)

# Add middleware in logical order
mcp.add_middleware(ErrorHandlingMiddleware(include_traceback=True))
mcp.add_middleware(RateLimitingMiddleware(max_requests_per_second=10))
mcp.add_middleware(TimingMiddleware())
mcp.add_middleware(LoggingMiddleware())


@mcp.tool()
def generate_image_url_from_text(
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
        error_msg = "Error: Connection failed - please check your internet connection"
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
