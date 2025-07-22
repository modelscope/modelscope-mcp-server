# ModelScope MCP Server

[![PyPI - Version](https://img.shields.io/pypi/v/modelscope-mcp-server.svg)](https://pypi.org/project/modelscope-mcp-server)
[![Docker](https://img.shields.io/badge/docker-supported-blue?logo=docker)](https://github.com/modelscope/modelscope-mcp-server/blob/main/Dockerfile)
[![Docker Hub](https://img.shields.io/docker/v/spadrian/modelscope-mcp-server?logo=docker)](https://hub.docker.com/r/spadrian/modelscope-mcp-server)
[![License](https://img.shields.io/github/license/modelscope/modelscope-mcp-server.svg)](https://github.com/modelscope/modelscope-mcp-server/blob/main/LICENSE)

A Model Context Protocol (MCP) server that integrates with [ModelScope](https://modelscope.cn)'s ecosystem, providing seamless access to AI models, datasets, apps, papers, and generation capabilities through popular MCP clients.

## ✨ Features

- 🔐 **User Authentication** - Retrieve information about the currently authenticated ModelScope user
- 🎨 **AI Image Generation** - Generate images from text prompts or transform existing images using AIGC models (supports both text-to-image and image-to-image generation)
- 🔍 **Resource Discovery** - Search and discover ModelScope resources including machine learning models, research papers, and MCP servers with advanced filtering options
- 📋 **Resource Details** _(Coming Soon)_ - Get comprehensive details for specific resources including model specifications, paper abstracts, and MCP server configurations
- 📖 **Documentation Search** _(Coming Soon)_ - Semantic search for ModelScope documentation and articles
- 🚀 **Gradio API Integration** _(Coming Soon)_ - Invoke Gradio APIs exposed by any pre-configured ModelScope studio (AI app)

## 🚀 Quick Start

### 1. Get Your API Token

1. Visit [ModelScope](https://modelscope.cn/home) and sign in to your account
2. Navigate to **[Home] → [Access Tokens]** to retrieve your default API token or create a new one

> 📖 For detailed instructions, refer to the [ModelScope Token Documentation](https://modelscope.cn/docs/accounts/token)

### 2. Integration with MCP Clients

Add the following JSON configuration to your MCP client's configuration file:

```json
{
  "mcpServers": {
    "modelscope-mcp-server": {
      "command": "uvx",
      "args": ["modelscope-mcp-server"],
      "env": {
        "MODELSCOPE_API_TOKEN": "your-api-token"
      }
    }
  }
}
```

Or, you can use the pre-built Docker image:

```json
{
  "mcpServers": {
    "modelscope-mcp-server": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "-e", "MODELSCOPE_API_TOKEN",
        "spadrian/modelscope-mcp-server:latest"
      ],
      "env": {
        "MODELSCOPE_API_TOKEN": "your-api-token"
      }
    }
  }
}
```

Refer to the [MCP JSON Configuration Standard](https://gofastmcp.com/integrations/mcp-json-configuration#mcp-json-configuration-standard) for more details.

This format is widely adopted across the MCP ecosystem:

- **Cherry Studio**: See [Cherry Studio MCP Configuration](https://docs.cherry-ai.com/advanced-basic/mcp/config)
- **Claude Desktop**: Uses `~/.claude/claude_desktop_config.json`
- **Cursor**: Uses `~/.cursor/mcp.json`
- **VS Code**: Uses workspace `.vscode/mcp.json`
- **Other clients**: Many MCP-compatible applications follow this standard

## 🛠️ Development

### Environment Setup

1. **Clone and Setup**:

   ```bash
   git clone https://github.com/modelscope/modelscope-mcp-server.git
   cd modelscope-mcp-server
   uv sync
   ```

2. **Activate Environment**:

   ```bash
   source .venv/bin/activate  # Linux/macOS
   # or via your IDE
   ```

3. **Set Your API Token Environment Variable**:

   ```bash
   export MODELSCOPE_API_TOKEN="your-api-token"
   ```

   Or, you can set the API token in the `.env` file (under the project root) for convenience:

   ```env
   MODELSCOPE_API_TOKEN="your-api-token"
   ```

### Running the Demo Script

Run a quick demo to explore the server's capabilities:

```bash
uv run python demo.py
```

Use the `--full` flag to demonstrate all available features:

```bash
uv run python demo.py --full
```

### Running the Server Locally

```bash
# Standard stdio transport (default)
uv run modelscope-mcp-server

# Streamable HTTP transport for web integration
uv run modelscope-mcp-server --transport http

# HTTP/SSE transport with custom port (default: 8000)
uv run modelscope-mcp-server --transport [http/sse] --port 8080
```

For HTTP/SSE mode, connect using a local URL in your MCP client configuration:

```json
{
  "mcpServers": {
    "modelscope-mcp-server": {
      "url": "http://127.0.0.1:8000/mcp/"
    }
  }
}
```

You can also debug the server using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector) tool:

```bash
npx @modelcontextprotocol/inspector uv run modelscope-mcp-server
```

The above command uses stdio transport by default; you can switch to HTTP or SSE in the Web UI as needed.

### Testing

Run the complete test suite:

```bash
# Basic test run
uv run pytest

# Run tests for a specific file
uv run pytest tests/test_search_papers.py

# With coverage report
uv run pytest --cov=src --cov=examples --cov-report=html
```

### Code Quality

This project uses `pre-commit` hooks for automated code formatting, linting, and type checking:

```bash
# Install hooks
uv run pre-commit install

# Run all checks manually
uv run pre-commit run --all-files
```

**All PRs must pass these checks and include appropriate tests.**

## 📦 Release Management

> TODO: trigger release from GitHub Actions

### Release to PyPI

```bash
python scripts/pypi_release.py
```

### Release to Docker Hub

```bash
docker login

# Release to Docker Hub (will auto-detect buildx or use traditional build)
python scripts/docker_release.py

# Release to Docker Hub (use traditional multi-arch build with manifest)
python scripts/docker_release.py --traditional-multiarch
```

## 🤝 Contributing

We welcome contributions! Please ensure that:

1. All PRs include relevant tests and pass the full test suite
2. Code follows our style guidelines (enforced by pre-commit hooks)
3. Documentation is updated for new features
4. Commit messages follow conventional commit format

## 📚 References

- **[Model Context Protocol](https://modelcontextprotocol.io/)** - Official MCP documentation
- **[FastMCP v2](https://github.com/jlowin/fastmcp)** - High-performance MCP framework
- **[MCP Example Servers](https://github.com/modelcontextprotocol/servers)** - Community server examples

## 📜 License

This project is licensed under the [Apache License (Version 2.0)](LICENSE).
