import json
import logging

import requests
from fastmcp import FastMCP
from mcp.types import TextContent

from ._version import __version__
from .settings import settings

# Configure logging with settings
logging.basicConfig(level=getattr(logging, settings.log_level))
logger = logging.getLogger(__name__)

mcp = FastMCP(f"ModelScope MCP Server v{__version__}")


@mcp.tool()
def generate_image_url_from_text(
    description: str, model: str | None = None
) -> list[TextContent]:
    """Generate an image from the input description using ModelScope API.

    This function sends a request to the ModelScope API to generate an image
    based on the provided text description and returns the image URL.

    Args:
        description: The description of the image to be generated, containing
                    the desired elements and visual features.
        model: The model name to be used for image generation.
               If not provided, uses the default model from settings.

    Returns:
        List[TextContent]: A list containing a single TextContent object with
                          the generated image URL or error message.

    Raises:
        None: All exceptions are caught and returned as error messages.
    """
    # Use default model if not specified
    if model is None:
        model = settings.default_image_generation_model

    # Validate input parameters
    if not description or not description.strip():
        error_msg = "Error: Description cannot be empty"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]

    if not model or not model.strip():
        error_msg = "Error: Model name cannot be empty"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]

    # Check if API key is configured
    if not settings.is_api_key_configured():
        error_msg = "Error: MODELSCOPE_API_KEY environment variable is not set"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]

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
        logger.info(f"Sending image generation request for model: {model}")

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
            return [TextContent(type="text", text=error_msg)]

        # Parse response JSON
        response_data = response.json()

        # Extract image URL from response
        if "images" in response_data and response_data["images"]:
            image_url = response_data["images"][0]["url"]
            logger.info(f"Successfully generated image URL: {image_url}")
            return [TextContent(type="text", text=image_url)]
        else:
            # Return full response data if no image URL found
            error_msg = f"Error: No image URL in response - {str(response_data)}"
            logger.error(error_msg)
            return [TextContent(type="text", text=error_msg)]

    except requests.exceptions.Timeout:
        error_msg = "Error: Request timeout - please try again later"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]

    except requests.exceptions.ConnectionError:
        error_msg = "Error: Connection failed - please check your internet connection"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]

    except requests.exceptions.RequestException as e:
        error_msg = f"Error: Request failed - {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]

    except json.JSONDecodeError:
        error_msg = "Error: Invalid JSON response from API"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]

    except Exception as e:
        error_msg = f"Error: Unexpected error - {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]
