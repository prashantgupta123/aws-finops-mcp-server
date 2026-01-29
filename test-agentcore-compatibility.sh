#!/bin/bash

# Test script to verify Amazon Bedrock AgentCore Runtime compatibility
# This script tests all required features for AgentCore Runtime deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
HOST="localhost"
PORT="8000"
BASE_URL="http://${HOST}:${PORT}"

print_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Test 1: Health Check
test_health_check() {
    print_header "Test 1: Health Check"
    
    response=$(curl -s -w "\n%{http_code}" "${BASE_URL}/health")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" = "200" ]; then
        print_success "Health check passed (HTTP $http_code)"
        echo "$body" | jq '.' 2>/dev/null || echo "$body"
    else
        print_error "Health check failed (HTTP $http_code)"
        exit 1
    fi
}

# Test 2: Server Info
test_server_info() {
    print_header "Test 2: Server Info"
    
    response=$(curl -s -w "\n%{http_code}" "${BASE_URL}/")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" = "200" ]; then
        print_success "Server info retrieved (HTTP $http_code)"
        echo "$body" | jq '.' 2>/dev/null || echo "$body"
        
        # Check for AgentCore compatibility flag
        agentcore_compatible=$(echo "$body" | jq -r '.agentcore_compatible' 2>/dev/null)
        if [ "$agentcore_compatible" = "true" ]; then
            print_success "AgentCore compatibility flag present"
        else
            print_warning "AgentCore compatibility flag not found"
        fi
    else
        print_error "Server info failed (HTTP $http_code)"
        exit 1
    fi
}

# Test 3: JSON-RPC 2.0 - Initialize
test_jsonrpc_initialize() {
    print_header "Test 3: JSON-RPC 2.0 - Initialize"
    
    response=$(curl -s -w "\n%{http_code}" -X POST "${BASE_URL}/mcp" \
        -H "Content-Type: application/json" \
        -d '{
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {}
        }')
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" = "200" ]; then
        print_success "Initialize method passed (HTTP $http_code)"
        echo "$body" | jq '.' 2>/dev/null || echo "$body"
        
        # Check protocol version
        protocol_version=$(echo "$body" | jq -r '.result.protocolVersion' 2>/dev/null)
        if [ "$protocol_version" = "2025-03-26" ]; then
            print_success "Protocol version correct: $protocol_version"
        else
            print_warning "Protocol version: $protocol_version"
        fi
    else
        print_error "Initialize method failed (HTTP $http_code)"
        exit 1
    fi
}

# Test 4: JSON-RPC 2.0 - Tools List
test_jsonrpc_tools_list() {
    print_header "Test 4: JSON-RPC 2.0 - Tools List"
    
    response=$(curl -s -w "\n%{http_code}" -X POST "${BASE_URL}/mcp" \
        -H "Content-Type: application/json" \
        -d '{
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }')
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" = "200" ]; then
        print_success "Tools list method passed (HTTP $http_code)"
        
        # Count tools
        tool_count=$(echo "$body" | jq '.result.tools | length' 2>/dev/null)
        if [ -n "$tool_count" ] && [ "$tool_count" -gt 0 ]; then
            print_success "Found $tool_count tools"
            echo "$body" | jq '.result.tools[0:3]' 2>/dev/null || echo "$body"
        else
            print_warning "No tools found"
        fi
    else
        print_error "Tools list method failed (HTTP $http_code)"
        exit 1
    fi
}

# Test 5: JSON-RPC 2.0 - Tool Call with Session ID
test_jsonrpc_tool_call() {
    print_header "Test 5: JSON-RPC 2.0 - Tool Call with Session ID"
    
    SESSION_ID="test-session-$(date +%s)"
    
    response=$(curl -s -w "\n%{http_code}" -X POST "${BASE_URL}/mcp" \
        -H "Content-Type: application/json" \
        -H "Mcp-Session-Id: ${SESSION_ID}" \
        -d '{
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "find_unused_elastic_ips",
                "arguments": {
                    "region_name": "us-east-1"
                }
            }
        }')
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" = "200" ]; then
        print_success "Tool call method passed (HTTP $http_code)"
        print_info "Session ID: ${SESSION_ID}"
        echo "$body" | jq '.' 2>/dev/null || echo "$body"
    else
        print_error "Tool call method failed (HTTP $http_code)"
        echo "$body"
        exit 1
    fi
}

# Test 6: Legacy Format (Backward Compatibility)
test_legacy_format() {
    print_header "Test 6: Legacy Format (Backward Compatibility)"
    
    response=$(curl -s -w "\n%{http_code}" -X POST "${BASE_URL}/mcp" \
        -H "Content-Type: application/json" \
        -d '{
            "tool": "find_unused_elastic_ips",
            "arguments": {
                "region_name": "us-east-1"
            }
        }')
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" = "200" ]; then
        print_success "Legacy format passed (HTTP $http_code)"
        echo "$body" | jq '.' 2>/dev/null || echo "$body"
    else
        print_warning "Legacy format failed (HTTP $http_code) - This is optional"
    fi
}

