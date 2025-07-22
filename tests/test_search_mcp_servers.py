import pytest
from fastmcp import Client


# Helper functions
async def search_mcp_servers_helper(client, params):
    """Helper function to search MCP servers and validate basic response structure."""
    result = await client.call_tool("search_mcp_servers", params)
    assert hasattr(result, "data"), "Result should have data attribute"
    servers = result.data
    assert isinstance(servers, list), "Servers should be a list"
    return servers


def print_server_info(server, extra_fields=None):
    """Print server information with optional extra fields."""
    base_info = (
        f"id: {server.get('id', '')} | "
        f"name: {server.get('name', '')} | "
        f"chinese_name: {server.get('chinese_name', '')} | "
        f"publisher: {server.get('publisher', '')}"
    )

    if extra_fields:
        for field in extra_fields:
            base_info += f" | {field}: {server.get(field, 0)}"

    print(base_info)


def print_servers_list(servers, description, extra_fields=None):
    """Print a list of servers with description and optional extra fields."""
    print(f"✅ Received {len(servers)} MCP servers {description}:")
    for server in servers:
        print_server_info(server, extra_fields)


def validate_server_fields(server):
    """Validate that server has all required fields."""
    required_fields = [
        "id",
        "name",
        "chinese_name",
        "description",
        "publisher",
        "tags",
        "view_count",
    ]

    for field in required_fields:
        assert field in server, f"Server should have {field}"


@pytest.mark.asyncio
async def test_search_mcp_servers(mcp_server):
    """Test basic MCP servers search."""
    async with Client(mcp_server) as client:
        servers = await search_mcp_servers_helper(
            client, {"search": "browser", "limit": 5}
        )

        print_servers_list(servers, "with 'browser' search", ["view_count"])

        assert len(servers) >= 0, "Servers list should not be negative"
        if len(servers) > 0:
            validate_server_fields(servers[0])


@pytest.mark.asyncio
async def test_search_mcp_servers_empty_search(mcp_server):
    """Test searching MCP servers with empty search term."""
    async with Client(mcp_server) as client:
        servers = await search_mcp_servers_helper(client, {"limit": 3})

        print_servers_list(servers, "with empty search", ["view_count"])


@pytest.mark.asyncio
async def test_search_mcp_servers_with_category_filter(mcp_server):
    """Test searching MCP servers with category filter."""
    async with Client(mcp_server) as client:
        servers = await search_mcp_servers_helper(
            client, {"search": "tool", "category": "developer-tools", "limit": 3}
        )

        print_servers_list(servers, "with developer-tools category", ["view_count"])


@pytest.mark.asyncio
async def test_search_mcp_servers_with_hosted_filter(mcp_server):
    """Test searching MCP servers with hosted filter."""
    async with Client(mcp_server) as client:
        servers = await search_mcp_servers_helper(
            client, {"search": "search", "is_hosted": True, "limit": 5}
        )

        print_servers_list(servers, "with hosted filter", ["view_count"])


@pytest.mark.asyncio
async def test_search_mcp_servers_multiple_categories(mcp_server):
    """Test searching MCP servers in different categories."""
    categories = ["browser-automation", "search", "developer-tools"]

    async with Client(mcp_server) as client:
        for category in categories:
            servers = await search_mcp_servers_helper(
                client, {"category": category, "limit": 2}
            )

            print_servers_list(servers, f"in {category} category", ["view_count"])


@pytest.mark.asyncio
async def test_search_mcp_servers_large_limit(mcp_server):
    """Test searching MCP servers with large limit."""
    async with Client(mcp_server) as client:
        servers = await search_mcp_servers_helper(
            client, {"search": "data", "limit": 20}
        )

        print_servers_list(servers, "with large limit", ["view_count"])

        # Should respect the limit
        assert len(servers) <= 20, "Should not exceed the specified limit"


@pytest.mark.asyncio
async def test_search_mcp_servers_all_filters(mcp_server):
    """Test searching MCP servers with all filters combined."""
    async with Client(mcp_server) as client:
        servers = await search_mcp_servers_helper(
            client,
            {
                "search": "automation",
                "category": "browser-automation",
                "is_hosted": False,
                "limit": 5,
            },
        )

        print_servers_list(servers, "with all filters", ["view_count"])
