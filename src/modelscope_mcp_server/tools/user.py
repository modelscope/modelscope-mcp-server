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
        Get current authenticated user information from ModelScope (魔搭社区).
        """
        if not settings.api_key:
            return UserInfo(
                authenticated=False,
                username=None,
                email=None,
                avatar_url=None,
                description=None,
            )

        url = "https://modelscope.cn/api/v1/users/login/info"
        headers = {
            # NOTE this is just a hack, may be changed in the future
            "Cookie": f"m_session_id={settings.api_key}",
            "User-Agent": "modelscope-mcp-server",
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()

        if not data.get("Success", False):
            logger.error(f"API call failed: {data.get('Message', 'Unknown error')}")
            return UserInfo(
                authenticated=False,
                username=None,
                email=None,
                avatar_url=None,
                description=None,
            )

        user_data = data.get("Data", {})

        return UserInfo(
            authenticated=True,
            username=user_data.get("Name"),
            email=user_data.get("Email"),
            avatar_url=user_data.get("Avatar"),
            description=user_data.get("Description"),
        )
