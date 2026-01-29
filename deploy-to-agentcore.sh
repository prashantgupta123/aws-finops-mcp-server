#!/bin/bash

# Deploy AWS FinOps MCP Server to Amazon Bedrock AgentCore
# This script automates the deployment process for both Gateway and Runtime methods

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
AWS_REGION=${AWS_REGION:-us-east-1}
DEPLOYMENT_METHOD=""
FUNCTION_NAME="aws-finops-mcp-server"
ECR_REPO_NAME="aws-finops-mcp-server"
GATEWAY_NAME="finops-mcp-gateway"
RUNTIME_NAME="finops-mcp-runtime"

# Helper functions
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    print_info "Checking prerequisites..."
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI not found. Please install it first."
        exit 1
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 not found. Please install it first."
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS credentials not configured. Run 'aws configure' first."
        exit 1
    fi
    
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    print_info "AWS Account ID: $AWS_ACCOUNT_ID"
    print_info "AWS Region: $AWS_REGION"
}

show_menu() {
    echo ""
    echo "========================================="
    echo "AWS FinOps MCP Server - AgentCore Deploy"
    echo "========================================="
    echo ""
    echo "Select deployment method:"
    echo "  1) Gateway (Lambda-based) - Quick setup, serverless"
    echo "  2) Runtime (Containerized) - Full control, production-ready"
    echo "  3) Exit"
    echo ""
    read -p "Enter choice [1-3]: " choice
    
    case $choice in
        1)
            DEPLOYMENT_METHOD="gateway"
            ;;
        2)
            DEPLOYMENT_METHOD="runtime"
            ;;
        3)
            print_info "Exiting..."
            exit 0
            ;;
        *)
            print_error "Invalid choice. Please try again."
            show_menu
            ;;
    esac
}

