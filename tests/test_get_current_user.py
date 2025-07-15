import pytest
from fastmcp import Client

from modelscope_mcp_server.settings import settings


@pytest.mark.asyncio
async def test_get_current_user_with_api_token(mcp_server):
    if not settings.is_api_token_configured():
        pytest.skip("API token not configured, skipping test")

    async with Client(mcp_server) as client:
        result = await client.call_tool("get_current_user", {})

        assert hasattr(result, "data"), "Result should have data attribute"
        user_info = result.data

        print(f"✅ Received user info with API token: {user_info}\n")

        assert user_info.authenticated is True, (
            "User should be authenticated with valid API token"
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
async def test_get_current_user_no_api_token(mcp_server):
    """Test get_current_user when API token is not configured."""
    # Temporarily remove API token
    original_api_token = settings.api_token

    try:
        # Set API token to None
        settings.api_token = None

        async with Client(mcp_server) as client:
            result = await client.call_tool("get_current_user", {})

            assert hasattr(result, "data"), "Result should have data attribute"
            user_info = result.data

            print(f"✅ Received user info without API token: {user_info}\n")

            assert user_info.authenticated is False, (
                "User should not be authenticated without API token"
            )
            assert "API token is not set" in user_info.reason, (
                "Should have correct error reason"
            )

    finally:
        # Restore original API token
        settings.api_token = original_api_token


@pytest.mark.asyncio
async def test_get_current_user_invalid_api_token(mcp_server):
    """Test get_current_user when API token is invalid."""
    # Temporarily set invalid API token
    original_api_token = settings.api_token

    try:
        # Set invalid API token
        settings.api_token = "invalid-api-token"

        async with Client(mcp_server) as client:
            result = await client.call_tool("get_current_user", {})

            assert hasattr(result, "data"), "Result should have data attribute"
            user_info = result.data

            print(f"✅ Received user info with empty API token: {user_info}\n")

            assert user_info.authenticated is False, (
                "User should not be authenticated with empty API token"
            )
            assert "Invalid API token" in user_info.reason, (
                "Should have correct error reason"
            )

    finally:
        # Restore original API token
        settings.api_token = original_api_token
