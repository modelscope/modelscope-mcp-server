import asyncio
from typing import cast

from fastmcp import FastMCP
from fastmcp import settings as fastmcp_settings
from fastmcp.server.middleware.error_handling import ErrorHandlingMiddleware
from fastmcp.server.middleware.logging import LoggingMiddleware
from fastmcp.server.middleware.rate_limiting import RateLimitingMiddleware
from fastmcp.server.middleware.timing import TimingMiddleware
from fastmcp.settings import LOG_LEVEL
from fastmcp.utilities import logging

from ._version import __version__
from .settings import settings
from .tools.aigc import register_aigc_tools

logger = logging.get_logger(__name__)


def create_mcp_server() -> FastMCP:
    """Create and configure the MCP server with all ModelScope tools."""

    fastmcp_settings.log_level = cast(LOG_LEVEL, settings.log_level)

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

    # Register all tools
    register_aigc_tools(mcp)

    async def log_mcp_server_stats():
        """Log stats about the MCP server."""
        tools = await mcp.get_tools()
        resources = await mcp.get_resources()
        prompts = await mcp.get_prompts()
        logger.debug(
            f"Created MCP server with {len(tools)} tools, {len(resources)} resources, and {len(prompts)} prompts"
        )

    asyncio.run(log_mcp_server_stats())

    return mcp
