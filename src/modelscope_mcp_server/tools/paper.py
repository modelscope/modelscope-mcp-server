"""
ModelScope MCP Server Paper tools.

Provides MCP tools for paper-related operations, such as searching for papers, getting paper details, etc.
"""

from typing import Annotated, Literal

import requests
from fastmcp import FastMCP
from fastmcp.utilities import logging
from pydantic import Field

from ..constants import MODELSCOPE_DOMAIN
from ..settings import settings
from ..types import Paper

logger = logging.get_logger(__name__)


def register_paper_tools(mcp: FastMCP) -> None:
    """
    Register all paper-related tools with the MCP server.

    Args:
        mcp (FastMCP): The MCP server instance
    """

    @mcp.tool(
        annotations={
            "title": "Search Papers",
        }
    )
    async def search_papers(
        query: Annotated[str, Field(description="Search query for papers")],
        sort: Annotated[
            Literal["default", "hot", "recommend"],
            Field(description="Sort order"),
        ] = "default",
        limit: Annotated[
            int, Field(description="Maximum number of papers to return", ge=1, le=100)
        ] = 10,
    ) -> list[Paper]:
        """
        Search for papers on ModelScope.
        """
        url = f"{settings.api_base_url}/dolphin/papers"

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "modelscope-mcp-server",
        }

        request_data = {
            "Query": query,
            "PageNumber": 1,
            "PageSize": limit,
            "Sort": sort,
            "Criterion": [],
        }

        try:
            response = requests.put(url, json=request_data, headers=headers, timeout=10)
        except requests.exceptions.Timeout:
            raise TimeoutError("Request timeout - please try again later")

        if response.status_code != 200:
            raise Exception(
                f"Server returned non-200 status code: {response.status_code} {response.text}"
            )

        data = response.json()

        if not data.get("Success", False):
            raise Exception(f"Server returned error: {data}")

        papers_data = data.get("Data", {}).get("Papers", [])

        papers = []
        for paper_data in papers_data:
            arxiv_id = paper_data.get("ArxivId")
            modelscope_url = f"{MODELSCOPE_DOMAIN}/papers/{arxiv_id}"

            paper = Paper(
                arxiv_id=arxiv_id,
                title=paper_data.get("Title"),
                authors=paper_data.get("Authors"),
                publish_date=paper_data.get("PublishDate"),
                abstract_cn=paper_data.get("AbstractCn"),
                abstract_en=paper_data.get("AbstractEn"),
                modelscope_url=modelscope_url,
                arxiv_url=paper_data.get("ArxivUrl"),
                pdf_url=paper_data.get("PdfUrl"),
                code_link=paper_data.get("CodeLink"),
                view_count=paper_data.get("ViewCount"),
                favorite_count=paper_data.get("FavoriteCount"),
                comment_count=paper_data.get("CommentTotalCount"),
            )
            papers.append(paper)

        return papers
