import pytest
from fastmcp import Client


@pytest.mark.asyncio
async def test_search_papers(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool(
            "search_papers", {"query": "nexus-gen", "limit": 2}
        )

        assert hasattr(result, "data"), "Result should have data attribute"
        papers = result.data

        print(f"✅ Received {len(papers)} papers:")
        for paper in papers:
            print(
                f"arxiv_id: {paper.get('arxiv_id', '')} | title: {paper.get('title', '')}"
            )

        assert isinstance(papers, list), "Papers should be a list"
        assert len(papers) > 0, "Papers should not be empty"

        paper = papers[0]
        assert "arxiv_id" in paper, "Paper should have arxiv_id"
        assert "title" in paper, "Paper should have title"
        assert "authors" in paper, "Paper should have authors"
        assert "modelscope_url" in paper, "Paper should have modelscope_url"
