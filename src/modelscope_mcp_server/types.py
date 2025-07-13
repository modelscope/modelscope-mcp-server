"""Type definitions for ModelScope MCP server."""

from typing import TypedDict


class ImageGenerationResult(TypedDict):
    """Image generation result."""

    success: bool
    model_used: str | None
    image_url: str | None
    error: str | None
