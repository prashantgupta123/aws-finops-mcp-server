# AWS FinOps MCP Server - Dockerfile
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy package files
COPY pyproject.toml ./
COPY src/ ./src/
COPY README.md ./

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install .

# Create non-root user
RUN useradd -m -u 1000 finops && \
    chown -R finops:finops /app

USER finops

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import aws_finops_mcp" || exit 1

# Run the server
CMD ["python", "-m", "aws_finops_mcp"]
