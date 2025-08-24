"""ModelScope MCP Server Paper tools.

Provides MCP tools for paper-related operations, such as searching for papers, getting paper details, etc.
"""

from typing import Annotated, Literal

from fastmcp import FastMCP
from fastmcp.utilities import logging
from pydantic import Field

from ..client import get_client
from ..settings import settings
from ..types import Paper

logger = logging.get_logger(__name__)


def register_paper_tools(mcp: FastMCP) -> None:
    """Register all paper-related tools with the MCP server.

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
        limit: Annotated[int, Field(description="Maximum number of papers to return", ge=1, le=100)] = 10,
    ) -> list[Paper]:
        """Search for papers on ModelScope."""
        url = f"{settings.main_domain}/api/v1/dolphin/papers"

        request_data = {
            "Query": query,
            "PageNumber": 1,
            "PageSize": limit,
            "Sort": sort,
            "Criterion": [],
        }

        client = get_client()
        response = await client.put(url, request_data)

        papers_data = response.get("Data", {}).get("Papers", [])

        papers = []
        for paper_data in papers_data:
            arxiv_id = paper_data.get("ArxivId")
            modelscope_url = f"{settings.main_domain}/papers/{arxiv_id}"

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
