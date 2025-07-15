# ModelScope MCP Server

[![PyPI - Version](https://img.shields.io/pypi/v/modelscope-mcp-server.svg)](https://pypi.org/project/modelscope-mcp-server) [![License](https://img.shields.io/github/license/pengqun/modelscope-mcp-server.svg)](https://github.com/pengqun/modelscope-mcp-server/blob/main/LICENSE)

## Features

- [x] Retrieve information about the currently authenticated ModelScope user
- [x] Generate images from text descriptions using any AIGC model available on ModelScope
- [x] Search for arXiv papers indexed in ModelScope, returning comprehensive metadata
- [ ] Search for models, datasets, studios and other resources on ModelScope
- [ ] Do semantic search for ModelScope documentation/articles to get help.
- [ ] Invoke Gradio API exposed by any ModelScope studio(app) you pre-configured.

## Usage

### Get API Token

1. Go to [ModelScope](https://modelscope.cn/home) and sign in.
2. Click [Home]->[Access Tokens] to get your default API Token or create a new one.

Refer to [ModelScope Documentation](https://modelscope.cn/docs/accounts/token) for more details.

### Built-in Demo

1. Set the ModelScope API token environment variable:

    ```bash
    export MODELSCOPE_API_TOKEN="your_api_token_here"
    ```

    Or, you can set the API token in the `.env` file (under the project root):

    ```env
    MODELSCOPE_API_TOKEN="your_api_token_here"
    ```

2. Run the demo:

    ```bash
    uv run python demo.py
    ```

### Integrate with popular MCP clients

- Use in [Claude Desktop](https://modelcontextprotocol.io/quickstart/user) / [Cursor](https://docs.cursor.com/context/model-context-protocol) / [Cherry Studio](https://docs.cherry-ai.com/advanced-basic/mcp/config):

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

## Contributing

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (Recommended for environment management)

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/pengqun/modelscope-mcp-server.git
   cd modelscope-mcp-server
   ```

2. Create and sync the environment:

   ```bash
   uv sync
   ```

   This installs all dependencies, including dev tools.

3. Activate the virtual environment (e.g., `source .venv/bin/activate` or via your IDE).

### Run the Server

```bash
# Run with stdio transport (default)
uv run modelscope-mcp-server

# Run with streamable HTTP transport
fastmcp run src/modelscope_mcp_server/server.py --transport http
```

### Unit Tests

All PRs must introduce or update tests as appropriate and pass the full suite.

Run tests using pytest:

```bash
uv run pytest
```

or if you want an overview of the code coverage

```bash
uv run pytest --cov=src --cov=examples --cov-report=html
```

### Static Checks

This project uses `pre-commit` for code formatting, linting, and type-checking. All PRs must pass these checks (they run automatically in CI).

Install the hooks locally:

```bash
uv run pre-commit install
```

The hooks will now run automatically on `git commit`. You can also run them manually at any time:

```bash
pre-commit run --all-files
# or via uv
uv run pre-commit run --all-files
```

### Version Management

The project uses automated version management scripts for releases:

#### Bump Version

```bash
# Bump patch version (1.0.0 -> 1.0.1)
python scripts/bump_version.py patch

# Bump minor version (1.0.0 -> 1.1.0)
python scripts/bump_version.py minor

# Bump major version (1.0.0 -> 2.0.0)
python scripts/bump_version.py major

# Create pre-release versions (in development order)
python scripts/bump_version.py patch --pre dev    # 1.0.1.dev1  (development snapshot)
python scripts/bump_version.py patch --pre alpha  # 1.0.1a1     (internal testing)
python scripts/bump_version.py patch --pre beta   # 1.0.1b1     (public testing)
python scripts/bump_version.py patch --pre rc     # 1.0.1rc1    (release candidate)
```

#### Release to PyPI

> TODO: trigger release from github actions

```bash
# Preview what will be released (dry-run mode)
python scripts/release.py --dry-run

# Perform actual release
python scripts/release.py
```

## References

- Model Context Protocol - <https://modelcontextprotocol.io/>
- FastMCP v2 - <https://github.com/jlowin/fastmcp>
- MCP Python SDK - <https://github.com/modelcontextprotocol/python-sdk>
- MCP Example Servers - <https://github.com/modelcontextprotocol/servers>
- Hugging Face Official MCP Server - <https://github.com/evalstate/hf-mcp-server>
- mcp-hfspace MCP Server - <https://github.com/evalstate/mcp-hfspace>
- shreyaskarnik/huggingface-mcp-server - <https://github.com/shreyaskarnik/huggingface-mcp-server>
- Cursor – Model Context Protocol - <https://docs.cursor.com/context/model-context-protocol>
