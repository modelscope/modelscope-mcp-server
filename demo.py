"""Demo script showing core ModelScope MCP server capabilities."""

import argparse
import asyncio
import json
import os
import signal
import sys

from fastmcp import Client

from modelscope_mcp_server.server import create_mcp_server
from modelscope_mcp_server.settings import settings
from modelscope_mcp_server.utils.metadata import get_server_name_with_version


def parse_tool_response(result) -> dict:
    """Parse tool response and return JSON data."""
    if not result.content or len(result.content) == 0:
        raise RuntimeError("Tool response is empty or invalid")

    try:
        return json.loads(result.content[0].text)
    except (json.JSONDecodeError, AttributeError, IndexError) as e:
        raise RuntimeError(f"Failed to parse tool response: {e}") from e


async def demo_user_info(client: Client) -> None:
    """Demo getting current user information."""
    print("1. 🛠️ Tool: get_current_user")
    print("   • Task: 👤 Get current user information")

    result = await client.call_tool("get_current_user", {})
    data = parse_tool_response(result)

    username = data.get("username", "N/A")
    email = data.get("email", "N/A")
    authenticated = data.get("authenticated", "N/A")

    print(f"   • Result: Username={username}, Email={email}, Authenticated={authenticated}")
    print()


async def demo_environment_info(client: Client) -> None:
    """Demo getting environment information."""
    print("2. 🛠️ Tool: get_environment_info")
    print("   • Task: 🔧 Get current MCP server environment information")

    result = await client.call_tool("get_environment_info", {})
    data = parse_tool_response(result)

    print(f"   • Result: {data}")
    print()


async def demo_search_models(client: Client) -> None:
    """Demo searching models."""
    print("3. 🛠️ Tool: search_models")
    print("   • Task: 🔍 Search text-generation models (keyword='DeepSeek', support inference, limit 3 results)")

    result = await client.call_tool(
        "search_models",
        {
            "query": "DeepSeek",
            "task": "text-generation",
            "filters": ["support_inference"],
            "limit": 3,
        },
    )
    data = parse_tool_response(result)

    if isinstance(data, list) and data:
        summaries = []
        for model in data:
            name = model.get("name", "N/A")
            downloads = model.get("downloads_count", 0)
            stars = model.get("stars_count", 0)
            summaries.append(f"{name} (Downloads {downloads:,}, Stars {stars})")
        print(f"   • Result: Found {len(data)} items - {' | '.join(summaries)}")
    else:
        print("   • Result: No models found")
    print()


async def demo_search_papers(client: Client) -> None:
    """Demo searching papers."""
    print("4. 🛠️ Tool: search_papers")
    print("   • Task: 📚 Search academic papers (keyword='Qwen3', sort='hot', limit 1 result)")

    result = await client.call_tool(
        "search_papers",
        {
            "query": "Qwen3",
            "sort": "hot",
            "limit": 1,
        },
    )
    data = parse_tool_response(result)

    if isinstance(data, list) and data:
        paper = data[0]
        title = paper.get("title", "N/A")
        arxiv_id = paper.get("arxiv_id", "N/A")
        view_count = paper.get("view_count", 0)
        modelscope_url = paper.get("modelscope_url", "N/A")
        print(f"   • Result: '{title}' ArXiv ID={arxiv_id}, Views={view_count:,} ModelScope URL={modelscope_url}")
    else:
        print("   • Result: No papers found")
    print()


async def demo_search_mcp_servers(client: Client) -> None:
    """Demo searching MCP servers."""
    print("5. 🛠️ Tool: search_mcp_servers")
    print("   • Task: 🔍 Search MCP servers (keyword='Chrome', category='browser-automation', limit 3 results)")

    result = await client.call_tool(
        "search_mcp_servers",
        {
            "search": "Chrome",
            "category": "browser-automation",
            "limit": 3,
        },
    )
    data = parse_tool_response(result)

    if isinstance(data, list) and data:
        summaries = []
        for server in data:
            name = server.get("name", "N/A")
            publisher = server.get("publisher", "N/A")
            view_count = server.get("view_count", 0)
            summaries.append(f"{name} by {publisher} (Views {view_count})")
        print(f"   • Result: Found {len(data)} items - {' | '.join(summaries)}")
    else:
        print("   • Result: No servers found")
    print()


async def demo_generate_image(client: Client) -> None:
    """Demo image generation."""
    print("6. 🛠️ Tool: generate_image")
    print("   • Task: 🎨 Generate image (prompt='A curious cat wearing a tiny wizard hat in candy cloud kingdom')")

    result = await client.call_tool(
        "generate_image",
        {
            "prompt": "A curious cat wearing a tiny wizard hat in candy cloud kingdom",
        },
    )
    data = parse_tool_response(result)

    image_url = data.get("image_url")
    model = data.get("model")

    if not image_url:
        raise RuntimeError("Missing required field 'image_url' in response")
    if not model:
        raise RuntimeError("Missing required field 'model' in response")

    print(f"   • Result: Image generated using model '{model}' - URL: {image_url}")
    print()


def setup_signal_handler() -> None:
    """Set up signal handler for graceful shutdown."""

    def signal_handler(signum, frame):
        print("\n🛑 Demo interrupted by user")
        os._exit(0)

    signal.signal(signal.SIGINT, signal_handler)


async def main() -> None:
    """Run demo tasks."""
    parser = argparse.ArgumentParser(description="ModelScope MCP server demo")
    parser.add_argument(
        "--full",
        action="store_true",
        help="Run all demos including slow operations like image generation",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="WARNING",
        help="Set log level",
    )
    args = parser.parse_args()

    print(f"🤖 {get_server_name_with_version()} Demo")

    if not args.full:
        print("💡 Running basic demos only. Use --full to include slow demos (like image generation)")
    else:
        print("🚀 Running all demos including slow operations")

    settings.log_level = args.log_level
    settings.show_settings()

    mcp = create_mcp_server()

    async with Client(mcp) as client:
        await demo_user_info(client)
        await demo_environment_info(client)
        await demo_search_models(client)
        await demo_search_papers(client)
        await demo_search_mcp_servers(client)

        if args.full:
            await demo_generate_image(client)
        else:
            print("⏭️  Skipping image generation demo (use --full to enable)")
            print()

    print("✨ Demo complete!")


if __name__ == "__main__":
    setup_signal_handler()

    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        sys.exit(1)