deploy_gateway() {
    print_info "Deploying to AgentCore Gateway (Lambda-based)..."
    
    # Step 1: Create Lambda deployment package
    print_info "Step 1/6: Creating Lambda deployment package..."
    mkdir -p lambda-deployment/package
    
    # Install dependencies
    pip install -t lambda-deployment/package/ boto3 mcp bedrock-agentcore-starter-toolkit
    
    # Copy source code
    cp -r src/aws_finops_mcp lambda-deployment/package/
    
    # Create Lambda handler
    cat > lambda-deployment/lambda_handler.py << 'EOF'
import json
import logging
from aws_finops_mcp.session import get_aws_session
from aws_finops_mcp.tools import cleanup, cost_explorer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def lambda_handler(event, context):
    try:
        tool_name = event.get('tool')
        arguments = event.get('arguments', {})
        
        if not tool_name:
            return {'statusCode': 400, 'body': json.dumps({'error': 'Missing tool parameter'})}
        
        region = arguments.get('region_name', 'us-east-1')
        session = get_aws_session(region_name=region)
        
        # Route to tool (add more as needed)
        if tool_name == 'find_unused_lambda_functions':
            result = cleanup.find_unused_lambda_functions(session, region, arguments.get('period', 90))
        elif tool_name == 'get_cost_by_region':
            result = cost_explorer.get_cost_by_region(session, region)
        else:
            return {'statusCode': 400, 'body': json.dumps({'error': f'Unknown tool: {tool_name}'})}
        
        return {'statusCode': 200, 'body': json.dumps({'success': True, 'result': result})}
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
EOF
    
    # Create deployment package
    cd lambda-deployment/package
    zip -r ../lambda-deployment.zip . > /dev/null
    cd ..
    zip -g lambda-deployment.zip lambda_handler.py > /dev/null
    cd ..
    
    print_info "Lambda package created: lambda-deployment/lambda-deployment.zip"
    
    # Step 2: Create IAM role
    print_info "Step 2/6: Creating IAM role for Lambda..."
    
    cat > /tmp/lambda-trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "lambda.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}
EOF
    
    if aws iam get-role --role-name FinOpsMCPLambdaRole &> /dev/null; then
        print_warning "Role FinOpsMCPLambdaRole already exists, skipping creation"
    else
        aws iam create-role \
          --role-name FinOpsMCPLambdaRole \
          --assume-role-policy-document file:///tmp/lambda-trust-policy.json
        
        aws iam attach-role-policy \
          --role-name FinOpsMCPLambdaRole \
          --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
        
        # Attach FinOps policy if it exists
        if aws iam get-policy --policy-arn arn:aws:iam::$AWS_ACCOUNT_ID:policy/FinOpsFullPolicy &> /dev/null; then
            aws iam attach-role-policy \
              --role-name FinOpsMCPLambdaRole \
              --policy-arn arn:aws:iam::$AWS_ACCOUNT_ID:policy/FinOpsFullPolicy
        else
            print_warning "FinOpsFullPolicy not found. Please attach appropriate IAM policies manually."
        fi
        
        print_info "Waiting for IAM role to propagate..."
        sleep 10
    fi
    
    ROLE_ARN=$(aws iam get-role --role-name FinOpsMCPLambdaRole --query 'Role.Arn' --output text)
    
    # Step 3: Deploy Lambda function
    print_info "Step 3/6: Deploying Lambda function..."
    
    if aws lambda get-function --function-name $FUNCTION_NAME &> /dev/null; then
        print_warning "Lambda function already exists, updating code..."
        aws lambda update-function-code \
          --function-name $FUNCTION_NAME \
          --zip-file fileb://lambda-deployment/lambda-deployment.zip > /dev/null
    else
        aws lambda create-function \
          --function-name $FUNCTION_NAME \
          --runtime python3.13 \
          --role $ROLE_ARN \
          --handler lambda_handler.lambda_handler \
          --zip-file fileb://lambda-deployment/lambda-deployment.zip \
          --timeout 300 \
          --memory-size 512 \
          --environment Variables="{AWS_REGION=$AWS_REGION}" > /dev/null
    fi
    
    aws lambda wait function-active --function-name $FUNCTION_NAME
    LAMBDA_ARN=$(aws lambda get-function --function-name $FUNCTION_NAME --query 'Configuration.FunctionArn' --output text)
    print_info "Lambda function deployed: $LAMBDA_ARN"
    
    # Step 4: Install AgentCore toolkit
    print_info "Step 4/6: Installing AgentCore starter toolkit..."
    pip install -q bedrock-agentcore-starter-toolkit
    
    # Step 5: Create Gateway
    print_info "Step 5/6: Creating AgentCore Gateway..."
    
    cat > /tmp/gateway_setup.py << EOF
import sys
from bedrock_agentcore_starter_toolkit import AgentCoreClient

try:
    client = AgentCoreClient(region_name='$AWS_REGION')
    
    # Create gateway
    gateway_response = client.create_gateway(
        name='$GATEWAY_NAME',
        description='AWS FinOps MCP Server Gateway',
        protocol_version='2025-03-26'
    )
    
    gateway_id = gateway_response['gatewayId']
    gateway_url = gateway_response['gatewayUrl']
    
    print(f"GATEWAY_ID={gateway_id}")
    print(f"GATEWAY_URL={gateway_url}")
    
    # Add Lambda target
    target_response = client.create_gateway_target(
        gateway_id=gateway_id,
        name='finops-lambda-target',
        target_type='lambda',
        lambda_arn='$LAMBDA_ARN'
    )
    
    target_id = target_response['targetId']
    print(f"TARGET_ID={target_id}")
    
    # Synchronize
    client.synchronize_gateway_targets(
        gateway_id=gateway_id,
        target_ids=[target_id]
    )
    
    print("SUCCESS")
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
EOF
    
    GATEWAY_OUTPUT=$(python3 /tmp/gateway_setup.py)
    
    if echo "$GATEWAY_OUTPUT" | grep -q "SUCCESS"; then
        GATEWAY_ID=$(echo "$GATEWAY_OUTPUT" | grep "GATEWAY_ID=" | cut -d'=' -f2)
        GATEWAY_URL=$(echo "$GATEWAY_OUTPUT" | grep "GATEWAY_URL=" | cut -d'=' -f2)
        
        print_info "Gateway created successfully!"
        echo ""
        echo "========================================="
        echo "Deployment Complete!"
        echo "========================================="
        echo "Gateway ID: $GATEWAY_ID"
        echo "Gateway URL: $GATEWAY_URL"
        echo ""
        echo "Add this to your MCP client configuration:"
        echo ""
        echo '{
  "mcpServers": {
    "aws-finops-agentcore": {
      "command": "mcp-client",
      "args": ["--url", "'$GATEWAY_URL'"]
    }
  }
}'
        echo ""
    else
        print_error "Failed to create gateway. Check the error above."
        exit 1
    fi
}

