"""ModelScope MCP Server implementation."""

from typing import cast

from fastmcp import FastMCP
from fastmcp.server.middleware.error_handling import ErrorHandlingMiddleware
from fastmcp.server.middleware.logging import LoggingMiddleware
from fastmcp.server.middleware.rate_limiting import RateLimitingMiddleware
from fastmcp.server.middleware.timing import TimingMiddleware
from fastmcp.settings import LOG_LEVEL
from fastmcp.utilities import logging
from fastmcp.utilities.logging import configure_logging

from .settings import settings
from .tools.aigc import register_aigc_tools
from .tools.context import register_context_tools
from .tools.dataset import register_dataset_tools
from .tools.mcp import register_mcp_tools
from .tools.model import register_model_tools
from .tools.paper import register_paper_tools
from .tools.studio import register_studio_tools
from .utils.metadata import get_server_name_with_version

logger = logging.get_logger(__name__)


def create_mcp_server() -> FastMCP:
    """Create and configure the MCP server with all ModelScope tools."""
    configure_logging(level=cast(LOG_LEVEL, settings.log_level))

    mcp = FastMCP(
        name=get_server_name_with_version(),
        instructions="This server provides tools for calling ModelScope (魔搭社区) API.",
    )

    # Add middleware in logical order
    mcp.add_middleware(ErrorHandlingMiddleware(logger=logger))
    mcp.add_middleware(RateLimitingMiddleware(max_requests_per_second=10))
    mcp.add_middleware(TimingMiddleware())
    mcp.add_middleware(LoggingMiddleware())

    # Register all tools
    register_context_tools(mcp)
    register_model_tools(mcp)
    register_dataset_tools(mcp)
    register_studio_tools(mcp)
    register_paper_tools(mcp)
    register_mcp_tools(mcp)
    register_aigc_tools(mcp)

    return mcp
