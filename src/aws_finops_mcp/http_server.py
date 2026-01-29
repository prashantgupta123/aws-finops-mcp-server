"""HTTP server wrapper for AWS FinOps MCP Server to enable remote access.

This server is compatible with Amazon Bedrock AgentCore Runtime requirements:
- Listens on 0.0.0.0:8000
- Serves MCP protocol at /mcp endpoint
- Supports JSON-RPC 2.0 format
- Handles Mcp-Session-Id header for session management
- Supports OAuth authentication (401 with WWW-Authenticate header)
"""

import json
import logging
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any
from collections import defaultdict

from .server import mcp
from .session import get_aws_session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Session storage for stateful operations (AgentCore Runtime requirement)
session_storage = defaultdict(dict)


class MCPHTTPHandler(BaseHTTPRequestHandler):
    """HTTP request handler for MCP server with AgentCore Runtime compatibility."""

    def do_GET(self) -> None:
        """Handle GET requests (health check and info)."""
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
                "protocol": "MCP",
                "protocol_version": "2025-03-26",
                "endpoints": {
                    "health": "/health",
                    "mcp": "/mcp (POST)",
                    "tools": "/tools (GET)"
                },
                "agentcore_compatible": True
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
        """Handle POST requests (MCP tool calls).
        
        Supports both:
        1. JSON-RPC 2.0 format (AgentCore Runtime requirement)
        2. Legacy format (backward compatibility)
        """
        if self.path == "/mcp":
            try:
                # Extract session ID from header (AgentCore Runtime requirement)
                session_id = self.headers.get("Mcp-Session-Id", "default")
                
                # Read request body
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length)
                request_data = json.loads(body.decode())

                # Check if authentication is required (OAuth support)
                auth_header = self.headers.get("Authorization")
                if self._requires_auth() and not auth_header:
                    self._send_auth_required()
                    return

                # Handle JSON-RPC 2.0 format (AgentCore Runtime)
                if "jsonrpc" in request_data:
                    result = self._handle_jsonrpc(request_data, session_id)
                else:
                    # Legacy format for backward compatibility
                    result = self._handle_legacy(request_data, session_id)

                # Send response
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(result, indent=2).encode())

            except json.JSONDecodeError:
                self.send_error_response(400, "Invalid JSON")
            except Exception as e:
                logger.error(f"Error executing tool: {e}", exc_info=True)
                self.send_error_response(500, str(e))
        else:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {"error": "Not found"}
            self.wfile.write(json.dumps(response).encode())

    def _requires_auth(self) -> bool:
        """Check if authentication is required."""
        # Check if OAuth is configured via environment variable
        return os.getenv("MCP_REQUIRE_AUTH", "false").lower() == "true"

    def _send_auth_required(self) -> None:
        """Send 401 Unauthorized with WWW-Authenticate header (OAuth support).
        
        This follows RFC 6749 authentication standards for AgentCore Runtime.
        """
        self.send_response(401)
        self.send_header("Content-Type", "application/json")
        
        # Add WWW-Authenticate header for OAuth discovery
        auth_server = os.getenv("OAUTH_AUTH_SERVER", "https://cognito-idp.us-east-1.amazonaws.com")
        token_endpoint = os.getenv("OAUTH_TOKEN_ENDPOINT", f"{auth_server}/oauth2/token")
        
        www_auth = (
            f'Bearer realm="{auth_server}", '
            f'authorization_uri="{auth_server}/oauth2/authorize", '
            f'token_uri="{token_endpoint}"'
        )
        self.send_header("WWW-Authenticate", www_auth)
        self.end_headers()
        
        response = {
            "error": "unauthorized",
            "error_description": "Authentication required",
            "authorization_uri": f"{auth_server}/oauth2/authorize",
            "token_uri": token_endpoint
        }
        self.wfile.write(json.dumps(response).encode())

    def _handle_jsonrpc(self, request: dict, session_id: str) -> dict:
        """Handle JSON-RPC 2.0 format requests (AgentCore Runtime requirement).
        
        Supports MCP protocol methods:
        - tools/list: List all available tools
        - tools/call: Execute a specific tool
        """
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        logger.info(f"JSON-RPC request: method={method}, session={session_id}")
        
        try:
            # Handle tools/list method
            if method == "tools/list":
                tools = self._get_available_tools_detailed()
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": tools
                    }
                }
            
            # Handle tools/call method
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if not tool_name:
                    return self._jsonrpc_error(request_id, -32602, "Missing tool name")
                
                result = self._execute_tool(tool_name, arguments, session_id)
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": result
                }
            
            # Handle initialize method (optional)
            elif method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2025-03-26",
                        "serverInfo": {
                            "name": "aws-finops-mcp",
                            "version": "0.2.0"
                        },
                        "capabilities": {
                            "tools": {}
                        }
                    }
                }
            
            # Unknown method
            else:
                return self._jsonrpc_error(request_id, -32601, f"Method not found: {method}")
        
        except Exception as e:
            logger.error(f"Error handling JSON-RPC request: {e}", exc_info=True)
            return self._jsonrpc_error(request_id, -32603, str(e))

    def _handle_legacy(self, request: dict, session_id: str) -> dict:
        """Handle legacy format requests (backward compatibility)."""
        tool_name = request.get("tool")
        arguments = request.get("arguments", {})

        if not tool_name:
            return {"error": "Missing 'tool' parameter"}

        result = self._execute_tool(tool_name, arguments, session_id)
        return {"success": True, "result": result}

    def _jsonrpc_error(self, request_id: Any, code: int, message: str) -> dict:
        """Create JSON-RPC 2.0 error response."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message
            }
        }

    def send_error_response(self, code: int, message: str) -> None:
        """Send error response."""
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        response = {"error": message}
        self.wfile.write(json.dumps(response).encode())

    def _execute_tool(self, tool_name: str, arguments: dict[str, Any], session_id: str) -> dict[str, Any]:
        """Execute MCP tool with session support."""
        # Import server module to get tool functions
        from . import server

        # Get the tool function
        if not hasattr(server, tool_name):
            raise ValueError(f"Tool '{tool_name}' not found")

        tool_func = getattr(server, tool_name)

        # Store session data if needed
        if session_id != "default":
            session_storage[session_id]["last_tool"] = tool_name
            session_storage[session_id]["last_arguments"] = arguments

        # Execute tool
        try:
            result = tool_func(**arguments)
            
            # Store result in session for potential follow-up
            if session_id != "default":
                session_storage[session_id]["last_result"] = result
            
            return result
        except Exception as e:
            logger.error(f"Error executing {tool_name}: {e}", exc_info=True)
            raise

    def _get_available_tools(self) -> list[str]:
        """Get list of available tool names."""
        from . import server
        import inspect

        tools = []
        for name, obj in inspect.getmembers(server):
            if inspect.isfunction(obj) and not name.startswith("_") and name != "create_session":
                tools.append(name)

        return sorted(tools)

    def _get_available_tools_detailed(self) -> list[dict]:
        """Get detailed list of available tools with schemas (for tools/list)."""
        from . import server
        import inspect

        tools = []
        for name, obj in inspect.getmembers(server):
            if inspect.isfunction(obj) and not name.startswith("_") and name != "create_session":
                # Get function signature and docstring
                sig = inspect.signature(obj)
                doc = inspect.getdoc(obj) or ""
                
                # Extract description from docstring
                description = doc.split("\n\n")[0] if doc else f"Execute {name}"
                
                # Build parameter schema
                parameters = {}
                for param_name, param in sig.parameters.items():
                    param_type = "string"
                    if param.annotation != inspect.Parameter.empty:
                        if param.annotation == int:
                            param_type = "integer"
                        elif param.annotation == bool:
                            param_type = "boolean"
                        elif param.annotation == float:
                            param_type = "number"
                    
                    parameters[param_name] = {
                        "type": param_type,
                        "description": f"Parameter {param_name}"
                    }
                
                tools.append({
                    "name": name,
                    "description": description,
                    "inputSchema": {
                        "type": "object",
                        "properties": parameters
                    }
                })

        return sorted(tools, key=lambda x: x["name"])

    def log_message(self, format: str, *args: Any) -> None:
        """Override to use logger instead of stderr."""
        logger.info(f"{self.address_string()} - {format % args}")


def run_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    """Run HTTP server for AgentCore Runtime.
    
    AgentCore Runtime requirements:
    - Host: 0.0.0.0 (required)
    - Port: 8000 (required)
    - Endpoint: /mcp (required)
    - Protocol: HTTP/1.1
    - Session support: Mcp-Session-Id header
    """
    server_address = (host, port)
    httpd = HTTPServer(server_address, MCPHTTPHandler)

    logger.info("=" * 60)
    logger.info("🚀 AWS FinOps MCP Server - AgentCore Runtime Compatible")
    logger.info("=" * 60)
    logger.info(f"� Server: http://{host}:{port}")
    logger.info(f"📊 Health: http://{host}:{port}/health")
    logger.info(f"🔧 Tools: http://{host}:{port}/tools")
    logger.info(f"🎯 MCP Endpoint: http://{host}:{port}/mcp (POST)")
    logger.info(f"📋 Protocol: MCP (JSON-RPC 2.0)")
    logger.info(f"🔐 Auth Required: {os.getenv('MCP_REQUIRE_AUTH', 'false')}")
    logger.info("=" * 60)
    logger.info("✅ Ready for AgentCore Runtime deployment")
    logger.info("Press Ctrl+C to stop")
    logger.info("=" * 60)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("\n🛑 Shutting down server...")
        httpd.shutdown()
        logger.info("✅ Server stopped")


if __name__ == "__main__":
    # Get configuration from environment (AgentCore Runtime compatible)
    host = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_SERVER_PORT", "8000"))

    # Validate AgentCore Runtime requirements
    if host != "0.0.0.0":
        logger.warning(f"⚠️  Host should be 0.0.0.0 for AgentCore Runtime (current: {host})")
    if port != 8000:
        logger.warning(f"⚠️  Port should be 8000 for AgentCore Runtime (current: {port})")

    run_server(host, port)
