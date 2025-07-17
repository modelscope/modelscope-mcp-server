import pytest
from fastmcp import Client


# Helper functions
async def search_models_helper(client, params):
    """Helper function to search models and validate basic response structure."""
    result = await client.call_tool("search_models", params)
    assert hasattr(result, "data"), "Result should have data attribute"
    models = result.data
    assert isinstance(models, list), "Models should be a list"
    return models


def print_model_info(model, extra_fields=None):
    """Print model information with optional extra fields."""
    base_info = (
        f"id: {model.get('id', '')} | "
        f"name: {model.get('name', '')} | "
        f"support_inference: {model.get('support_inference', False)}"
    )

    if extra_fields:
        for field in extra_fields:
            base_info += f" | {field}: {model.get(field, 0)}"

    print(base_info)


def print_models_list(models, description, extra_fields=None):
    """Print a list of models with description and optional extra fields."""
    print(f"✅ Received {len(models)} models {description}:")
    for model in models:
        print_model_info(model, extra_fields)


def validate_model_fields(model):
    """Validate that model has all required fields."""
    required_fields = [
        "id",
        "name",
        "path",
        "chinese_name",
        "created_by",
        "support_inference",
        "downloads_count",
        "stars_count",
        "created_at",
        "updated_at",
    ]

    for field in required_fields:
        assert field in model, f"Model should have {field}"


@pytest.mark.asyncio
async def test_search_models(mcp_server):
    async with Client(mcp_server) as client:
        models = await search_models_helper(
            client, {"query": "flux", "task": "text-to-image", "limit": 5}
        )

        print_models_list(models, "", ["downloads_count"])

        assert len(models) > 0, "Models should not be empty"
        validate_model_fields(models[0])


@pytest.mark.asyncio
async def test_search_models_without_task_filter(mcp_server):
    async with Client(mcp_server) as client:
        models = await search_models_helper(client, {"query": "bert", "limit": 3})

        print_models_list(models, "without task filter", ["stars_count"])


@pytest.mark.asyncio
async def test_search_models_with_filters(mcp_server):
    async with Client(mcp_server) as client:
        models = await search_models_helper(
            client, {"query": "qwen", "filters": ["support_inference"], "limit": 3}
        )

        print_models_list(models, "with inference support", ["downloads_count"])

        # Verify that all returned models support inference
        for model in models:
            assert model.get("support_inference", False), (
                f"Model {model.get('id', '')} should support inference"
            )


@pytest.mark.asyncio
async def test_search_models_sort_by_stars(mcp_server):
    async with Client(mcp_server) as client:
        models = await search_models_helper(
            client, {"query": "llama", "sort": "StarsCount", "limit": 3}
        )

        print_models_list(models, "sorted by stars", ["stars_count"])
