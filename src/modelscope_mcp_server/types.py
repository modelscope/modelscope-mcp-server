"""Type definitions for ModelScope MCP server."""

from typing import Annotated

from pydantic import BaseModel, Field


class UserInfo(BaseModel):
    """User information."""

    authenticated: Annotated[
        bool, Field(description="Whether the user is authenticated")
    ]
    reason: Annotated[
        str | None, Field(description="Reason for failed authentication")
    ] = None
    username: Annotated[str | None, Field(description="Username")] = None
    email: Annotated[str | None, Field(description="Email")] = None
    avatar_url: Annotated[str | None, Field(description="Avatar URL")] = None
    description: Annotated[str | None, Field(description="Description")] = None


class ImageGenerationResult(BaseModel):
    """Image generation result."""

    model_used: Annotated[str, Field(description="Model used for image generation")]
    image_url: Annotated[str, Field(description="URL of the generated image")]


class Paper(BaseModel):
    """Paper information."""

    # Basic information
    arxiv_id: Annotated[str, Field(description="Arxiv ID")]
    title: Annotated[str, Field(description="Title")]
    authors: Annotated[str, Field(description="Authors")]
    publish_date: Annotated[str, Field(description="Publish date")]
    abstract_cn: Annotated[str, Field(description="Abstract in Chinese")]
    abstract_en: Annotated[str, Field(description="Abstract in English")]

    # Links
    modelscope_url: Annotated[str, Field(description="ModelScope page URL")]
    arxiv_url: Annotated[str, Field(description="Arxiv page URL")]
    pdf_url: Annotated[str, Field(description="PDF URL")]
    code_link: Annotated[str | None, Field(description="Code link")] = None

    # Metrics
    view_count: Annotated[int, Field(description="View count")] = 0
    favorite_count: Annotated[int, Field(description="Favorite count")] = 0
    comment_count: Annotated[int, Field(description="Comment count")] = 0
