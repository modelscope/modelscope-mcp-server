import pytest
from fastmcp import Client


# Helper functions
async def search_datasets_helper(client, params):
    """Helper function to search datasets and validate basic response structure."""
    result = await client.call_tool("search_datasets", params)
    assert hasattr(result, "data"), "Result should have data attribute"
    datasets = result.data
    assert isinstance(datasets, list), "Datasets should be a list"
    return datasets


def print_dataset_info(dataset, extra_fields=None):
    """Print dataset information with optional extra fields."""
    base_info = (
        f"id: {dataset.get('id', '')} | "
        f"name: {dataset.get('name', '')} | "
        f"chinese_name: {dataset.get('chinese_name', '')}"
    )

    if extra_fields:
        for field in extra_fields:
            base_info += f" | {field}: {dataset.get(field, 0)}"

    print(base_info)


def print_datasets_list(datasets, description, extra_fields=None):
    """Print a list of datasets with description and optional extra fields."""
    print(f"✅ Received {len(datasets)} datasets {description}:")
    for dataset in datasets:
        print_dataset_info(dataset, extra_fields)


def validate_dataset_fields(dataset):
    """Validate that dataset has all required fields."""
    required_fields = [
        "id",
        "path",
        "name",
        "chinese_name",
        "created_by",
        "license",
        "modelscope_url",
        "downloads_count",
        "likes_count",
        "created_at",
        "updated_at",
    ]

    for field in required_fields:
        assert field in dataset, f"Dataset should have {field}"


@pytest.mark.integration
async def test_search_datasets(mcp_server):
    async with Client(mcp_server) as client:
        datasets = await search_datasets_helper(client, {"query": "金融", "limit": 5})

        print_datasets_list(datasets, "", ["downloads_count"])

        assert len(datasets) > 0, "Datasets should not be empty"
        validate_dataset_fields(datasets[0])


@pytest.mark.integration
async def test_search_datasets_without_query(mcp_server):
    async with Client(mcp_server) as client:
        datasets = await search_datasets_helper(client, {"limit": 3})

        print_datasets_list(datasets, "without query filter", ["likes_count"])


@pytest.mark.integration
async def test_search_datasets_sort_by_downloads(mcp_server):
    async with Client(mcp_server) as client:
        datasets = await search_datasets_helper(client, {"query": "问答", "sort": "downloads", "limit": 3})

        print_datasets_list(datasets, "sorted by downloads", ["downloads_count"])


@pytest.mark.integration
async def test_search_datasets_sort_by_likes(mcp_server):
    async with Client(mcp_server) as client:
        datasets = await search_datasets_helper(client, {"query": "文本", "sort": "likes", "limit": 3})

        print_datasets_list(datasets, "sorted by likes", ["likes_count"])
