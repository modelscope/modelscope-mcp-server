# ModelScope MCP Server

[![PyPI - Version](https://img.shields.io/pypi/v/modelscope-mcp-server.svg)](https://pypi.org/project/modelscope-mcp-server)
[![Docker](https://img.shields.io/badge/docker-supported-blue?logo=docker)](https://github.com/modelscope/modelscope-mcp-server/blob/main/Dockerfile)
[![GitHub Container Registry](https://img.shields.io/badge/container-registry-blue?logo=github)](https://github.com/modelscope/modelscope-mcp-server/pkgs/container/modelscope-mcp-server)
[![License](https://img.shields.io/github/license/modelscope/modelscope-mcp-server.svg)](https://github.com/modelscope/modelscope-mcp-server/blob/main/LICENSE)

[English](README.md) | 中文

魔搭社区（[ModelScope](https://modelscope.cn)）官方 MCP 服务器，为你的 AI 应用提供一站式接入能力，轻松访问平台海量的模型、数据集、创空间、论文、MCP 服务，以及各种 AIGC 生成能力。

## ✨ 功能特性

- 🎨 **AI 图像生成** - 使用 AIGC 模型从文本提示生成图像或转换现有图像（支持文生图和图生图）
- 🔍 **资源发现** - 搜索和发现 ModelScope 资源，包括机器学习模型、研究论文和 MCP 服务器，支持高级过滤选项
- 📋 **资源详情** _（即将推出）_ - 获取特定资源的全面详情，包括模型规格、论文摘要和 MCP 服务器配置
- 📖 **文档搜索** _（即将推出）_ - 对 ModelScope 文档和文章进行语义搜索
- 🚀 **Gradio API 集成** _（即将推出）_ - 调用任何预配置的 ModelScope Studio（AI 应用）暴露的 Gradio API
- 🔐 **上下文信息** - 访问当前操作上下文，包括认证用户信息和环境详情

## 🚀 快速开始

### 1. 获取您的 API Token

1. 访问 [ModelScope](https://modelscope.cn/home) 站点并登录您的账户
2. 导航至 **[首页] → [访问令牌]** 获取或创建您的 API Token

> 📖 详细说明请参考 [ModelScope 访问令牌](https://modelscope.cn/docs/accounts/token)

### 2. 与 MCP 客户端集成

将以下 JSON 配置添加到您的 MCP 客户端配置文件中：

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

或者，您可以使用预构建的 Docker 镜像：

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

更多详情请参考 [MCP JSON 配置标准](https://gofastmcp.com/integrations/mcp-json-configuration#mcp-json-configuration-standard)。

此格式在 MCP 生态系统中被广泛采用：

- **Cherry Studio**: 参见 [Cherry Studio MCP 配置](https://docs.cherry-ai.com/advanced-basic/mcp/config)
- **Claude Desktop**: 使用 `~/.claude/claude_desktop_config.json`
- **Cursor**: 使用 `~/.cursor/mcp.json`
- **VS Code**: 使用工作区 `.vscode/mcp.json`
- **其他客户端**: 许多 MCP 兼容的应用程序都遵循此标准

## 🛠️ 开发

### 环境设置

1. **克隆和设置**：

   ```bash
   git clone https://github.com/modelscope/modelscope-mcp-server.git
   cd modelscope-mcp-server
   uv sync
   ```

2. **激活环境**（或使用您的 IDE）：

   ```bash
   source .venv/bin/activate  # Linux/macOS
   ```

3. **设置您的 API Token**（Token 设置请参见快速开始部分）：

   ```bash
   export MODELSCOPE_API_TOKEN="your-api-token"
   # 或创建 .env 文件: echo 'MODELSCOPE_API_TOKEN="your-api-token"' > .env
   ```

### 运行演示脚本

运行快速演示以探索服务器的功能：

```bash
uv run python demo.py
```

使用 `--full` 标志进行全面功能演示：

```bash
uv run python demo.py --full
```

### 本地运行服务器

```bash
# 标准 stdio 传输（默认）
uv run modelscope-mcp-server

# 用于 Web 集成的可流式 HTTP 传输
uv run modelscope-mcp-server --transport http

# 自定义端口的 HTTP/SSE 传输（默认：8000）
uv run modelscope-mcp-server --transport [http/sse] --port 8080
```

对于 HTTP/SSE 模式，在您的 MCP 客户端配置中使用本地 URL 连接：

```json
{
  "mcpServers": {
    "modelscope-mcp-server": {
      "url": "http://127.0.0.1:8000/mcp/"
    }
  }
}
```

您也可以使用 [MCP Inspector](https://github.com/modelcontextprotocol/inspector) 工具调试服务器：

```bash
npx @modelcontextprotocol/inspector uv run modelscope-mcp-server
```

默认使用 stdio 传输；根据需要在 Web UI 中切换到 HTTP/SSE。

### 测试

```bash
# 运行所有测试
uv run pytest

# 运行特定测试文件
uv run pytest tests/test_search_papers.py

# 带覆盖率报告
uv run pytest --cov=src --cov-report=html
```

## 🔄 持续集成

本项目使用 GitHub Actions 进行自动化 CI/CD 工作流，在每次推送和拉取请求时运行：

### 自动化检查

- **✨ [Lint](https://github.com/modelscope/modelscope-mcp-server/actions/workflows/lint.yml)** - 使用 pre-commit hooks 进行代码格式化、代码检查和风格检查
- **🧪 [Test](https://github.com/modelscope/modelscope-mcp-server/actions/workflows/test.yml)** - 跨所有支持的 Python 版本进行全面测试
- **🔍 [CodeQL](https://github.com/modelscope/modelscope-mcp-server/actions/workflows/codeql.yml)** - 安全漏洞扫描和代码质量分析
- **🔒 [Gitleaks](https://github.com/modelscope/modelscope-mcp-server/actions/workflows/gitleaks.yml)** - 检测密码、API 密钥和令牌等敏感信息

### 本地开发检查

在提交 PR 之前在本地运行相同的检查：

```bash
# 安装并运行 pre-commit hooks
uv run pre-commit install
uv run pre-commit run --all-files

# 运行测试
uv run pytest
```

在 [Actions 标签页](https://github.com/modelscope/modelscope-mcp-server/actions) 中监控 CI 状态。

## 📦 发布管理

本项目使用 GitHub Actions 进行自动化发布管理。创建新版本的步骤：

1. **更新版本**，使用版本更新脚本：

   ```bash
   uv run python scripts/bump_version.py [patch|minor|major]
   # 或设置特定版本: uv run python scripts/bump_version.py set 1.2.3.dev1
   ```

2. **提交并打标签**（按照脚本输出的说明）：

   ```bash
   git add src/modelscope_mcp_server/_version.py
   git commit -m "chore: bump version to v{version}"
   git tag v{version} && git push origin v{version}
   ```

3. **自动发布** - GitHub Actions 将自动：
   - 创建新的 [GitHub Release](https://github.com/modelscope/modelscope-mcp-server/releases)
   - 发布包到 [PyPI 仓库](https://pypi.org/project/modelscope-mcp-server/)
   - 构建并推送 Docker 镜像到 [GitHub Container Registry](https://github.com/modelscope/modelscope-mcp-server/pkgs/container/modelscope-mcp-server)

## 🤝 贡献

我们欢迎贡献！请确保您的 PR：

- 包含相关测试并通过所有 CI 检查
- 为新功能更新文档
- 遵循常规提交格式

## 📚 参考资料

- **[Model Context Protocol](https://modelcontextprotocol.io/)** - 官方 MCP 文档
- **[FastMCP v2](https://github.com/jlowin/fastmcp)** - 高性能 MCP 框架
- **[MCP Example Servers](https://github.com/modelcontextprotocol/servers)** - 社区服务器示例

## 📜 许可证

本项目采用 [Apache 许可证（版本 2.0）](LICENSE)。
