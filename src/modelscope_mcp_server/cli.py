"""Command line interface for ModelScope MCP Server"""

import argparse
import sys

from .server import mcp


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="ModelScope MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                        # Run with stdio transport (default)
  %(prog)s --transport stdio      # Run with stdio transport
  %(prog)s --transport sse         # Run with SSE transport on port 8000 (default)
  %(prog)s --transport sse --port 8080    # Run with SSE transport on port 8080
  %(prog)s --transport http --port 3000   # Run with streamable HTTP transport on port 3000
        """,
    )

    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "http"],
        default="stdio",
        help="Transport type (default: stdio)",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port number for SSE/HTTP transport (default: 8000)",
    )

    # Import version from __init__.py to avoid circular imports
    from . import __version__

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    return parser


def validate_args(args: argparse.Namespace) -> None:
    """Validate parsed arguments."""
    if args.transport != "stdio" and args.port <= 0:
        raise ValueError("Port must be a positive integer for SSE/HTTP transport")


def run_server(args: argparse.Namespace) -> None:
    """Run the MCP server with the specified arguments."""
    try:
        mcp.run(transport=args.transport, port=args.port, show_banner=False)
    except KeyboardInterrupt:
        print("\nShutting down ModelScope MCP Server...", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Error starting server: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    try:
        validate_args(args)
        run_server(args)
    except ValueError as e:
        parser.error(str(e))
