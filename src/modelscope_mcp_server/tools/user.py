"""
ModelScope MCP Server User tools.

Provides MCP tools for user-related operations, such as querying user information.
"""

import requests
from fastmcp import FastMCP
from fastmcp.utilities import logging

from ..settings import settings
from ..types import UserInfo

logger = logging.get_logger(__name__)


def register_user_tools(mcp: FastMCP) -> None:
    """
    Register all user-related tools with the MCP server.

    Args:
        mcp (FastMCP): The MCP server instance
    """

    @mcp.tool(
        annotations={
            "title": "Get Current User",
            "readOnlyHint": True,
        }
    )
    async def get_current_user() -> UserInfo:
        """
        Get current authenticated user information from ModelScope.
        """
        if not settings.is_api_token_configured():
            return UserInfo(authenticated=False, reason="API token is not set")

        # Should change to use the official OpenAPI when it's available
        url = f"{settings.api_base_url}/users/login/info"

        headers = {
            "Cookie": f"m_session_id={settings.api_token}",
            "User-Agent": "modelscope-mcp-server",
        }

        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 401 or response.status_code == 403:
            return UserInfo(
                authenticated=False,
                reason=f"Invalid API token: server returned {response.status_code}",
            )
        elif response.status_code != 200:
            raise Exception(
                f"Server returned non-200 status code: {response.status_code} {response.text}"
            )

        data = response.json()

        if not data.get("Success", False):
            raise Exception(f"Server returned error: {data}")

        user_data = data.get("Data", {})

        return UserInfo(
            authenticated=True,
            username=user_data.get("Name"),
            email=user_data.get("Email"),
            avatar_url=user_data.get("Avatar"),
            description=user_data.get("Description") or "",
        )
