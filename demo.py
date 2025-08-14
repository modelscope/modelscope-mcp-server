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

# Global counter for demo step numbering
demo_step = 0


def print_step_title(tool_name: str, task_description: str) -> None:
    """Print demo step title."""
    global demo_step
    demo_step += 1
    print(f"{demo_step}. 🛠️ Tool: {tool_name}")
    print(f"   • Task: {task_description}")


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
    tool_name = "get_current_user"
    print_step_title(tool_name, "👤 Get current user information")

    result = await client.call_tool(tool_name, {})
    data = parse_tool_response(result)

    username = data.get("username", "N/A")
    email = data.get("email", "N/A")
    authenticated = data.get("authenticated", "N/A")

    print(f"   • Result: Username={username}, Email={email}, Authenticated={authenticated}")
    print()


async def demo_environment_info(client: Client) -> None:
    """Demo getting environment information."""
    tool_name = "get_environment_info"
    print_step_title(tool_name, "🔧 Get current MCP server environment information")

    result = await client.call_tool(tool_name, {})
    data = parse_tool_response(result)

    print(f"   • Result: {data}")
    print()


async def demo_search_models(client: Client) -> None:
    """Demo searching models."""
    tool_name = "search_models"
    print_step_title(
        tool_name, "🔍 Search text-generation models (keyword='DeepSeek', support inference, limit 3 results)"
    )

    result = await client.call_tool(
        tool_name,
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


async def demo_search_datasets(client: Client) -> None:
    """Demo searching datasets."""
    tool_name = "search_datasets"
    print_step_title(tool_name, "📊 Search datasets (keyword='金融', sort='downloads', limit 3 results)")

    result = await client.call_tool(
        tool_name,
        {
            "query": "金融",
            "sort": "downloads",
            "limit": 3,
        },
    )
    data = parse_tool_response(result)

    if isinstance(data, list) and data:
        summaries = []
        for dataset in data:
            name = dataset.get("name", "N/A")
            chinese_name = dataset.get("chinese_name", "N/A")
            downloads = dataset.get("downloads_count", 0)
            likes = dataset.get("likes_count", 0)
            summaries.append(f"{name} ({chinese_name}) - Downloads {downloads:,}, Likes {likes}")
        print(f"   • Result: Found {len(data)} items - {' | '.join(summaries)}")
    else:
        print("   • Result: No datasets found")
    print()


async def demo_search_studios(client: Client) -> None:
    """Demo searching studios."""
    tool_name = "search_studios"
    print_step_title(tool_name, "🔍 Search studios (keyword='TTS', sort='VisitsCount', limit 3 results)")

    result = await client.call_tool(tool_name, {"query": "TTS", "sort": "VisitsCount", "limit": 3})
    data = parse_tool_response(result)

    if isinstance(data, list) and data:
        summaries = []
        for studio in data:
            name = studio.get("name", "N/A")
            chinese_name = studio.get("chinese_name", "N/A")
            status = studio.get("status", "N/A")
            stars = studio.get("stars", 0)
            visits = studio.get("visits", 0)

            summaries.append(f"{name} ({chinese_name}) - Status={status}, Stars={stars}, Visits={visits}")

        print(f"   • Result: Found {len(data)} items - {' | '.join(summaries)}")
    else:
        print("   • Result: No studios found")
    print()


async def demo_search_papers(client: Client) -> None:
    """Demo searching papers."""
    tool_name = "search_papers"
    print_step_title(tool_name, "📚 Search papers (keyword='Qwen3', sort='hot', limit 3 result)")

    result = await client.call_tool(
        tool_name,
        {
            "query": "Qwen3",
            "sort": "hot",
            "limit": 3,
        },
    )
    data = parse_tool_response(result)

    if isinstance(data, list) and data:
        summaries = []
        for paper in data:
            title = paper.get("title", "N/A")
            arxiv_id = paper.get("arxiv_id", "N/A")
            view_count = paper.get("view_count", 0)
            modelscope_url = paper.get("modelscope_url", "N/A")
            summaries.append(f"{title} (ArXiv={arxiv_id}, Views={view_count:,} URL={modelscope_url})")
        print(f"   • Result: Found {len(data)} items - {' | '.join(summaries)}")
    else:
        print("   • Result: No papers found")
    print()


async def demo_search_mcp_servers(client: Client) -> None:
    """Demo searching MCP servers."""
    tool_name = "search_mcp_servers"
    print_step_title(
        tool_name, "🔍 Search MCP servers (keyword='Chrome', category='browser-automation', limit 3 results)"
    )

    result = await client.call_tool(
        tool_name,
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
            view_count = server.get("view_count", 0)
            summaries.append(f"{name} (Views {view_count})")
        print(f"   • Result: Found {len(data)} items - {' | '.join(summaries)}")
    else:
        print("   • Result: No servers found")
    print()


async def demo_get_mcp_server_detail(client: Client) -> None:
    """Demo getting MCP server detail."""
    tool_name = "get_mcp_server_detail"
    server_id = "@modelscope/modelscope-mcp-server"
    print_step_title(tool_name, f"🔍 Get MCP server detail for '{server_id}'")

    result = await client.call_tool(
        tool_name,
        {
            "server_id": server_id,
        },
    )
    data = parse_tool_response(result)

    if data:
        name = data.get("name", "N/A")
        author = data.get("author", "N/A")
        description = data.get("description", "N/A")
        is_hosted = data.get("is_hosted", False)
        is_verified = data.get("is_verified", False)
        view_count = data.get("view_count", 0)
        github_stars = data.get("github_stars", 0)
        tags = ", ".join(data.get("tags", []))
        modelscope_url = data.get("modelscope_url", "N/A")

        print(f"   • Name: {name}")
        print(f"   • Author: {author}")
        print(f"   • Description: {description[:80]}{'...' if len(description) > 80 else ''}")
        print(f"   • Status: {'Hosted' if is_hosted else 'Not Hosted'}, {'Verified' if is_verified else 'Unverified'}")
        print(f"   • Metrics: {view_count:,} views, {github_stars:,} GitHub stars")
        print(f"   • Tags: {tags}")
        print(f"   • ModelScope URL: {modelscope_url}")
    else:
        print("   • Result: Server detail not found")
    print()


async def demo_generate_image(client: Client) -> None:
    """Demo image generation."""
    tool_name = "generate_image"
    prompt = 'Chinese calligraphy on parchment reading "ModelScope MCP Server by 魔搭社区" '
    print_step_title(tool_name, f"🎨 Generate image with prompt: {prompt}")

    result = await client.call_tool(tool_name, {"prompt": prompt})
    data = parse_tool_response(result)

    image_url = data.get("image_url", "N/A")
    model = data.get("model", "N/A")

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
        await demo_search_datasets(client)
        await demo_search_studios(client)
        await demo_search_papers(client)
        await demo_search_mcp_servers(client)
        await demo_get_mcp_server_detail(client)

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
