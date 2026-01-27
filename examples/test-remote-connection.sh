#!/bin/bash
# Test script for remote MCP server connection

set -e

# Configuration
SERVER_URL="${1:-http://localhost:8000}"

echo "=========================================="
echo "Testing AWS FinOps MCP Server"
echo "=========================================="
echo "Server URL: $SERVER_URL"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Test 1: Health Check
echo "Test 1: Health Check"
if response=$(curl -s -f "$SERVER_URL/health"); then
    print_success "Health check passed"
    echo "Response: $response"
else
    print_error "Health check failed"
    exit 1
fi
echo ""

# Test 2: Server Info
echo "Test 2: Server Info"
if response=$(curl -s -f "$SERVER_URL/"); then
    print_success "Server info retrieved"
    echo "$response" | python3 -m json.tool
else
    print_error "Failed to get server info"
    exit 1
fi
echo ""

# Test 3: List Tools
echo "Test 3: List Available Tools"
if response=$(curl -s -f "$SERVER_URL/tools"); then
    print_success "Tools list retrieved"
    tool_count=$(echo "$response" | python3 -c "import sys, json; print(len(json.load(sys.stdin)['tools']))")
    print_info "Found $tool_count tools"
    echo "$response" | python3 -m json.tool | head -20
else
    print_error "Failed to get tools list"
    exit 1
fi
echo ""

# Test 4: Execute a Tool (get_cost_by_region)
echo "Test 4: Execute Tool (get_cost_by_region)"
request_data='{
  "tool": "get_cost_by_region",
  "arguments": {
    "region_name": "us-east-1"
  }
}'

if response=$(curl -s -f -X POST "$SERVER_URL/mcp" \
    -H "Content-Type: application/json" \
    -d "$request_data"); then
    print_success "Tool executed successfully"
    echo "$response" | python3 -m json.tool | head -30
else
    print_error "Tool execution failed"
    print_info "This might be due to missing AWS credentials"
    print_info "Make sure the server has proper AWS credentials configured"
fi
echo ""

# Test 5: Execute Another Tool (find_unused_lambda_functions)
echo "Test 5: Execute Tool (find_unused_lambda_functions)"
request_data='{
  "tool": "find_unused_lambda_functions",
  "arguments": {
    "region_name": "us-east-1",
    "period": 90
  }
}'

if response=$(curl -s -f -X POST "$SERVER_URL/mcp" \
    -H "Content-Type: application/json" \
    -d "$request_data"); then
    print_success "Tool executed successfully"
    echo "$response" | python3 -m json.tool | head -30
else
    print_error "Tool execution failed"
    print_info "This might be due to missing AWS credentials or permissions"
fi
echo ""

echo "=========================================="
echo "✅ Testing Complete!"
echo "=========================================="
echo ""
print_info "If all tests passed, your MCP server is working correctly!"
print_info "You can now configure your MCP client to use: $SERVER_URL/mcp"
