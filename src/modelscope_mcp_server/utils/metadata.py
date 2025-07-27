"""Metadata utilities for version information."""

import sys
from importlib import metadata

from .. import __version__


def get_server_name() -> str:
    """Get ModelScope MCP Server name.

    Returns:
        str: Server name without version

    """
    return "ModelScope MCP Server"


def get_server_name_with_version() -> str:
    """Get ModelScope MCP Server name with version.

    Returns:
        str: Server name with version (e.g., "ModelScope MCP Server v1.0.0")

    """
    return f"{get_server_name()} v{get_server_version()}"


def get_server_version() -> str:
    """Get ModelScope MCP Server version.

    Returns:
        str: Server version string

    """
    return __version__


def get_fastmcp_version() -> str:
    """Get FastMCP framework version.

    Returns:
        str: FastMCP version string, or "unknown" if not available

    """
    try:
        return metadata.version("fastmcp")
    except metadata.PackageNotFoundError:
        return "unknown"


def get_mcp_protocol_version() -> str:
    """Get MCP protocol version.

    Returns:
        str: MCP protocol version string, or "unknown" if not available

    """
    try:
        return metadata.version("mcp")
    except metadata.PackageNotFoundError:
        return "unknown"


def get_python_version() -> str:
    """Get Python runtime version.

    Returns:
        str: Python version in x.y.z format

    """
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