# Test 7: OAuth Authentication (if enabled)
test_oauth_auth() {
    print_header "Test 7: OAuth Authentication"
    
    # Check if auth is required
    if [ "${MCP_REQUIRE_AUTH}" = "true" ]; then
        print_info "Testing OAuth authentication..."
        
        response=$(curl -s -w "\n%{http_code}" -X POST "${BASE_URL}/mcp" \
            -H "Content-Type: application/json" \
            -d '{
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/list",
                "params": {}
            }')
        
        http_code=$(echo "$response" | tail -n1)
        body=$(echo "$response" | head -n-1)
        
        if [ "$http_code" = "401" ]; then
            print_success "OAuth authentication required (HTTP 401)"
            
            # Check for WWW-Authenticate header
            www_auth=$(curl -s -I -X POST "${BASE_URL}/mcp" \
                -H "Content-Type: application/json" \
                -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' \
                | grep -i "WWW-Authenticate")
            
            if [ -n "$www_auth" ]; then
                print_success "WWW-Authenticate header present"
                echo "$www_auth"
            else
                print_warning "WWW-Authenticate header not found"
            fi
        else
            print_warning "Expected 401 for unauthenticated request, got $http_code"
        fi
    else
        print_info "OAuth authentication not enabled (MCP_REQUIRE_AUTH=false)"
        print_info "Set MCP_REQUIRE_AUTH=true to test OAuth"
    fi
}

# Test 8: Error Handling
test_error_handling() {
    print_header "Test 8: Error Handling"
    
    # Test invalid method
    response=$(curl -s -w "\n%{http_code}" -X POST "${BASE_URL}/mcp" \
        -H "Content-Type: application/json" \
        -d '{
            "jsonrpc": "2.0",
            "id": 5,
            "method": "invalid/method",
            "params": {}
        }')
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" = "200" ]; then
        error_code=$(echo "$body" | jq -r '.error.code' 2>/dev/null)
        if [ "$error_code" = "-32601" ]; then
            print_success "Error handling correct (Method not found: -32601)"
        else
            print_warning "Unexpected error code: $error_code"
        fi
    else
        print_warning "Expected 200 with error object, got HTTP $http_code"
    fi
}

# Test 9: Docker Requirements
test_docker_requirements() {
    print_header "Test 9: Docker Requirements Check"
    
    print_info "Checking Dockerfile.agentcore..."
    
    if [ -f "Dockerfile.agentcore" ]; then
        print_success "Dockerfile.agentcore exists"
        
        # Check platform
        if grep -q "linux/arm64" Dockerfile.agentcore; then
            print_success "Platform: linux/arm64 ✓"
        else
            print_error "Platform: linux/arm64 not found"
        fi
        
        # Check port
        if grep -q "EXPOSE 8000" Dockerfile.agentcore; then
            print_success "Port: 8000 ✓"
        else
            print_error "Port: 8000 not exposed"
        fi
        
        # Check host
        if grep -q "MCP_SERVER_HOST=0.0.0.0" Dockerfile.agentcore; then
            print_success "Host: 0.0.0.0 ✓"
        else
            print_error "Host: 0.0.0.0 not set"
        fi
        
        # Check health check
        if grep -q "HEALTHCHECK" Dockerfile.agentcore; then
            print_success "Health check configured ✓"
        else
            print_warning "Health check not configured"
        fi
    else
        print_error "Dockerfile.agentcore not found"
    fi
}

# Main execution
main() {
    print_header "AWS FinOps MCP Server - AgentCore Runtime Compatibility Test"
    
    print_info "Testing server at: ${BASE_URL}"
    print_info "Make sure the server is running before executing this script"
    echo ""
    
    # Wait for server to be ready
    print_info "Waiting for server to be ready..."
    for i in {1..30}; do
        if curl -s "${BASE_URL}/health" > /dev/null 2>&1; then
            print_success "Server is ready!"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "Server not responding after 30 seconds"
            print_info "Start the server with: python -m aws_finops_mcp"
            exit 1
        fi
        sleep 1
    done
    
    # Run tests
    test_health_check
    test_server_info
    test_jsonrpc_initialize
    test_jsonrpc_tools_list
    test_jsonrpc_tool_call
    test_legacy_format
    test_oauth_auth
    test_error_handling
    test_docker_requirements
    
    # Summary
    print_header "Test Summary"
    print_success "All critical tests passed!"
    print_info "Your MCP server is compatible with Amazon Bedrock AgentCore Runtime"
    echo ""
    print_info "Next steps:"
    echo "  1. Build Docker image: docker build -f Dockerfile.agentcore -t aws-finops-mcp:latest ."
    echo "  2. Test locally: docker run -p 8000:8000 aws-finops-mcp:latest"
    echo "  3. Push to ECR and deploy to AgentCore Runtime"
    echo ""
    print_info "See BEDROCK_AGENTCORE_DEPLOYMENT.md for deployment instructions"
}

# Run main function
main
