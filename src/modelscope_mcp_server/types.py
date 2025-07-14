"""Type definitions for ModelScope MCP server."""

from typing import TypedDict


class UserInfo(TypedDict):
    """User information."""

    authenticated: bool
    username: str | None
    email: str | None
    avatar_url: str | None
    description: str | None


class ImageGenerationResult(TypedDict):
    """Image generation result."""

    success: bool
    model_used: str | None
    image_url: str | None
    error: str | None
