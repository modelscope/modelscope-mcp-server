"""ModelScope MCP Server"""

from ._version import __version__
from .settings import settings


def main():
    """Main entry point for ModelScope MCP Server"""
    from .cli import main as cli_main

    cli_main()


__all__ = ["main", "__version__", "settings"]
