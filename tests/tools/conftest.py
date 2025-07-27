"""
pytest configuration and shared fixtures for ModelScope MCP Server tests.
"""

import pytest

from modelscope_mcp_server.server import create_mcp_server


@pytest.fixture
def mcp_server():
    """
    Create MCP server with all tools registered.

    This fixture is shared across all test files and provides a
    configured MCP server instance with all ModelScope tools.

    Returns:
        FastMCP: Configured MCP server instance with all ModelScope tools
    """
    return create_mcp_server()
