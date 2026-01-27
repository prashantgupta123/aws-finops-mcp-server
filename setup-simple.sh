#!/bin/bash
# AWS FinOps MCP Server - Simple Setup Script

set -e

echo "========================================="
echo "AWS FinOps MCP Server - Setup"
echo "========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3.13 --version

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Removing existing venv..."
    rm -rf venv
fi
python3.13 -m venv venv

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install package
echo ""
echo "Installing AWS FinOps MCP Server..."
pip install -e .

# Verify installation
echo ""
echo "Verifying installation..."
python -c "import aws_finops_mcp; print('✓ Package imported successfully')"

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "To activate the virtual environment:"
echo "  source venv/bin/activate"
echo ""
echo "To run the server:"
echo "  python -m aws_finops_mcp"
echo ""
echo "To run verification:"
echo "  python verify_installation.py"
echo ""
