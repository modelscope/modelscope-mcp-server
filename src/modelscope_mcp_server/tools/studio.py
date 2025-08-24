"""ModelScope MCP Server Studio tools.

Provides tools for studio-related operations in the ModelScope MCP Server,
such as searching for studios and retrieving studio details.
"""

from typing import Annotated, Literal

from fastmcp import FastMCP
from fastmcp.utilities import logging
from pydantic import Field

from ..client import get_client
from ..settings import settings
from ..types import Studio

logger = logging.get_logger(__name__)


def register_studio_tools(mcp: FastMCP) -> None:
    """Register all studio-related tools with the MCP server.

    Args:
        mcp (FastMCP): The MCP server instance

    """

    @mcp.tool(
        annotations={
            "title": "Search Studios (创空间 AI 应用)",
        }
    )
    async def search_studios(
        query: Annotated[
            str,
            Field(
                description="Keyword to search for related studios. "
                "Leave empty to get all studios based on other filters."
            ),
        ] = "",
        domains: Annotated[
            list[Literal["multi-modal", "cv", "nlp", "audio", "AutoML"]] | None,
            Field(description="Domain categories to filter by"),
        ] = None,
        sort: Annotated[
            Literal["Default", "gmt_modified", "VisitsCount", "StarsCount"],
            Field(description="Sort order"),
        ] = "Default",
        limit: Annotated[int, Field(description="Maximum number of studios to return", ge=1, le=30)] = 10,
    ) -> list[Studio]:
        """Search for studios on ModelScope."""
        url = f"{settings.main_domain}/api/v1/dolphin/studios"

        # Build criterion for filters
        criterion = []

        # Add create_type filter (always include all types)
        criterion.append(
            {
                "category": "create_type",
                "predicate": "contains",
                "values": ["interactive", "programmatic"],
            }
        )

        # Add domains filter
        if domains:
            criterion.append(
                {
                    "category": "domains",
                    "predicate": "contains",
                    "values": domains,
                }
            )

        request_data = {
            "Name": query,
            "Criterion": criterion,
            "SortBy": sort,
            "PageNumber": 1,
            "PageSize": limit,
        }

        client = get_client()
        response = await client.put(url, request_data)

        studios_data = response.get("Data", {}).get("Studios", [])

        studios = []
        for studio_data in studios_data:
            path = studio_data.get("Path", "")
            name = studio_data.get("Name", "")
            modelscope_url = f"{settings.main_domain}/studios/{path}/{name}"

            if not path or not name:
                logger.warning(f"Skipping studio with invalid path or name: {studio_data}")
                continue

            studio = Studio(
                id=str(studio_data.get("Id", "")),
                path=path,
                name=name,
                chinese_name=studio_data.get("ChineseName", ""),
                description=studio_data.get("Description", ""),
                created_by=studio_data.get("CreatedBy", ""),
                license=studio_data.get("License", ""),
                modelscope_url=modelscope_url,
                independent_url=studio_data.get("IndependentUrl"),
                cover_image=studio_data.get("CoverImage"),
                type=studio_data.get("Type", ""),
                status=studio_data.get("Status", ""),
                domains=studio_data.get("Domain") or [],
                stars=studio_data.get("Stars", 0),
                visits=studio_data.get("Visits", 0),
                created_at=studio_data.get("CreatedTime", 0),
                updated_at=studio_data.get("LastUpdatedTime", 0),
                deployed_at=studio_data.get("DeployedTime", 0),
            )
            studios.append(studio)

        return studios
