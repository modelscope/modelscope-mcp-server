"""Demo script showing all ModelScope MCP server capabilities."""

import asyncio

from fastmcp import Client

from modelscope_mcp_server.server import mcp


async def main():
    print("🤖 ModelScope MCP server demo\n")

    async with Client(mcp) as client:
        print("1. Calling generate_image_url_from_text tool")
        result = await client.call_tool(
            "generate_image_url_from_text",
            {
                "description": "A curious cat wearing a tiny wizard hat, casting magical rainbow sparkles while riding a flying donut through a candy cloud kingdom",
                "model": "epochcian/CANCANwatercolor_1",
            },
        )

        if result.content and len(result.content) > 0:
            image_url = result.content[0].text
            print(f"✅ Generated image URL: {image_url}")


if __name__ == "__main__":
    asyncio.run(main())
