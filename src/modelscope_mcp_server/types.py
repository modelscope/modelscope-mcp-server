"""Type definitions for ModelScope MCP server."""

from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field


class GenerationType(str, Enum):
    """Content generation types."""

    TEXT_TO_IMAGE = "text-to-image"
    IMAGE_TO_IMAGE = "image-to-image"


class UserInfo(BaseModel):
    """User information."""

    # Authentication result
    authenticated: Annotated[bool, Field(description="Whether the user is authenticated")]
    reason: Annotated[str | None, Field(description="Reason for failed authentication")] = None

    # Basic information
    username: Annotated[str | None, Field(description="Username")] = None
    email: Annotated[str | None, Field(description="Email")] = None
    avatar_url: Annotated[str | None, Field(description="Avatar URL")] = None
    description: Annotated[str | None, Field(description="Description")] = None

    # Links
    modelscope_url: Annotated[str | None, Field(description="Profile page URL on ModelScope")] = None


class Model(BaseModel):
    """Model information."""

    # Basic information
    id: Annotated[str, Field(description="Unique model ID, formatted as 'path/name'")]
    path: Annotated[str, Field(description="Model path, for example 'deepseek-ai'")]
    name: Annotated[str, Field(description="Model name, for example 'DeepSeek-R1'")]
    chinese_name: Annotated[str, Field(description="Chinese name")]
    created_by: Annotated[str, Field(description="User who created the model")]
    license: Annotated[str, Field(description="Open source license")]

    # Links
    modelscope_url: Annotated[str, Field(description="Detail page URL on ModelScope")]

    # Capabilities
    support_inference: Annotated[bool, Field(description="Whether the model supports inference API")] = False

    # Metrics
    downloads_count: Annotated[int, Field(description="Number of downloads")] = 0
    stars_count: Annotated[int, Field(description="Number of stars")] = 0

    # Timestamps
    created_at: Annotated[int, Field(description="Created time (unix timestamp, seconds)")] = 0
    updated_at: Annotated[int, Field(description="Last updated time (unix timestamp, seconds)")] = 0


class Dataset(BaseModel):
    """Dataset information."""

    # Basic information
    id: Annotated[str, Field(description="Unique dataset ID, formatted as 'path/name'")]
    path: Annotated[str, Field(description="Dataset path, for example 'opencompass'")]
    name: Annotated[str, Field(description="Dataset name, for example 'mmlu'")]
    chinese_name: Annotated[str, Field(description="Chinese name")]
    created_by: Annotated[str, Field(description="User who created the dataset")]
    license: Annotated[str, Field(description="Open source license")]

    # Links
    modelscope_url: Annotated[str, Field(description="Detail page URL on ModelScope")]

    # Metrics
    downloads_count: Annotated[int, Field(description="Number of downloads")] = 0
    likes_count: Annotated[int, Field(description="Number of likes")] = 0

    # Timestamps
    created_at: Annotated[int, Field(description="Created time (unix timestamp, seconds)")] = 0
    updated_at: Annotated[int, Field(description="Last updated time (unix timestamp, seconds)")] = 0


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
    modelscope_url: Annotated[str, Field(description="Detail page URL on ModelScope")]
    arxiv_url: Annotated[str, Field(description="Arxiv page URL")]
    pdf_url: Annotated[str, Field(description="PDF URL")]
    code_link: Annotated[str | None, Field(description="Code link")] = None

    # Metrics
    view_count: Annotated[int, Field(description="View count")] = 0
    favorite_count: Annotated[int, Field(description="Favorite count")] = 0
    comment_count: Annotated[int, Field(description="Comment count")] = 0


class McpServer(BaseModel):
    """MCP Server information."""

    # Basic information
    id: Annotated[str, Field(description="MCP Server ID")]
    name: Annotated[str, Field(description="MCP Server name")]
    chinese_name: Annotated[str, Field(description="Chinese name")]
    description: Annotated[str, Field(description="Description")]
    publisher: Annotated[str, Field(description="Publisher")]
    tags: Annotated[list[str], Field(description="Tags")] = []

    # Links
    modelscope_url: Annotated[str, Field(description="Detail page URL on ModelScope")]

    # Metrics
    view_count: Annotated[int, Field(description="View count")] = 0


class ImageGenerationResult(BaseModel):
    """Image generation result."""

    type: Annotated[GenerationType, Field(description="Type of image generation")]
    model: Annotated[str, Field(description="Model used for image generation")]
    image_url: Annotated[str, Field(description="URL of the generated image")]


class EnvironmentInfo(BaseModel):
    """Environment information."""

    # Versions
    server_version: Annotated[str, Field(description="ModelScope MCP Server version")]
    fastmcp_version: Annotated[str, Field(description="FastMCP framework version")]
    mcp_protocol_version: Annotated[str, Field(description="MCP protocol version")]
    python_version: Annotated[str, Field(description="Python runtime version")]

    # Domains
    main_domain: Annotated[str, Field(description="ModelScope website domain")]
    api_inference_domain: Annotated[str, Field(description="ModelScope API inference domain")]

    # Settings
    default_text_to_image_model: Annotated[str, Field(description="Default text-to-image model")]
    default_image_to_image_model: Annotated[str, Field(description="Default image-to-image model")]
