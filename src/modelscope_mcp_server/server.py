import os
import json
import requests
import logging
from typing import List, Optional
from fastmcp import FastMCP
from mcp.types import TextContent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("ModelScope MCP Server")


@mcp.tool()
def generate_image_url_from_text(
    description: str, model: str = "MusePublic/489_ckpt_FLUX_1"
) -> List[TextContent]:
    """Generate an image from the input description using ModelScope API.

    This function sends a request to the ModelScope API to generate an image
    based on the provided text description and returns the image URL.

    Args:
        description: The description of the image to be generated, containing
                    the desired elements and visual features.
        model: The model name to be used for image generation.
               Default is "MusePublic/489_ckpt_FLUX_1".

    Returns:
        List[TextContent]: A list containing a single TextContent object with
                          the generated image URL or error message.

    Raises:
        None: All exceptions are caught and returned as error messages.
    """
    # Validate input parameters
    if not description or not description.strip():
        error_msg = "Error: Description cannot be empty"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]

    if not model or not model.strip():
        error_msg = "Error: Model name cannot be empty"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]

    # Get API token from environment
    token = os.environ.get("MODELSCOPE_API_KEY")
    if not token:
        error_msg = "Error: MODELSCOPE_API_KEY environment variable is not set"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]

    # API endpoint and request configuration
    url = "https://api-inference.modelscope.cn/v1/images/generations"

    payload = {
        "model": model,  # ModelScope Model-Id, required field
        "prompt": description,  # Required field
    }

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    try:
        logger.info(f"Sending image generation request for model: {model}")

        # Send POST request to ModelScope API
        response = requests.post(
            url,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers=headers,
            timeout=300,  # Add timeout for better reliability
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
