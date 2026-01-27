#!/bin/bash
# AWS FinOps MCP Server - Test Script
# This script runs tests in the virtual environment

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

# Check if pytest is installed
if ! python -c "import pytest" 2>/dev/null; then
    echo -e "${YELLOW}pytest not found. Installing development dependencies...${NC}"
    pip install -e ".[dev]" > /dev/null 2>&1
    echo -e "${GREEN}✓ Development dependencies installed${NC}"
fi

# Run tests
echo -e "${GREEN}Running tests...${NC}"
echo ""

pytest tests/ -v

echo ""
echo -e "${GREEN}Tests complete!${NC}"
