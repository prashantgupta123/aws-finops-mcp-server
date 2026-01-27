"""Entry point for AWS FinOps MCP Server."""

import logging
import os
from .server import mcp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    """Run the MCP server."""
    # Check if HTTP server mode is enabled
    if os.getenv("MCP_SERVER_MODE") == "http":
        from .http_server import run_server
        
        host = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
        port = int(os.getenv("MCP_SERVER_PORT", "8000"))
        
        logger.info("Starting AWS FinOps MCP Server in HTTP mode")
        run_server(host, port)
    else:
        # Standard MCP server mode (stdio)
        logger.info("Starting AWS FinOps MCP Server in stdio mode")
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
