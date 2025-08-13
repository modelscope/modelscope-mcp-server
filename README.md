# ModelScope MCP Server

[![PyPI Version](https://img.shields.io/pypi/v/modelscope-mcp-server.svg)](https://pypi.org/project/modelscope-mcp-server)
[![PyPI Downloads](https://static.pepy.tech/badge/modelscope-mcp-server)](https://pepy.tech/projects/modelscope-mcp-server)
[![Docker](https://img.shields.io/badge/docker-supported-blue?logo=docker)](https://github.com/modelscope/modelscope-mcp-server/blob/main/Dockerfile)
[![GitHub Container Registry](https://img.shields.io/badge/container-registry-blue?logo=github)](https://github.com/modelscope/modelscope-mcp-server/pkgs/container/modelscope-mcp-server)
[![License](https://img.shields.io/github/license/modelscope/modelscope-mcp-server.svg)](https://github.com/modelscope/modelscope-mcp-server/blob/main/LICENSE)

English | [中文](README_zh-CN.md)

Empowers AI agents and chatbots with direct access to [ModelScope](https://modelscope.cn)'s rich ecosystem of AI resources. From generating images to discovering cutting-edge models, datasets, apps and research papers, this MCP server makes ModelScope's vast collection of tools and services accessible through simple conversational interactions.

For a quick trial or a hosted option, visit the [project page](https://modelscope.cn/mcp/servers/@modelscope/modelscope-mcp-server) on the ModelScope MCP Plaza.

## ✨ Features

- 🎨 **AI Image Generation** - Generate images from prompts (text-to-image) or transform existing images (image-to-image) using AIGC models
- 🔍 **Resource Discovery** - Search and discover ModelScope resources including models, datasets, studios (AI apps), research papers, and MCP servers with advanced filtering options
- 📋 **Resource Details** - Get comprehensive details for specific resources
- 📖 **Documentation Search** _(Coming Soon)_ - Semantic search for ModelScope documentation and articles
- 🚀 **Gradio API Integration** _(Coming Soon)_ - Invoke Gradio APIs exposed by any pre-configured ModelScope studios
- 🔐 **Context Information** - Access current operational context including authenticated user information and environment details

## 🚀 Quick Start

### 1. Get Your API Token

1. Visit [ModelScope](https://modelscope.cn/home) and sign in to your account
2. Navigate to **[Home] → [Access Tokens]** to retrieve or create your API token

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
        "ghcr.io/modelscope/modelscope-mcp-server"
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

2. **Activate Environment** (or use your IDE):

   ```bash
   source .venv/bin/activate  # Linux/macOS
   ```

3. **Set Your API Token** (see Quick Start section for token setup):

   ```bash
   export MODELSCOPE_API_TOKEN="your-api-token"
   # Or create .env file: echo 'MODELSCOPE_API_TOKEN="your-api-token"' > .env
   ```

### Running the Demo Script

Run a quick demo to explore the server's capabilities:

```bash
uv run python demo.py
```

Use the `--full` flag for comprehensive feature demonstration:

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
# Run in UI mode with stdio transport (can switch to HTTP/SSE in the Web UI as needed)
npx @modelcontextprotocol/inspector uv run modelscope-mcp-server

# Run in CLI mode with HTTP transport (can do operations across tools, resources, and prompts)
npx @modelcontextprotocol/inspector --cli http://127.0.0.1:8000/mcp/ --transport http --method tools/list
```

### Testing

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_search_papers.py

# With coverage report
uv run pytest --cov=src --cov-report=html
```

## 🔄 Continuous Integration

This project uses GitHub Actions for automated CI/CD workflows that run on every push and pull request:

### Automated Checks

- **✨ [Lint](https://github.com/modelscope/modelscope-mcp-server/actions/workflows/lint.yml)** - Code formatting, linting, and style checks using pre-commit hooks
- **🧪 [Test](https://github.com/modelscope/modelscope-mcp-server/actions/workflows/test.yml)** - Comprehensive testing across all supported Python versions
- **🔍 [CodeQL](https://github.com/modelscope/modelscope-mcp-server/actions/workflows/codeql.yml)** - Security vulnerability scanning and code quality analysis
- **🔒 [Gitleaks](https://github.com/modelscope/modelscope-mcp-server/actions/workflows/gitleaks.yml)** - Detecting secrets like passwords, API keys, and tokens

### Local Development Checks

Run the same checks locally before submitting PRs:

```bash
# Install and run pre-commit hooks
uv run pre-commit install
uv run pre-commit run --all-files

# Run tests
uv run pytest
```

Monitor CI status in the [Actions tab](https://github.com/modelscope/modelscope-mcp-server/actions).

## 📦 Release Management

This project uses GitHub Actions for automated release management. To create a new release:

1. **Update version** using the bump script:

   ```bash
   uv run python scripts/bump_version.py [patch|minor|major]
   # Or set specific version: uv run python scripts/bump_version.py set 1.2.3.dev1
   ```

2. **Commit and tag** (follow the script's output instructions):

   ```bash
   git add src/modelscope_mcp_server/_version.py
   git commit -m "chore: bump version to v{version}"
   git tag v{version} && git push origin v{version}
   ```

3. **Automated publishing** - GitHub Actions will automatically:
   - Create a new [GitHub Release](https://github.com/modelscope/modelscope-mcp-server/releases)
   - Publish package to [PyPI repository](https://pypi.org/project/modelscope-mcp-server/)
   - Build and push Docker image to [GitHub Container Registry](https://github.com/modelscope/modelscope-mcp-server/pkgs/container/modelscope-mcp-server)

## 🤝 Contributing

We welcome contributions! Please ensure your PRs:

- Include relevant tests and pass all CI checks
- Update documentation for new features
- Follow conventional commit format

## 📚 References

- **[Model Context Protocol](https://modelcontextprotocol.io/)** - Official MCP documentation
- **[FastMCP v2](https://github.com/jlowin/fastmcp)** - High-performance MCP framework
- **[MCP Example Servers](https://github.com/modelcontextprotocol/servers)** - Community server examples

## 📜 License

This project is licensed under the [Apache License (Version 2.0)](LICENSE).
