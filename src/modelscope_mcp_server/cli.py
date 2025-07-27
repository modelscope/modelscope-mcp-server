"""Command line interface for ModelScope MCP Server."""

import argparse
import sys

from .server import create_mcp_server
from .utils.metadata import get_server_name, get_server_name_with_version, get_server_version


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description=get_server_name_with_version(),
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

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {get_server_version()}",
    )

    return parser


def validate_args(args: argparse.Namespace) -> None:
    """Validate parsed arguments."""
    if args.transport != "stdio" and args.port <= 0:
        raise ValueError("Port must be a positive integer for SSE/HTTP transport")


def main() -> None:
    """Handle CLI entry point operations."""
    parser = create_parser()
    args = parser.parse_args()

    try:
        validate_args(args)
    except ValueError as e:
        parser.error(str(e))

    # Create and configure the MCP server
    try:
        mcp = create_mcp_server()
    except Exception as e:
        print(f"Error creating MCP server: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        if args.transport == "stdio":
            mcp.run(
                transport=args.transport,
                show_banner=False,
            )
        else:
            mcp.run(
                transport=args.transport,
                port=args.port,
                show_banner=False,
            )
    except KeyboardInterrupt:
        print(f"\nShutting down {get_server_name()}...", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Error starting server: {e}", file=sys.stderr)
        sys.exit(1)
