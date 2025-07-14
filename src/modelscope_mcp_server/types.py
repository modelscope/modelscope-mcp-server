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


class Paper(BaseModel):
    """Paper information."""

    # Basic information
    id: int | None = None
    arxiv_id: str | None = None
    title: str | None = None
    authors: str | None = None
    publish_date: str | None = None
    abstract_cn: str | None = None
    abstract_en: str | None = None

    # Links
    pdf_url: str | None = None
    arxiv_url: str | None = None
    code_link: str | None = None

    # Metrics
    view_count: int | None = None
    favorite_count: int | None = None
    comment_count: int | None = None
