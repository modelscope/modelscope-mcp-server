"""ModelScope MCP Server Context tools.

Provides MCP tools about the current context you are operating in, such as the current user.
"""

from fastmcp import FastMCP
from fastmcp.utilities import logging
from httpx import HTTPStatusError

from modelscope_mcp_server.client import get_client

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

        url = f"{settings.main_domain}/api/v1/users/login/info"

        try:
            client = get_client()
            response = await client.get(url)
        except HTTPStatusError as e:
            if e.response.status_code == 401 or e.response.status_code == 403:
                return UserInfo(
                    authenticated=False,
                    reason=f"Invalid API token: {str(e)}",
                )
            raise

        user_data = response.get("Data", {})

        username = user_data.get("Name")
        modelscope_url = f"{settings.main_domain}/profile/{username}"

        return UserInfo(
            authenticated=True,
            username=username,
            email=user_data.get("Email"),
            avatar_url=user_data.get("Avatar"),
            description=user_data.get("Description") or "",
            modelscope_url=modelscope_url,
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
            main_domain=settings.main_domain,
            api_inference_domain=settings.api_inference_domain,
            default_text_to_image_model=settings.default_text_to_image_model,
            default_image_to_image_model=settings.default_image_to_image_model,
        )
