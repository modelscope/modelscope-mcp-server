import pytest
from fastmcp import Client

from modelscope_mcp_server.settings import settings


@pytest.mark.integration
async def test_get_current_user_success(mcp_server):
    """Test successful get_current_user when API token is configured."""
    # Only run this test if API token is configured
    if not settings.is_api_token_configured():
        pytest.skip("API token not configured")

    async with Client(mcp_server) as client:
        result = await client.call_tool("get_current_user", {})

        assert hasattr(result, "data"), "Result should have data attribute"
        user_info = result.data

        print(f"✅ Received user info: {user_info}\n")

        assert user_info.authenticated is True, "User should be authenticated"
        assert user_info.username is not None, "Username should be present"
        assert user_info.email is not None, "Email should be present"
        assert user_info.modelscope_url is not None, "ModelScope URL should be present"


@pytest.mark.integration
async def test_get_current_user_no_api_token(mcp_server):
    """Test get_current_user when no API token is configured."""
    # Temporarily remove API token
    original_api_token = settings.api_token

    try:
        # Remove API token
        settings.api_token = None

        async with Client(mcp_server) as client:
            result = await client.call_tool("get_current_user", {})

            assert hasattr(result, "data"), "Result should have data attribute"
            user_info = result.data

            print(f"✅ Received user info with no API token: {user_info}\n")

            assert user_info.authenticated is False, "User should not be authenticated with no API token"
            assert "API token is not set" in user_info.reason, "Should have correct error reason"

    finally:
        # Restore original API token
        settings.api_token = original_api_token


@pytest.mark.integration
async def test_get_current_user_invalid_api_token(mcp_server, mocker):
    """Test get_current_user when API token is invalid."""
    # Store original API token
    original_api_token = settings.api_token

    try:
        # Clear the global client to force re-initialization with new token
        from modelscope_mcp_server.client import ModelScopeClient

        await ModelScopeClient.close_global_pool()

        # Set invalid API token
        settings.api_token = "invalid-api-token"

        async with Client(mcp_server) as client:
            result = await client.call_tool("get_current_user", {})

            assert hasattr(result, "data"), "Result should have data attribute"
            user_info = result.data

            print(f"✅ Received user info with invalid API token: {user_info}\n")

            assert user_info.authenticated is False, "User should not be authenticated with invalid API token"
            assert "Invalid API token" in user_info.reason, "Should have correct error reason"

    finally:
        # Restore original API token and close pool again to force re-init
        settings.api_token = original_api_token
        from modelscope_mcp_server.client import ModelScopeClient

        await ModelScopeClient.close_global_pool()
