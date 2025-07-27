"""ModelScope MCP Server Context tools.

Provides MCP tools about the current context you are operating in, such as the current user.
"""

import requests
from fastmcp import FastMCP
from fastmcp.utilities import logging

from ..settings import settings
from ..types import EnvironmentInfo, UserInfo
from ..utils.metadata import get_fastmcp_version, get_mcp_protocol_version, get_python_version, get_server_version

logger = logging.get_logger(__name__)


def register_context_tools(mcp: FastMCP) -> None:
    """Register all context-related tools with the MCP server.

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
        """Get current authenticated user information from ModelScope.

        Use this when a request is about the user's own profile for ModelScope.
        Or when information is missing to build other tool calls.
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
            raise Exception(f"Server returned non-200 status code: {response.status_code} {response.text}")

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

    @mcp.tool(
        annotations={
            "title": "Get Environment Info",
            "readOnlyHint": True,
        }
    )
    async def get_environment_info() -> EnvironmentInfo:
        """Get current MCP server environment information.

        Returns version information for the server, FastMCP framework, MCP protocol, and Python runtime.
        Useful for debugging and compatibility checking.
        """
        return EnvironmentInfo(
            server_version=get_server_version(),
            fastmcp_version=get_fastmcp_version(),
            mcp_protocol_version=get_mcp_protocol_version(),
            python_version=get_python_version(),
        )
