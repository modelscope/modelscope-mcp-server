"""ModelScope MCP Server Dataset tools.

Provides tools for dataset-related operations in the ModelScope MCP Server,
such as searching for datasets and retrieving dataset details.
"""

from typing import Annotated, Literal

from fastmcp import FastMCP
from fastmcp.utilities import logging
from pydantic import Field

from ..client import get_client
from ..settings import settings
from ..types import Dataset

logger = logging.get_logger(__name__)


def register_dataset_tools(mcp: FastMCP) -> None:
    """Register all dataset-related tools with the MCP server.

    Args:
        mcp (FastMCP): The MCP server instance

    """

    @mcp.tool(
        annotations={
            "title": "Search Datasets",
        }
    )
    async def search_datasets(
        query: Annotated[
            str,
            Field(
                description="Keyword to search for related datasets. "
                "Leave empty to get all datasets based on other filters."
            ),
        ] = "",
        sort: Annotated[
            Literal["default", "downloads", "likes", "gmt_modified"],
            Field(description="Sort order"),
        ] = "default",
        limit: Annotated[int, Field(description="Maximum number of datasets to return", ge=1, le=30)] = 10,
    ) -> list[Dataset]:
        """Search for datasets on ModelScope."""
        url = f"{settings.main_domain}/api/v1/dolphin/datasets"

        params = {
            "Query": query,
            "Sort": sort,
            "PageNumber": 1,
            "PageSize": limit,
        }

        client = get_client()
        response = await client.get(url, params=params)

        datasets_data = response.get("Data", [])

        datasets = []
        for dataset_data in datasets_data:
            path = dataset_data.get("Namespace", "")
            name = dataset_data.get("Name", "")
            modelscope_url = f"{settings.main_domain}/datasets/{path}/{name}"

            if not path or not name:
                logger.warning(f"Skipping dataset with invalid path or name: {dataset_data}")
                continue

            dataset = Dataset(
                id=f"{path}/{name}",
                path=path,
                name=name,
                chinese_name=dataset_data.get("ChineseName", ""),
                created_by=dataset_data.get("CreatedBy", ""),
                license=dataset_data.get("License", ""),
                modelscope_url=modelscope_url,
                downloads_count=dataset_data.get("Downloads", 0),
                likes_count=dataset_data.get("Likes", 0),
                created_at=dataset_data.get("GmtCreate", 0),
                updated_at=dataset_data.get("LastUpdatedTime", 0),
            )
            datasets.append(dataset)

        return datasets
