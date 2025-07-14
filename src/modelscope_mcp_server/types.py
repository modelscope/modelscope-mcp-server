"""Type definitions for ModelScope MCP server."""

from pydantic import BaseModel


class UserInfo(BaseModel):
    """User information."""

    authenticated: bool
    reason: str | None = None
    username: str | None = None
    email: str | None = None
    avatar_url: str | None = None
    description: str | None = None


class ImageGenerationResult(BaseModel):
    """Image generation result."""

    model_used: str | None = None
    image_url: str | None = None
