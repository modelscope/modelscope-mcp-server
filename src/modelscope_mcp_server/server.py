from fastmcp import FastMCP

mcp = FastMCP("ModelScope MCP Server")


@mcp.tool()
def sum(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"
