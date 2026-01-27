#!/usr/bin/env python3
"""
MCP HTTP Client Wrapper
Bridges stdio MCP protocol to HTTP REST API

This script is NOT needed for HTTP mode!
The HTTP server itself handles MCP protocol.

For HTTP mode, configure Kiro to run the server directly:
{
  "command": "python",
  "args": ["-m", "aws_finops_mcp"],
  "env": {
    "MCP_SERVER_MODE": "http",
    "MCP_SERVER_HOST": "0.0.0.0",
    "MCP_SERVER_PORT": "8000"
  }
}
"""

import sys
import os

def main():
    """This wrapper is not needed - use direct server mode instead."""
    print("ERROR: This wrapper script is not the correct approach.", file=sys.stderr)
    print("", file=sys.stderr)
    print("For HTTP mode, you should run the server separately and NOT use it as an MCP server.", file=sys.stderr)
    print("", file=sys.stderr)
    print("Instead, use stdio mode (default) for MCP client integration:", file=sys.stderr)
    print("", file=sys.stderr)
    print('{', file=sys.stderr)
    print('  "mcpServers": {', file=sys.stderr)
    print('    "aws-finops": {', file=sys.stderr)
    print('      "command": "python",', file=sys.stderr)
    print('      "args": ["-m", "aws_finops_mcp"],', file=sys.stderr)
    print('      "env": {', file=sys.stderr)
    print('        "AWS_PROFILE": "your-profile",', file=sys.stderr)
    print('        "AWS_REGION": "us-east-1"', file=sys.stderr)
    print('      }', file=sys.stderr)
    print('    }', file=sys.stderr)
    print('  }', file=sys.stderr)
    print('}', file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    main()
