"""Demo script showing all ModelScope MCP server capabilities."""

import asyncio

from fastmcp import Client

from modelscope_mcp_server.server import create_mcp_server
from modelscope_mcp_server.settings import settings


async def demo_get_current_user(client: Client) -> None:
    """Demo: Get current user information."""
    print("1. Calling get_current_user tool\n")

    user_result = await client.call_tool("get_current_user", {})

    if user_result.content and len(user_result.content) > 0:
        user_info = user_result.content[0].text  # type: ignore
        print(f"✅ Current user info: {user_info}\n")


async def demo_search_papers(client: Client) -> None:
    """Demo: Search papers using query."""
    print("2. Calling search_papers tool\n")

    result = await client.call_tool(
        "search_papers",
        {"query": "Qwen3", "page_number": 1, "page_size": 1},
    )

    if result.content and len(result.content) > 0:
        papers = result.content[0].text  # type: ignore
        print(f"✅ Search papers: {papers}\n")


async def demo_generate_image(client: Client) -> None:
    """Demo: Generate image URL from text prompt."""
    print("3. Calling generate_image tool (using default model)\n")

    result = await client.call_tool(
        "generate_image",
        {
            "prompt": "A curious cat wearing a tiny wizard hat, casting magical rainbow sparkles while riding a flying donut through a candy cloud kingdom",
        },
    )

    if result.content and len(result.content) > 0:
        image_url = result.content[0].text  # type: ignore
        print(f"✅ Generated image URL: {image_url}\n")


def show_configuration() -> None:
    """Display current configuration settings."""
    print("📋 Current configuration:")
    print(f"   API Token: {settings.api_token}")
    print(f"   API Base URL: {settings.api_base_url}")
    print(f"   OpenAPI Base URL: {settings.openapi_base_url}")
    print(f"   API Inference Base URL: {settings.api_inference_base_url}")
    print(
        f"   Default Image Generation Model: {settings.default_image_generation_model}"
    )
    print(f"   Log level: {settings.log_level}")
    print()


async def main():
    print("🤖 ModelScope MCP server demo\n")

    show_configuration()

    mcp = create_mcp_server()

    async with Client(mcp) as client:
        await demo_get_current_user(client)
        await demo_search_papers(client)
        await demo_generate_image(client)

        print("✨ Demo complete!")


if __name__ == "__main__":
    asyncio.run(main())
