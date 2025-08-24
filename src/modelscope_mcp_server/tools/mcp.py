"""ModelScope MCP Server MCP tools.

Provides tools for MCP-related operations in the ModelScope MCP Server, such as searching for MCP servers.
"""

from typing import Annotated, Literal

from fastmcp import FastMCP
from fastmcp.utilities import logging
from pydantic import Field

from ..client import get_client
from ..settings import settings
from ..types import McpServer, McpServerDetail

logger = logging.get_logger(__name__)


def register_mcp_tools(mcp: FastMCP) -> None:
    """Register all MCP-related tools with the MCP server.

    Args:
        mcp (FastMCP): The MCP server instance

    """

    @mcp.tool(
        annotations={
            "title": "Search MCP Servers",
        }
    )
    async def search_mcp_servers(
        search: Annotated[
            str,
            Field(description="Search keyword for MCP servers"),
        ] = "",
        category: Annotated[
            (
                Literal[
                    "browser-automation",
                    "search",
                    "communication",
                    "customer-and-marketing",
                    "developer-tools",
                    "entertainment-and-media",
                    "file-systems",
                    "finance",
                    "knowledge-and-memory",
                    "location-services",
                    "art-and-culture",
                    "research-and-data",
                    "calendar-management",
                    "other",
                ]
                | None
            ),
            Field(description=("Filter by category")),
        ] = None,
        is_hosted: Annotated[
            bool | None,
            Field(description="Filter by hosted status"),
        ] = None,
        limit: Annotated[int, Field(description="Maximum number of servers to return", ge=1, le=100)] = 10,
    ) -> list[McpServer]:
        """Search for MCP servers on ModelScope."""
        url = f"{settings.main_domain}/openapi/v1/mcp/servers"

        # Build filter object
        filter_obj = {}
        if category is not None:
            filter_obj["category"] = category
        if is_hosted is not None:
            filter_obj["is_hosted"] = is_hosted

        request_data = {
            "filter": filter_obj,
            "page_number": 1,
            "page_size": limit,
            "search": search,
        }

        client = get_client()
        response = await client.put(url, request_data)

        servers_data = response.get("data", {}).get("mcp_server_list", [])

        servers = []
        for server_data in servers_data:
            id = server_data.get("id", "")
            modelscope_url = f"{settings.main_domain}/mcp/servers/{id}"

            server = McpServer(
                id=id,
                name=server_data.get("name", ""),
                description=server_data.get("description", ""),
                tags=server_data.get("tags", []),
                logo_url=server_data.get("logo_url"),
                modelscope_url=modelscope_url,
                view_count=server_data.get("view_count", 0),
            )
            servers.append(server)

        return servers

    @mcp.tool(
        annotations={
            "title": "Get MCP Server Detail",
        }
    )
    async def get_mcp_server_detail(
        server_id: Annotated[
            str,
            Field(description="MCP Server's unique ID, for example '@modelscope/modelscope-mcp-server'"),
        ],
    ) -> McpServerDetail:
        """Get detailed information about a specific MCP server."""
        url = f"{settings.main_domain}/openapi/v1/mcp/servers/{server_id}"

        client = get_client()
        response = await client.get(url)
        server_data = response.get("data", {})

        id = server_data.get("id", "")
        modelscope_url = f"{settings.main_domain}/mcp/servers/{id}"

        server_detail = McpServerDetail(
            # McpServer fields
            id=id,
            name=server_data.get("name", ""),
            description=server_data.get("description", ""),
            tags=server_data.get("tags", []),
            logo_url=server_data.get("logo_url"),
            modelscope_url=modelscope_url,
            view_count=server_data.get("view_count", 0),
            # Additional fields
            author=server_data.get("author", ""),
            server_config=server_data.get("server_config", []),
            env_schema=server_data.get("env_schema", ""),
            is_hosted=server_data.get("is_hosted", False),
            is_verified=server_data.get("is_verified", False),
            source_url=server_data.get("source_url", ""),
            readme=server_data.get("readme", ""),
            github_stars=server_data.get("github_stars", 0),
        )

        return server_detail
