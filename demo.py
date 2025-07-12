"""Demo script showing all ModelScope MCP server capabilities."""

import asyncio

from fastmcp import Client

from modelscope_mcp_server.server import mcp
from modelscope_mcp_server.settings import settings


async def main():
    print("🤖 ModelScope MCP server demo\n")

    # Show configuration
    print("📋 Current configuration:")
    print(f"   API Key: {settings.api_key}")
    print(f"   API Inference Base URL: {settings.api_inference_base_url}")
    print(
        f"   Default Image Generation Model: {settings.default_image_generation_model}"
    )
    print(f"   Log level: {settings.log_level}")
    print()

    async with Client(mcp) as client:
        print("1. Calling generate_image_url_from_text tool (using default model)")
        print()

        result = await client.call_tool(
            "generate_image_url_from_text",
            {
                "description": "A curious cat wearing a tiny wizard hat, casting magical rainbow sparkles while riding a flying donut through a candy cloud kingdom",
            },
        )

        if result.content and len(result.content) > 0:
            image_url = result.content[0].text  # type: ignore
            print(f"✅ Generated image URL: {image_url}")

        print("\n✨ Demo complete!")


if __name__ == "__main__":
    asyncio.run(main())
