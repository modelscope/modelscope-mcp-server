from fastmcp import Client


async def test_get_environment_info(mcp_server):
    """Test get_environment_info tool returns valid environment information."""
    async with Client(mcp_server) as client:
        result = await client.call_tool("get_environment_info", {})

        assert hasattr(result, "data"), "Result should have data attribute"
        env_info = result.data

        print(f"✅ Received environment info: {env_info}\n")

        assert env_info.server_version is not None, "Server version should be present"
        assert env_info.fastmcp_version is not None, "FastMCP version should be present"
        assert env_info.mcp_protocol_version is not None, "MCP protocol version should be present"
        assert env_info.python_version is not None, "Python version should be present"
