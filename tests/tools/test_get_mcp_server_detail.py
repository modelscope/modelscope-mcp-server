import pytest
from fastmcp import Client


# Helper functions
async def get_mcp_server_detail_helper(client, server_id):
    """Helper function to get MCP server detail and validate basic response structure."""
    result = await client.call_tool("get_mcp_server_detail", {"server_id": server_id})
    assert hasattr(result, "data"), "Result should have data attribute"
    server_detail = result.data
    return server_detail


def print_server_detail_info(server_detail):
    """Print server detail information."""
    print(f"ID: {server_detail.id}")
    print(f"Name: {server_detail.name}")
    print(f"Author: {server_detail.author}")
    print(f"Description: {server_detail.description}")
    print(f"Is Hosted: {server_detail.is_hosted}")
    print(f"Is Verified: {server_detail.is_verified}")
    print(f"View Count: {server_detail.view_count}")
    print(f"GitHub Stars: {server_detail.github_stars}")
    print(f"Tags: {server_detail.tags}")
    print(f"Source URL: {server_detail.source_url}")
    print(f"Logo URL: {server_detail.logo_url}")
    print(f"ModelScope URL: {server_detail.modelscope_url}")
    print(f"Server Config: {server_detail.server_config}")
    print(f"Env Schema: {server_detail.env_schema}")
    print(f"Readme: {server_detail.readme}")


def validate_server_detail_fields(server_detail):
    """Validate that server detail has all required fields."""
    required_fields = [
        "id",
        "name",
        "description",
        "author",
        "tags",
        "env_schema",
        "server_config",
        "is_hosted",
        "is_verified",
        "modelscope_url",
        "source_url",
        "logo_url",
        "readme",
        "view_count",
        "github_stars",
    ]

    for field in required_fields:
        assert hasattr(server_detail, field), f"Server detail should have '{field}' attribute"

    # Validate field types
    assert isinstance(server_detail.id, str), "ID should be a string"
    assert isinstance(server_detail.name, str), "Name should be a string"
    assert isinstance(server_detail.tags, list), "Tags should be a list"
    assert isinstance(server_detail.is_hosted, bool), "is_hosted should be a boolean"
    assert isinstance(server_detail.is_verified, bool), "is_verified should be a boolean"
    assert isinstance(server_detail.view_count, int), "View count should be an integer"
    assert isinstance(server_detail.github_stars, int), "GitHub stars should be an integer"
    assert isinstance(server_detail.server_config, list), "Server config should be a list"
    assert isinstance(server_detail.env_schema, str), "Env schema should be a string"
    assert isinstance(server_detail.readme, str), "Readme should be a string"
    assert isinstance(server_detail.logo_url, str), "Logo URL should be a string"


@pytest.mark.integration
async def test_get_mcp_server_detail(mcp_server):
    """Test get_mcp_server_detail with a known server ID."""
    async with Client(mcp_server) as client:
        server_id = "@modelscope/modelscope-mcp-server"
        server_detail = await get_mcp_server_detail_helper(client, server_id)

        # Validate response structure
        validate_server_detail_fields(server_detail)

        # Print detailed information
        print(f"\n✅ Received MCP server detail for '{server_id}':")
        print_server_detail_info(server_detail)

        # Validate specific fields for known server
        assert server_detail.id == server_id, f"Server ID should be {server_id}"
        assert server_detail.author == "modelscope", "Author should be modelscope"
        assert server_detail.name != "", "Name should not be empty"
