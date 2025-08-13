# ModelScope MCP Server

[![PyPI Version](https://img.shields.io/pypi/v/modelscope-mcp-server.svg)](https://pypi.org/project/modelscope-mcp-server)
[![PyPI Downloads](https://static.pepy.tech/badge/modelscope-mcp-server)](https://pepy.tech/projects/modelscope-mcp-server)
[![Docker](https://img.shields.io/badge/docker-supported-blue?logo=docker)](https://github.com/modelscope/modelscope-mcp-server/blob/main/Dockerfile)
[![GitHub Container Registry](https://img.shields.io/badge/container-registry-blue?logo=github)](https://github.com/modelscope/modelscope-mcp-server/pkgs/container/modelscope-mcp-server)
[![License](https://img.shields.io/github/license/modelscope/modelscope-mcp-server.svg)](https://github.com/modelscope/modelscope-mcp-server/blob/main/LICENSE)

[English](README.md) | 中文

魔搭社区（[ModelScope](https://modelscope.cn)）官方 MCP 服务器，为你的 AI 应用提供一站式接入能力，轻松访问平台海量的模型、数据集、创空间、论文、MCP 服务，以及各种 AIGC 生成能力。

如需快速体验和托管部署，可访问魔搭社区 MCP 广场上的[项目页面](https://modelscope.cn/mcp/servers/@modelscope/modelscope-mcp-server)。

## ✨ 核心功能

- 🎨 **AI 图像生成** - 借助 AIGC 模型，轻松实现文生图（根据描述生成图像）或图生图（转换现有图像）
- 🔍 **资源发现** - 快速搜索和发现 ModelScope 平台上的模型、数据集、创空间（AI 应用）、研究论文和 MCP 服务，支持多种高级筛选
- 📋 **资源详情** - 深入了解特定资源的详细信息
- 📖 **文档搜索** _（即将推出）_ - 智能语义搜索 ModelScope 文档和文章内容
- 🚀 **Gradio API 集成** _（即将推出）_ - 调用任意预配置的 ModelScope 创空间暴露的 Gradio API
- 🔐 **上下文信息** - 实时获取当前操作环境信息，包括用户认证状态和运行环境详情

## 🚀 快速上手

### 1. 获取您的 API Token

1. 访问 [ModelScope 魔搭](https://modelscope.cn/home) 并登录您的账户
2. 进入 **[首页] → [访问令牌]** 页面获取或创建您的 API Token

> 📖 更详细的说明，请参考 [ModelScope 访问令牌文档](https://modelscope.cn/docs/accounts/token)

### 2. 集成到 MCP 客户端

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

或者，您也可以使用预构建的 Docker 镜像：

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

这一配置格式在 MCP 生态中被广泛采用：

- **Cherry Studio**: 参考 [Cherry Studio MCP 配置](https://docs.cherry-ai.com/advanced-basic/mcp/config)
- **Claude Desktop**: 配置文件位于 `~/.claude/claude_desktop_config.json`
- **Cursor**: 配置文件位于 `~/.cursor/mcp.json`
- **VS Code**: 工作区配置文件 `.vscode/mcp.json`
- **其他客户端**: 多数 MCP 兼容应用均支持此标准

## 🛠️ 开发指南

### 环境搭建

1. **克隆并设置项目**：

   ```bash
   git clone https://github.com/modelscope/modelscope-mcp-server.git
   cd modelscope-mcp-server
   uv sync
   ```

2. **激活环境**（或在您的 IDE 中使用）：

   ```bash
   source .venv/bin/activate  # Linux/macOS
   ```

3. **配置您的 API Token**（Token 获取方法请参考快速上手部分）：

   ```bash
   export MODELSCOPE_API_TOKEN="your-api-token"
   # 或创建 .env 文件: echo 'MODELSCOPE_API_TOKEN="your-api-token"' > .env
   ```

### 运行演示脚本

运行快速演示，体验服务器的核心功能：

```bash
uv run python demo.py
```

使用 `--full` 参数可体验完整功能演示：

```bash
uv run python demo.py --full
```

### 本地启动服务器

```bash
# 标准 stdio 传输（默认模式）
uv run modelscope-mcp-server

# 面向 Web 集成的流式 HTTP 传输
uv run modelscope-mcp-server --transport http

# 自定义端口的 HTTP/SSE 传输（默认端口：8000）
uv run modelscope-mcp-server --transport [http/sse] --port 8080
```

在 HTTP/SSE 模式下，您可以在 MCP 客户端配置中使用本地 URL 连接：

```json
{
  "mcpServers": {
    "modelscope-mcp-server": {
      "url": "http://127.0.0.1:8000/mcp/"
    }
  }
}
```

您还可以使用 [MCP Inspector](https://github.com/modelcontextprotocol/inspector) 工具调试服务器：

```bash
# 使用 stdio 传输在 UI 模式下运行（可根据需要在 Web UI 中切换到 HTTP/SSE）
npx @modelcontextprotocol/inspector uv run modelscope-mcp-server

# 使用 HTTP 传输在 CLI 模式下运行（可跨工具、资源和提示进行操作）
npx @modelcontextprotocol/inspector --cli http://127.0.0.1:8000/mcp/ --transport http --method tools/list
```

### 运行测试

```bash
# 运行全部测试
uv run pytest

# 运行指定测试文件
uv run pytest tests/test_search_papers.py

# 生成覆盖率报告
uv run pytest --cov=src --cov-report=html
```

## 🔄 持续集成

本项目使用 GitHub Actions 实现自动化 CI/CD 工作流，每次推送和拉取请求时都会自动运行：

### 自动化检查

- **✨ [Lint](https://github.com/modelscope/modelscope-mcp-server/actions/workflows/lint.yml)** - 使用 pre-commit hooks 进行代码格式化、代码检查和风格规范
- **🧪 [Test](https://github.com/modelscope/modelscope-mcp-server/actions/workflows/test.yml)** - 跨所有支持的 Python 版本进行全面功能测试
- **🔍 [CodeQL](https://github.com/modelscope/modelscope-mcp-server/actions/workflows/codeql.yml)** - 安全漏洞扫描和代码质量分析
- **🔒 [Gitleaks](https://github.com/modelscope/modelscope-mcp-server/actions/workflows/gitleaks.yml)** - 检测代码中可能泄露的密码、API 密钥和访问令牌

### 本地开发检查

提交 PR 前，请在本地运行相同的检查：

```bash
# 安装并运行 pre-commit hooks
uv run pre-commit install
uv run pre-commit run --all-files

# 运行测试
uv run pytest
```

您可以在 [Actions 标签页](https://github.com/modelscope/modelscope-mcp-server/actions) 中查看 CI 状态。

## 📦 版本发布

本项目使用 GitHub Actions 实现自动化版本发布管理。创建新版本的步骤：

1. **更新版本号**，使用版本更新脚本：

   ```bash
   uv run python scripts/bump_version.py [patch|minor|major]
   # 或设置指定版本: uv run python scripts/bump_version.py set 1.2.3.dev1
   ```

2. **提交并打标签**（请按照脚本输出的说明操作）：

   ```bash
   git add src/modelscope_mcp_server/_version.py
   git commit -m "chore: bump version to v{version}"
   git tag v{version} && git push origin v{version}
   ```

3. **自动发布** - GitHub Actions 将自动完成：
   - 创建新的 [GitHub Release](https://github.com/modelscope/modelscope-mcp-server/releases)
   - 发布包到 [PyPI 仓库](https://pypi.org/project/modelscope-mcp-server/)
   - 构建并推送 Docker 镜像到 [GitHub Container Registry](https://github.com/modelscope/modelscope-mcp-server/pkgs/container/modelscope-mcp-server)

## 🤝 贡献指南

我们热烈欢迎您的贡献！请确保您的 PR：

- 包含相关测试并通过所有 CI 检查
- 为新增功能补充相应文档
- 遵循常规提交格式规范

## 📚 相关资源

- **[Model Context Protocol](https://modelcontextprotocol.io/)** - 官方 MCP 文档
- **[FastMCP v2](https://github.com/jlowin/fastmcp)** - 高性能 MCP 框架
- **[MCP Example Servers](https://github.com/modelcontextprotocol/servers)** - 社区服务器示例

## 📜 许可证

本项目采用 [Apache 许可证（版本 2.0）](LICENSE)。
