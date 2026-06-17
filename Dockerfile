# cowork-to-code-bridge MCP Server
# Containerized MCP server for local code execution via Claude Code

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy package files
COPY pyproject.toml setup.py* ./

# Install bridge
RUN pip install --no-cache-dir -e .

# Health check: verify MCP server can initialize
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from cowork_to_code_bridge.mcp_server import MCPServer; MCPServer()" && echo "OK" || exit 1

# Run MCP server over stdio (standard for MCP)
ENTRYPOINT ["cowork-to-code-bridge-mcp"]
CMD ["--stdio"]
