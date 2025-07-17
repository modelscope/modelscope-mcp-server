import pytest
from fastmcp import Client


@pytest.mark.asyncio
async def test_search_models(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool(
            "search_models", {"query": "flux", "task": "text-to-image", "limit": 5}
        )

        assert hasattr(result, "data"), "Result should have data attribute"
        models = result.data

        print(f"✅ Received {len(models)} models:")
        for model in models:
            print(
                f"id: {model.get('id', '')} | name: {model.get('name', '')} | downloads: {model.get('downloads_count', 0)}"
            )

        assert isinstance(models, list), "Models should be a list"
        assert len(models) > 0, "Models should not be empty"

        model = models[0]
        assert "id" in model, "Model should have id"
        assert "name" in model, "Model should have name"
        assert "path" in model, "Model should have path"
        assert "chinese_name" in model, "Model should have chinese_name"
        assert "created_by" in model, "Model should have created_by"
        assert "downloads_count" in model, "Model should have downloads_count"
        assert "stars_count" in model, "Model should have stars_count"
        assert "created_at" in model, "Model should have created_at"
        assert "updated_at" in model, "Model should have updated_at"


@pytest.mark.asyncio
async def test_search_models_without_task_filter(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool("search_models", {"query": "bert", "limit": 3})

        assert hasattr(result, "data"), "Result should have data attribute"
        models = result.data

        print(f"✅ Received {len(models)} models without task filter:")
        for model in models:
            print(
                f"id: {model.get('id', '')} | name: {model.get('name', '')} | stars: {model.get('stars_count', 0)}"
            )

        assert isinstance(models, list), "Models should be a list"


@pytest.mark.asyncio
async def test_search_models_with_support_inference_false(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool(
            "search_models", {"query": "qwen", "support_inference": False, "limit": 3}
        )

        assert hasattr(result, "data"), "Result should have data attribute"
        models = result.data

        print(f"✅ Received {len(models)} models (including non-inference):")
        for model in models:
            print(
                f"id: {model.get('id', '')} | name: {model.get('name', '')} | downloads: {model.get('downloads_count', 0)}"
            )

        assert isinstance(models, list), "Models should be a list"


@pytest.mark.asyncio
async def test_search_models_sort_by_stars(mcp_server):
    async with Client(mcp_server) as client:
        result = await client.call_tool(
            "search_models", {"query": "llama", "sort": "StarsCount", "limit": 3}
        )

        assert hasattr(result, "data"), "Result should have data attribute"
        models = result.data

        print(f"✅ Received {len(models)} models sorted by stars:")
        for model in models:
            print(
                f"id: {model.get('id', '')} | name: {model.get('name', '')} | stars: {model.get('stars_count', 0)}"
            )

        assert isinstance(models, list), "Models should be a list"
