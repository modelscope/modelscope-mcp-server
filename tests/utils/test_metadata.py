from modelscope_mcp_server.utils.metadata import (
    get_fastmcp_version,
    get_mcp_protocol_version,
    get_python_version,
    get_server_name,
    get_server_name_with_version,
    get_server_version,
)


def test_get_server_name():
    """Test get_server_name returns correct server name."""
    name = get_server_name()

    assert isinstance(name, str), "Server name should be a string"
    assert len(name) > 0, "Server name should not be empty"


def test_get_server_name_with_version():
    """Test get_server_name_with_version returns server name with version."""
    name_with_version = get_server_name_with_version()

    # Should start with server name
    server_name = get_server_name()
    assert name_with_version.startswith(server_name), f"Should start with '{server_name}'"

    # Should end with version
    server_version = get_server_version()
    assert name_with_version.endswith(server_version), f"Should end with version '{server_version}'"


def test_get_server_version():
    """Test get_server_version returns valid version string."""
    version = get_server_version()

    assert isinstance(version, str), "Server version should be a string"
    assert len(version) > 0, "Server version should not be empty"


def test_get_fastmcp_version():
    """Test get_fastmcp_version returns valid version string."""
    version = get_fastmcp_version()

    assert isinstance(version, str), "FastMCP version should be a string"
    assert len(version) > 0, "FastMCP version should not be empty"


def test_get_mcp_protocol_version():
    """Test get_mcp_protocol_version returns valid version string."""
    version = get_mcp_protocol_version()

    assert isinstance(version, str), "MCP protocol version should be a string"
    assert len(version) > 0, "MCP protocol version should not be empty"


def test_get_python_version():
    """Test get_python_version returns valid version string."""
    version = get_python_version()

    assert isinstance(version, str), "Python version should be a string"
    assert len(version) > 0, "Python version should not be empty"
