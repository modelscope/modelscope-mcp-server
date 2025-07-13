import logging

from fastmcp import FastMCP
from fastmcp.server.middleware.error_handling import ErrorHandlingMiddleware
from fastmcp.server.middleware.logging import LoggingMiddleware
from fastmcp.server.middleware.rate_limiting import RateLimitingMiddleware
from fastmcp.server.middleware.timing import TimingMiddleware

from ._version import __version__
from .settings import settings
from .tools.aigc import register_aigc_tools

# Configure logging with settings
logging.basicConfig(level=getattr(logging, settings.log_level))
logger = logging.getLogger(__name__)


def create_mcp_server() -> FastMCP:
    """Create and configure the MCP server with all ModelScope tools."""

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

    return mcp
