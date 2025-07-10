"""ModelScope MCP Server"""

from .server import mcp

__version__ = "0.1.0"


def main():
    """Main entry point for ModelScope MCP Server"""
    mcp.run(transport="http", host="0.0.0.0", port=8000)


# Export the main function for entry point
__all__ = ["main", "__version__"]
