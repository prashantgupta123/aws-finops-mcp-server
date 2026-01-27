#!/usr/bin/env python3
"""
MCP HTTP Client Wrapper with Authentication
Bridges stdio MCP protocol to HTTP REST API with basic auth support
"""

import json
import sys
import urllib.request
import urllib.error
import base64
import os


def main():
    """Read MCP requests from stdin and forward to HTTP server with auth."""
    server_url = os.getenv("MCP_SERVER_URL", "http://localhost:8000")
    username = os.getenv("MCP_USERNAME", "")
    password = os.getenv("MCP_PASSWORD", "")
    
    # Create basic auth header if credentials provided
    headers = {'Content-Type': 'application/json'}
    if username and password:
        credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
        headers['Authorization'] = f'Basic {credentials}'
    
    # Read from stdin line by line
    for line in sys.stdin:
        try:
            # Parse MCP request
            request = json.loads(line.strip())
            
            # Forward to HTTP server
            http_request = urllib.request.Request(
                f"{server_url}/mcp",
                data=json.dumps(request).encode('utf-8'),
                headers=headers
            )
            
            # Get response
            with urllib.request.urlopen(http_request) as response:
                result = json.loads(response.read().decode('utf-8'))
                
            # Write response to stdout
            print(json.dumps(result), flush=True)
            
        except json.JSONDecodeError as e:
            error = {"error": f"Invalid JSON: {e}"}
            print(json.dumps(error), file=sys.stderr, flush=True)
            
        except urllib.error.HTTPError as e:
            error = {"error": f"HTTP {e.code}: {e.reason}"}
            print(json.dumps(error), file=sys.stderr, flush=True)
            
        except Exception as e:
            error = {"error": str(e)}
            print(json.dumps(error), file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