deploy_runtime() {
    print_info "Deploying to AgentCore Runtime (Containerized)..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker not found. Please install Docker first."
        exit 1
    fi
    
    # Step 1: Create Dockerfile
    print_info "Step 1/5: Creating Dockerfile for AgentCore..."
    
    cat > Dockerfile.agentcore << 'EOF'
FROM --platform=linux/arm64 python:3.13-slim-bookworm

WORKDIR /app

RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
COPY src/ ./src/

RUN pip install --no-cache-dir -e .

EXPOSE 8000

ENV MCP_SERVER_MODE=http
ENV MCP_SERVER_HOST=0.0.0.0
ENV MCP_SERVER_PORT=8000
ENV PYTHONUNBUFFERED=1

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["python", "-m", "aws_finops_mcp"]
EOF
    
    # Step 2: Build Docker image
    print_info "Step 2/5: Building Docker image (this may take a few minutes)..."
    docker buildx build --platform linux/arm64 \
      -t $ECR_REPO_NAME:latest \
      -f Dockerfile.agentcore . > /dev/null
    
    print_info "Docker image built successfully"
    
    # Step 3: Create ECR repository and push
    print_info "Step 3/5: Creating ECR repository and pushing image..."
    
    if ! aws ecr describe-repositories --repository-names $ECR_REPO_NAME &> /dev/null; then
        aws ecr create-repository --repository-name $ECR_REPO_NAME --region $AWS_REGION > /dev/null
    fi
    
    # Authenticate Docker to ECR
    aws ecr get-login-password --region $AWS_REGION | \
      docker login --username AWS --password-stdin \
      $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com > /dev/null
    
    # Tag and push
    IMAGE_URI=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME:latest
    docker tag $ECR_REPO_NAME:latest $IMAGE_URI
    docker push $IMAGE_URI > /dev/null
    
    print_info "Image pushed to ECR: $IMAGE_URI"
    
    # Step 4: Install AgentCore toolkit
    print_info "Step 4/5: Installing AgentCore starter toolkit..."
    pip install -q bedrock-agentcore-starter-toolkit
    
    # Step 5: Deploy to Runtime
    print_info "Step 5/5: Deploying to AgentCore Runtime..."
    
    cat > /tmp/runtime_deployment.py << EOF
import sys
from bedrock_agentcore_starter_toolkit import AgentCoreClient

try:
    client = AgentCoreClient(region_name='$AWS_REGION')
    
    runtime_response = client.create_runtime(
        name='$RUNTIME_NAME',
        description='AWS FinOps MCP Server Runtime',
        image_uri='$IMAGE_URI',
        protocol_version='2025-03-26',
        environment_variables={
            'AWS_REGION': '$AWS_REGION',
            'MCP_SERVER_MODE': 'http',
            'MCP_SERVER_HOST': '0.0.0.0',
            'MCP_SERVER_PORT': '8000'
        }
    )
    
    runtime_id = runtime_response['runtimeId']
    runtime_url = runtime_response['runtimeUrl']
    
    print(f"RUNTIME_ID={runtime_id}")
    print(f"RUNTIME_URL={runtime_url}")
    print("SUCCESS")
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
EOF
    
    RUNTIME_OUTPUT=$(python3 /tmp/runtime_deployment.py)
    
    if echo "$RUNTIME_OUTPUT" | grep -q "SUCCESS"; then
        RUNTIME_ID=$(echo "$RUNTIME_OUTPUT" | grep "RUNTIME_ID=" | cut -d'=' -f2)
        RUNTIME_URL=$(echo "$RUNTIME_OUTPUT" | grep "RUNTIME_URL=" | cut -d'=' -f2)
        
        print_info "Runtime deployed successfully!"
        echo ""
        echo "========================================="
        echo "Deployment Complete!"
        echo "========================================="
        echo "Runtime ID: $RUNTIME_ID"
        echo "Runtime URL: $RUNTIME_URL"
        echo ""
        echo "Add this to your MCP client configuration:"
        echo ""
        echo '{
  "mcpServers": {
    "aws-finops-agentcore": {
      "command": "mcp-client",
      "args": ["--url", "'$RUNTIME_URL'"]
    }
  }
}'
        echo ""
    else
        print_error "Failed to deploy runtime. Check the error above."
        exit 1
    fi
}

# Main execution
main() {
    echo ""
    echo "AWS FinOps MCP Server - AgentCore Deployment"
    echo "============================================="
    echo ""
    
    check_prerequisites
    show_menu
    
    case $DEPLOYMENT_METHOD in
        gateway)
            deploy_gateway
            ;;
        runtime)
            deploy_runtime
            ;;
    esac
    
    print_info "Deployment completed successfully!"
    print_info "See BEDROCK_AGENTCORE_DEPLOYMENT.md for detailed documentation."
}

# Run main function
main
