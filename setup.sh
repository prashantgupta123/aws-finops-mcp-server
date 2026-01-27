#!/bin/bash
# AWS FinOps MCP Server - Setup Script
# This script sets up a Python virtual environment and installs the package

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}AWS FinOps MCP Server - Setup${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check Python version
echo -e "${YELLOW}Checking Python version...${NC}"
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 13 ]); then
    echo -e "${RED}Error: Python 3.13 or higher is required${NC}"
    echo -e "${RED}Current version: $PYTHON_VERSION${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python $PYTHON_VERSION${NC}"
echo ""

# Create virtual environment
VENV_DIR="venv"
echo -e "${YELLOW}Creating virtual environment in '$VENV_DIR'...${NC}"

if [ -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}Virtual environment already exists. Removing...${NC}"
    rm -rf "$VENV_DIR"
fi

python3 -m venv "$VENV_DIR"
echo -e "${GREEN}✓ Virtual environment created${NC}"
echo ""

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source "$VENV_DIR/bin/activate"
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip > /dev/null 2>&1
echo -e "${GREEN}✓ pip upgraded${NC}"
echo ""

# Install package
echo -e "${YELLOW}Installing AWS FinOps MCP Server...${NC}"
if pip install -e . 2>&1 | grep -v "^Requirement already satisfied" | grep -v "^Obtaining file://"; then
    echo -e "${GREEN}✓ Package installed${NC}"
else
    echo -e "${RED}✗ Package installation failed${NC}"
    echo -e "${YELLOW}Trying with verbose output...${NC}"
    pip install -e .
fi
echo ""

# Install development dependencies (optional)
read -p "Install development dependencies? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Installing development dependencies...${NC}"
    if pip install -e ".[dev]" 2>&1 | grep -v "^Requirement already satisfied" | grep -v "^Obtaining file://"; then
        echo -e "${GREEN}✓ Development dependencies installed${NC}"
    else
        echo -e "${RED}✗ Development dependencies installation failed${NC}"
        echo -e "${YELLOW}Trying with verbose output...${NC}"
        pip install -e ".[dev]"
    fi
    echo ""
fi

# Verify installation
echo -e "${YELLOW}Verifying installation...${NC}"
python verify_installation.py

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "To activate the virtual environment, run:"
echo -e "${YELLOW}  source venv/bin/activate${NC}"
echo ""
echo -e "To run the MCP server:"
echo -e "${YELLOW}  python -m aws_finops_mcp${NC}"
echo ""
echo -e "To deactivate the virtual environment:"
echo -e "${YELLOW}  deactivate${NC}"
echo ""
