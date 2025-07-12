"""ModelScope MCP Server"""

from .server import mcp

__version__ = "0.1.1"


def main():
    """Main entry point for ModelScope MCP Server"""
    from .cli import main as cli_main

    cli_main()


__all__ = ["main", "__version__", "mcp"]
