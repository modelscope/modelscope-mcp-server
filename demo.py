"""Demo script showing all ModelScope MCP server capabilities."""

import argparse
import asyncio
import json
import os
import signal
import sys

from fastmcp import Client

from modelscope_mcp_server import __version__
from modelscope_mcp_server.server import create_mcp_server
from modelscope_mcp_server.settings import settings


async def demo_get_current_user(client: Client) -> None:
    """Demo: Get current user information."""
    print("1. 🛠️ Tool: get_current_user")
    print("   • Task: 👤 Get current user information")

    user_result = await client.call_tool("get_current_user", {})

    if user_result.content and len(user_result.content) > 0:
        user_info = json.loads(user_result.content[0].text)  # type: ignore
        username = user_info.get("username", "N/A")
        email = user_info.get("email", "N/A")
        authenticated = user_info.get("authenticated", "N/A")
        print(
            f"   • Result: Username={username}, Email={email}, Authenticated={authenticated}"
        )
    else:
        print("   • Result: No user information retrieved")
    print()


async def demo_search_models(client: Client) -> None:
    """Demo: Search models using various parameters."""
    print("2. 🛠️ Tool: search_models")
    print(
        "   • Task: 🔍 Search text-generation models (keyword='DeepSeek', support inference, limit 3 results)"
    )

    result = await client.call_tool(
        "search_models",
        {
            "query": "DeepSeek",
            "task": "text-generation",
            "filters": ["support_inference"],
            "limit": 3,
        },
    )

    if result.content and len(result.content) > 0:
        models = json.loads(result.content[0].text)  # type: ignore
        model_summary = []
        for model in models:
            name = model.get("chinese_name", model.get("name", "N/A"))
            downloads = model.get("downloads_count", 0)
            stars = model.get("stars_count", 0)
            model_summary.append(f"{name}(Downloads {downloads:,}, Stars {stars})")
        print(f"   • Result: Found {len(models)} models - {' | '.join(model_summary)}")
    else:
        print("   • Result: No models found")
    print()


async def demo_search_papers(client: Client) -> None:
    """Demo: Search papers using query."""
    print("3. 🛠️ Tool: search_papers")
    print(
        "   • Task: 📚 Search academic papers (keyword='Qwen3', sort='hot', limit 1 result)"
    )

    result = await client.call_tool(
        "search_papers",
        {"query": "Qwen3", "sort": "hot", "limit": 1},
    )

    if result.content and len(result.content) > 0:
        papers = json.loads(result.content[0].text)  # type: ignore
        if papers:
            paper = papers[0]
            title = paper.get("title", "N/A")
            authors = paper.get("authors", "N/A")
            arxiv_id = paper.get("arxiv_id", "N/A")
            views = paper.get("view_count", 0)
            print(
                f"   • Result: '{title}' Authors={authors}, ArXiv ID={arxiv_id}, Views={views:,}"
            )
        else:
            print("   • Result: No papers found")
    else:
        print("   • Result: No papers found")
    print()


async def demo_search_mcp_servers(client: Client) -> None:
    """Demo: Search MCP servers using various parameters."""
    print("4. 🛠️ Tool: search_mcp_servers")
    print(
        "   • Task: 🔍 Search MCP servers (keyword='Chrome', category='browser-automation', limit 3 results)"
    )

    result = await client.call_tool(
        "search_mcp_servers",
        {
            "search": "Chrome",
            "category": "browser-automation",
            "limit": 3,
        },
    )

    if result.content and len(result.content) > 0:
        servers = json.loads(result.content[0].text)  # type: ignore
        server_summary = []
        for server in servers:
            name = server.get("chinese_name", server.get("name", "N/A"))
            publisher = server.get("publisher", "N/A")
            views = server.get("view_count", 0)
            server_summary.append(f"{name} by {publisher} (Views {views:,})")
        print(
            f"   • Result: Found {len(servers)} servers - {' | '.join(server_summary)}"
        )
    else:
        print("   • Result: No MCP servers found")
    print()


async def demo_generate_image(client: Client) -> None:
    """Demo: Generate image URL from text prompt."""
    print("5. 🛠️ Tool: generate_image")
    print(
        "   • Task: 🎨 Generate image (prompt='A curious cat wearing a tiny wizard hat in candy cloud kingdom')"
    )

    result = await client.call_tool(
        "generate_image",
        {
            "prompt": "A curious cat wearing a tiny wizard hat, casting magical rainbow sparkles while riding a flying donut through a candy cloud kingdom",
        },
    )

    if result.content and len(result.content) > 0:
        image_url = result.content[0].text  # type: ignore
        print(f"   • Result: Image generated successfully - {image_url}")
    else:
        print("   • Result: Image generation failed")
    print()


def setup_signal_handler():
    """Setup signal handler for graceful shutdown."""

    def signal_handler(signum, frame):
        print("\n🛑 Demo interrupted by user")
        os._exit(0)

    signal.signal(signal.SIGINT, signal_handler)


async def main():
    parser = argparse.ArgumentParser(description="ModelScope MCP server demo")
    parser.add_argument(
        "--full",
        action="store_true",
        help="Run all demos including slow ones (like image generation)",
    )
    args = parser.parse_args()

    print(f"🤖 ModelScope MCP Server Demo (v{__version__})")
    if not args.full:
        print(
            "💡 Running basic demos only. Use --full to include slow demos (like image generation)"
        )

    # Set log level to WARNING to avoid too many logs
    settings.log_level = "WARNING"
    settings.show_settings()

    mcp = create_mcp_server()

    async with Client(mcp) as client:
        await demo_get_current_user(client)
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
