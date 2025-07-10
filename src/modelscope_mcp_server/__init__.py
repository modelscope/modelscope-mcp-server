"""ModelScope MCP Server"""

from .server import mcp

__version__ = "0.1.1"


def main():
    """Main entry point for ModelScope MCP Server"""
    mcp.run(transport="stdio")


# Export the main function for entry point
__all__ = ["main", "__version__"]
