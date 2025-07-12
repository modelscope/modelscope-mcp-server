# ModelScope Unofficial MCP Server

> 🚧 **WIP**: This project is currently under development and not yet complete. It's in the early development stage, and features and APIs may change.

## Features

- [x] Generate image URL from text

## Usage

### Runing the Demo

```bash
export MODELSCOPE_API_KEY="your_api_key_here"

uv run python demo.py
```

### Integrate with popular MCP clients

TODO

- Cursor
- VS Code
- ModelScope MCP Playground
- Cherry Studio

## Development

```bash
# Run with stdio transport (default)
uv run modelscope-mcp-server

# Run with streamable HTTP transport
fastmcp run src/modelscope_mcp_server/server.py --transport http
```

## Publishing

```bash
# Run the publishing script
python scripts/publish.py
```

TODO: auto publish via Github Actions

## References

- Model Context Protocol - <https://modelcontextprotocol.io/>
- FastMCP v2 - <https://github.com/jlowin/fastmcp>
- MCP Python SDK - <https://github.com/modelcontextprotocol/python-sdk>
- MCP Example Servers - <https://github.com/modelcontextprotocol/servers>
- Hugging Face Official MCP Server - <https://github.com/evalstate/hf-mcp-server>
- mcp-hfspace MCP Server - <https://github.com/evalstate/mcp-hfspace>
- shreyaskarnik/huggingface-mcp-server - <https://github.com/shreyaskarnik/huggingface-mcp-server>
- Cursor – Model Context Protocol - <https://docs.cursor.com/context/model-context-protocol>
