FROM python:3.12-alpine

# Install system dependencies
RUN apk add --no-cache curl

# Install uv from official image (supports multi-arch)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy dependency files first for better caching
COPY pyproject.toml uv.lock ./

# Install dependencies first (this layer will be cached if dependencies don't change)
RUN uv sync --frozen --no-install-project

# Copy the rest of the project files
COPY . /app

# Install the project itself (this will be much faster as dependencies are already installed)
RUN uv sync --frozen

# Create a non-root user
RUN adduser -D -u 1000 mcpuser && chown -R mcpuser:mcpuser /app
USER mcpuser

# Use virtual environment activation and direct Python execution
# Avoid "uv run" to prevent runtime project rebuilding and reduce startup overhead
ENTRYPOINT [".venv/bin/python", "-m", "modelscope_mcp_server"]

CMD []
