#!/bin/bash

# Verification script for AgentCore deployment readiness
# Run this before executing 'agentcore launch'

set -e

echo "🔍 Verifying AgentCore Deployment Readiness..."
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0
WARNINGS=0

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
        ERRORS=$((ERRORS + 1))
    fi
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    WARNINGS=$((WARNINGS + 1))
}

# Check 1: AWS Credentials
echo "1️⃣  Checking AWS credentials..."
if aws sts get-caller-identity &> /dev/null; then
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    REGION=$(aws configure get region || echo "us-east-1")
    print_status 0 "AWS credentials configured (Account: $ACCOUNT_ID, Region: $REGION)"
else
    print_status 1 "AWS credentials not configured"
    echo "   Run: aws configure"
fi
echo ""

# Check 2: Required files
echo "2️⃣  Checking required files..."
if [ -f ".bedrock_agentcore.yaml" ]; then
    print_status 0 ".bedrock_agentcore.yaml exists"
    
    # Validate YAML structure
    if grep -q "agents:" .bedrock_agentcore.yaml && grep -q "default_agent:" .bedrock_agentcore.yaml; then
        print_status 0 ".bedrock_agentcore.yaml has correct structure"
    else
        print_status 1 ".bedrock_agentcore.yaml missing 'agents' or 'default_agent'"
    fi
else
    print_status 1 ".bedrock_agentcore.yaml not found"
fi

if [ -f "Dockerfile.agentcore" ]; then
    print_status 0 "Dockerfile.agentcore exists"
    
    # Check for required platform
    if grep -q "linux/arm64" Dockerfile.agentcore; then
        print_status 0 "Dockerfile configured for linux/arm64"
    else
        print_status 1 "Dockerfile missing linux/arm64 platform"
    fi
else
    print_status 1 "Dockerfile.agentcore not found"
fi

if [ -f "src/aws_finops_mcp/http_server.py" ]; then
    print_status 0 "http_server.py exists"
else
    print_status 1 "http_server.py not found"
fi
echo ""

# Check 3: Python environment
echo "3️⃣  Checking Python environment..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_status 0 "Python 3 installed (version: $PYTHON_VERSION)"
else
    print_status 1 "Python 3 not found"
fi

if [ -d "myenv" ] || [ -d ".venv" ] || [ -d "venv" ]; then
    print_status 0 "Virtual environment found"
    
    # Check if activated
    if [ -n "$VIRTUAL_ENV" ]; then
        print_status 0 "Virtual environment activated"
    else
        print_warning "Virtual environment not activated. Run: source myenv/bin/activate"
    fi
else
    print_warning "No virtual environment found"
fi
echo ""

# Check 4: Required packages
echo "4️⃣  Checking required packages..."
if python3 -c "import bedrock_agentcore_starter_toolkit" 2>/dev/null; then
    print_status 0 "bedrock-agentcore-starter-toolkit installed"
else
    print_status 1 "bedrock-agentcore-starter-toolkit not installed"
    echo "   Run: pip install bedrock-agentcore-starter-toolkit bedrock-agentcore"
fi

if command -v agentcore &> /dev/null; then
    print_status 0 "agentcore CLI available"
else
    print_status 1 "agentcore CLI not found"
    echo "   Run: pip install bedrock-agentcore-starter-toolkit bedrock-agentcore"
fi
echo ""

# Check 5: IAM Permissions (basic check)
echo "5️⃣  Checking IAM permissions..."
if aws sts get-caller-identity &> /dev/null; then
    # Check ECR permissions
    if aws ecr describe-repositories --max-items 1 &> /dev/null; then
        print_status 0 "ECR permissions available"
    else
        print_warning "ECR permissions may be insufficient"
    fi
    
    # Check IAM permissions
    if aws iam get-user &> /dev/null || aws iam get-role --role-name test-role &> /dev/null 2>&1; then
        print_status 0 "IAM read permissions available"
    else
        print_warning "IAM permissions may be insufficient"
    fi
fi
echo ""

# Check 6: Region support
echo "6️⃣  Checking region support..."
CURRENT_REGION=$(aws configure get region || echo "us-east-1")
SUPPORTED_REGIONS=("us-east-1" "us-west-2" "eu-west-1" "ap-southeast-1" "ap-northeast-1")

if [[ " ${SUPPORTED_REGIONS[@]} " =~ " ${CURRENT_REGION} " ]]; then
    print_status 0 "Region $CURRENT_REGION is supported"
else
    print_warning "Region $CURRENT_REGION may not support AgentCore"
    echo "   Supported regions: ${SUPPORTED_REGIONS[*]}"
fi
echo ""

# Check 7: Docker (optional, for local testing)
echo "7️⃣  Checking Docker (optional)..."
if command -v docker &> /dev/null; then
    print_status 0 "Docker installed (for local testing)"
    
    if docker info &> /dev/null; then
        print_status 0 "Docker daemon running"
    else
        print_warning "Docker daemon not running"
    fi
else
    print_warning "Docker not installed (not required for agentcore launch)"
fi
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ All critical checks passed!${NC}"
    echo ""
    echo "🚀 Ready to deploy! Run:"
    echo ""
    echo "   agentcore launch"
    echo ""
    
    if [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}⚠️  $WARNINGS warning(s) found (non-critical)${NC}"
        echo ""
    fi
else
    echo -e "${RED}❌ $ERRORS error(s) found${NC}"
    echo ""
    echo "Please fix the errors above before deploying."
    echo ""
    echo "Quick fixes:"
    echo "  - AWS credentials: aws configure"
    echo "  - Install toolkit: pip install bedrock-agentcore-starter-toolkit bedrock-agentcore"
    echo "  - Activate venv: source myenv/bin/activate"
    echo ""
    exit 1
fi

# Show next steps
echo "📋 Next Steps:"
echo ""
echo "1. Deploy to AgentCore:"
echo "   agentcore launch"
echo ""
echo "2. Monitor deployment:"
echo "   agentcore status"
echo ""
echo "3. Test your agent:"
echo "   agentcore invoke '{\"prompt\": \"list unused resources\"}'"
echo ""
echo "4. View logs:"
echo "   agentcore logs --follow"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📚 For detailed guides, see:"
echo "   - AGENTCORE_RUNTIME_REVIEW.md (status & troubleshooting)"
echo "   - QUICK_FIX_DEPLOYMENT.md (quick deployment)"
echo "   - MANUAL_AGENTCORE_DEPLOY.md (manual deployment)"
echo ""
