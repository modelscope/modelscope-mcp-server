"""测试 search_studios 工具的功能。"""

import pytest
from fastmcp import Client


# Helper functions
async def search_studios_helper(client, params):
    """Helper function to search studios and validate basic response structure."""
    result = await client.call_tool("search_studios", params)
    assert hasattr(result, "data"), "Result should have data attribute"
    studios = result.data
    assert isinstance(studios, list), "Studios should be a list"
    return studios


def print_studio_info(studio, extra_fields=None):
    """Print studio information with optional extra fields."""
    base_info = (
        f"id: {studio.get('id', '')} | "
        f"name: {studio.get('name', '')} | "
        f"chinese_name: {studio.get('chinese_name', '')} | "
        f"type: {studio.get('type', '')}"
    )

    if extra_fields:
        for field in extra_fields:
            base_info += f" | {field}: {studio.get(field, 0)}"

    print(base_info)


def print_studios_list(studios, description, extra_fields=None):
    """Print a list of studios with description and optional extra fields."""
    print(f"✅ Received {len(studios)} studios {description}:")
    for studio in studios:
        print_studio_info(studio, extra_fields)


def validate_studio_fields(studio):
    """Validate that studio has all required fields."""
    required_fields = [
        "id",
        "path",
        "name",
        "chinese_name",
        "description",
        "created_by",
        "license",
        "modelscope_url",
        "type",
        "status",
        "domains",
        "stars",
        "visits",
        "created_at",
        "updated_at",
        "deployed_at",
    ]

    for field in required_fields:
        assert field in studio, f"Studio should have {field}"


@pytest.mark.integration
async def test_search_studios(mcp_server):
    async with Client(mcp_server) as client:
        studios = await search_studios_helper(client, {"query": "ChatTTS", "limit": 5})

        print_studios_list(studios, "", ["stars"])

        assert len(studios) > 0, "Studios should not be empty"
        validate_studio_fields(studios[0])


@pytest.mark.integration
async def test_search_studios_with_domain_filter(mcp_server):
    async with Client(mcp_server) as client:
        studios = await search_studios_helper(client, {"query": "音频", "domains": ["audio"], "limit": 3})

        print_studios_list(studios, "with audio domain filter", ["visits"])

        # Verify that all returned studios have audio domain
        for studio in studios:
            assert "audio" in studio.get("domains", []), f"Studio {studio.get('id', '')} should have audio domain"


@pytest.mark.integration
async def test_search_studios_with_domain_filter_cv(mcp_server):
    async with Client(mcp_server) as client:
        studios = await search_studios_helper(client, {"domains": ["cv"], "limit": 3})

        print_studios_list(studios, "with cv domain filter", ["predicts"])

        # Verify that all returned studios have cv domain
        for studio in studios:
            assert "cv" in studio.get("domains", []), f"Studio {studio.get('id', '')} should have cv domain"


@pytest.mark.integration
async def test_search_studios_sort_by_stars(mcp_server):
    async with Client(mcp_server) as client:
        studios = await search_studios_helper(client, {"query": "生成", "sort": "StarsCount", "limit": 3})

        print_studios_list(studios, "sorted by stars", ["stars"])
