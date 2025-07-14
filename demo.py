"""Demo script showing all ModelScope MCP server capabilities."""

import asyncio

from fastmcp import Client

from modelscope_mcp_server.server import create_mcp_server
from modelscope_mcp_server.settings import settings


async def main():
    print("🤖 ModelScope MCP server demo\n")

    # Show configuration
    print("📋 Current configuration:")
    print(f"   API Key: {settings.api_key}")
    print(f"   API Base URL: {settings.api_base_url}")
    print(f"   OpenAPI Base URL: {settings.openapi_base_url}")
    print(f"   API Inference Base URL: {settings.api_inference_base_url}")
    print(
        f"   Default Image Generation Model: {settings.default_image_generation_model}"
    )
    print(f"   Log level: {settings.log_level}")
    print()

    mcp = create_mcp_server()

    async with Client(mcp) as client:
        print("1. Calling get_current_user tool\n")

        user_result = await client.call_tool("get_current_user", {})

        if user_result.content and len(user_result.content) > 0:
            user_info = user_result.content[0].text  # type: ignore
            print(f"✅ Current user info: {user_info}\n")

        print("2. Calling search_papers tool\n")

        result = await client.call_tool(
            "search_papers",
            {"query": "Qwen3", "page_number": 1, "page_size": 1},
        )

        if result.content and len(result.content) > 0:
            papers = result.content[0].text  # type: ignore
            print(f"✅ Search papers: {papers}\n")

        print("3. Calling generate_image_url_from_text tool (using default model)\n")

        result = await client.call_tool(
            "generate_image_url_from_text",
            {
                "description": "A curious cat wearing a tiny wizard hat, casting magical rainbow sparkles while riding a flying donut through a candy cloud kingdom",
            },
        )

        if result.content and len(result.content) > 0:
            image_url = result.content[0].text  # type: ignore
            print(f"✅ Generated image URL: {image_url}\n")

        print("✨ Demo complete!")


if __name__ == "__main__":
    asyncio.run(main())
