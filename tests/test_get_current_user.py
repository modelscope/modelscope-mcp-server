import pytest
from fastmcp import Client

from modelscope_mcp_server.settings import settings


@pytest.mark.asyncio
async def test_get_current_user_with_api_key(mcp_server):
    if not settings.is_api_key_configured():
        pytest.skip("API key not configured, skipping test")

    async with Client(mcp_server) as client:
        result = await client.call_tool("get_current_user", {})

        assert hasattr(result, "data"), "Result should have data attribute"
        user_info = result.data

        print(f"✅ Received user info with API key: {user_info}\n")

        assert user_info.authenticated is True, (
            "User should be authenticated with valid API key"
        )
        assert user_info.reason is None, (
            "No error reason should be present for authenticated user"
        )

        assert user_info.username is not None, (
            "Username should be present for authenticated user"
        )
        assert isinstance(user_info.username, str), "Username should be a string"
        assert len(user_info.username) > 0, "Username should not be empty"


@pytest.mark.asyncio
async def test_get_current_user_no_api_key(mcp_server):
    original_api_key = settings.api_key

    try:
        settings.api_key = None

        async with Client(mcp_server) as client:
            result = await client.call_tool("get_current_user", {})

            assert hasattr(result, "data"), "Result should have data attribute"
            user_info = result.data

            print(f"✅ Received user info without API key: {user_info}\n")

            assert user_info.authenticated is False, (
                "User should not be authenticated without API key"
            )
            assert "API key is not set" in user_info.reason, (
                "Should have correct error reason"
            )

    finally:
        settings.api_key = original_api_key


@pytest.mark.asyncio
async def test_get_current_user_invalid_api_key(mcp_server):
    """Test get_current_user when API key is invalid."""
    original_api_key = settings.api_key

    try:
        settings.api_key = "invalid-api-key"

        async with Client(mcp_server) as client:
            result = await client.call_tool("get_current_user", {})

            assert hasattr(result, "data"), "Result should have data attribute"
            user_info = result.data

            print(f"✅ Received user info with empty API key: {user_info}\n")

            assert user_info.authenticated is False, (
                "User should not be authenticated with empty API key"
            )
            assert "Invalid API key" in user_info.reason, (
                "Should have correct error reason"
            )

    finally:
        settings.api_key = original_api_key
