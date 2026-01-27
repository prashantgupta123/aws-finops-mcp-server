"""HTTP server wrapper for AWS FinOps MCP Server to enable remote access."""

import json
import logging
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

from .server import mcp
from .session import get_aws_session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPHTTPHandler(BaseHTTPRequestHandler):
    """HTTP request handler for MCP server."""

    def do_GET(self) -> None:
        """Handle GET requests (health check)."""
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {"status": "healthy", "server": "aws-finops-mcp"}
            self.wfile.write(json.dumps(response).encode())
        elif self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {
                "name": "AWS FinOps MCP Server",
                "version": "0.2.0",
                "tools": 24,
                "endpoints": {
                    "health": "/health",
                    "mcp": "/mcp (POST)",
                    "tools": "/tools (GET)"
                }
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
        elif self.path == "/tools":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            # List all available tools
            tools = self._get_available_tools()
            self.wfile.write(json.dumps({"tools": tools}, indent=2).encode())
        else:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {"error": "Not found"}
            self.wfile.write(json.dumps(response).encode())

    def do_POST(self) -> None:
        """Handle POST requests (MCP tool calls)."""
        if self.path == "/mcp":
            try:
                # Read request body
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length)
                request_data = json.loads(body.decode())

                # Extract tool name and arguments
                tool_name = request_data.get("tool")
                arguments = request_data.get("arguments", {})

                if not tool_name:
                    self.send_error_response(400, "Missing 'tool' parameter")
                    return

                # Execute tool
                result = self._execute_tool(tool_name, arguments)

                # Send response
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(result, indent=2).encode())

            except json.JSONDecodeError:
                self.send_error_response(400, "Invalid JSON")
            except Exception as e:
                logger.error(f"Error executing tool: {e}")
                self.send_error_response(500, str(e))
        else:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {"error": "Not found"}
            self.wfile.write(json.dumps(response).encode())

    def send_error_response(self, code: int, message: str) -> None:
        """Send error response."""
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        response = {"error": message}
        self.wfile.write(json.dumps(response).encode())

    def _execute_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute MCP tool."""
        # Import server module to get tool functions
        from . import server

        # Get the tool function
        if not hasattr(server, tool_name):
            return {"error": f"Tool '{tool_name}' not found"}

        tool_func = getattr(server, tool_name)

        # Execute tool
        try:
            result = tool_func(**arguments)
            return {"success": True, "result": result}
        except Exception as e:
            logger.error(f"Error executing {tool_name}: {e}")
            return {"success": False, "error": str(e)}

    def _get_available_tools(self) -> list[str]:
        """Get list of available tools."""
        from . import server
        import inspect

        tools = []
        for name, obj in inspect.getmembers(server):
            if inspect.isfunction(obj) and not name.startswith("_") and name != "create_session":
                tools.append(name)

        return sorted(tools)

    def log_message(self, format: str, *args: Any) -> None:
        """Override to use logger instead of stderr."""
        logger.info(f"{self.address_string()} - {format % args}")


def run_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    """Run HTTP server."""
    server_address = (host, port)
    httpd = HTTPServer(server_address, MCPHTTPHandler)

    logger.info(f"🚀 AWS FinOps MCP Server starting on http://{host}:{port}")
    logger.info(f"📊 Health check: http://{host}:{port}/health")
    logger.info(f"🔧 Tools list: http://{host}:{port}/tools")
    logger.info(f"🎯 MCP endpoint: http://{host}:{port}/mcp (POST)")
    logger.info("Press Ctrl+C to stop")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("\n🛑 Shutting down server...")
        httpd.shutdown()
        logger.info("✅ Server stopped")


if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_SERVER_PORT", "8000"))

    run_server(host, port)
