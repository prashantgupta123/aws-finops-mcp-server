#!/bin/bash
# AWS FinOps MCP Server - Run Script
# This script runs the MCP server in the virtual environment

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

VENV_DIR="venv"

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${RED}Error: Virtual environment not found${NC}"
    echo -e "${YELLOW}Run './setup.sh' first to create the virtual environment${NC}"
    exit 1
fi

# Activate virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
source "$VENV_DIR/bin/activate"

# Check if package is installed
if ! python -c "import aws_finops_mcp" 2>/dev/null; then
    echo -e "${RED}Error: aws_finops_mcp package not found${NC}"
    echo -e "${YELLOW}Run './setup.sh' first to install the package${NC}"
    exit 1
fi

# Run the server
echo -e "${GREEN}Starting AWS FinOps MCP Server...${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
echo ""

python -m aws_finops_mcp
