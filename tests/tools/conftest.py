"""
pytest configuration and shared fixtures for ModelScope MCP Server tests.
"""

import pytest

from modelscope_mcp_server.client import ModelScopeClient
from modelscope_mcp_server.server import create_mcp_server


@pytest.fixture
async def mcp_server():
    """
    Create MCP server with all tools registered.

    This fixture is shared across all test files and provides a
    configured MCP server instance with all ModelScope tools.

    Also ensures proper cleanup of the global connection pool after each test.

    Returns:
        FastMCP: Configured MCP server instance with all ModelScope tools
    """
    server = create_mcp_server()
    yield server
    # Clean up the global connection pool after each test
    await ModelScopeClient.close_global_pool()
