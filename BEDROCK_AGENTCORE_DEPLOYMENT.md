# Deploy AWS FinOps MCP Server on Amazon Bedrock AgentCore

This guide provides step-by-step instructions for deploying the AWS FinOps MCP Server on Amazon Bedrock AgentCore using two deployment methods: **Gateway** and **Runtime**.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Deployment Method 1: AgentCore Gateway (Lambda-based)](#deployment-method-1-agentcore-gateway-lambda-based)
4. [Deployment Method 2: AgentCore Runtime (Containerized)](#deployment-method-2-agentcore-runtime-containerized)
5. [Testing Your Deployment](#testing-your-deployment)
6. [Monitoring and Observability](#monitoring-and-observability)
7. [Troubleshooting](#troubleshooting)

---

## Overview

Amazon Bedrock AgentCore provides two deployment options for MCP servers:

### Gateway Method
- **Best for**: Wrapping existing Lambda functions or APIs as MCP tools
- **Pros**: Simpler setup, serverless, no container management
- **Cons**: Limited to Lambda execution time (15 minutes max)
- **Use case**: Quick deployment, individual tool exposure

### Runtime Method
- **Best for**: Custom containerized MCP servers with complex logic
- **Pros**: Full control, longer execution times, stateful operations
- **Cons**: Requires Docker, more complex setup
- **Use case**: Production deployments, complex workflows

---

## Prerequisites

### Required Tools and Accounts

1. **AWS Account** with appropriate permissions
2. **AWS CLI** installed and configured
   ```bash
   aws --version  # Should be 2.x or higher
   aws configure  # Set up your credentials
   ```

3. **Python 3.10+** installed
   ```bash
   python3 --version
   ```

4. **Docker** (for Runtime method only)
   ```bash
   docker --version
   ```

5. **AgentCore Starter Toolkit**
   ```bash
   pip install bedrock-agentcore-starter-toolkit
   ```

### IAM Permissions

Create an IAM policy with the following permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock-agentcore:CreateGateway",
                "bedrock-agentcore:GetGateway",
                "bedrock-agentcore:CreateGatewayTarget",
                "bedrock-agentcore:GetGatewayTarget",
                "bedrock-agentcore:SynchronizeGatewayTargets",
                "bedrock-agentcore:UpdateGatewayTarget",
                "bedrock-agentcore:CreateRuntime",
                "bedrock-agentcore:GetRuntime",
                "bedrock-agentcore:InvokeAgent"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "lambda:CreateFunction",
                "lambda:UpdateFunctionCode",
                "lambda:GetFunction",
                "lambda:InvokeFunction",
                "lambda:AddPermission"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "iam:CreateRole",
                "iam:AttachRolePolicy",
                "iam:PassRole",
                "iam:GetRole"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "ecr:CreateRepository",
                "ecr:GetAuthorizationToken",
                "ecr:BatchCheckLayerAvailability",
                "ecr:PutImage",
                "ecr:InitiateLayerUpload",
                "ecr:UploadLayerPart",
                "ecr:CompleteLayerUpload"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "cognito-idp:CreateUserPool",
                "cognito-idp:CreateUserPoolClient",
                "cognito-idp:DescribeUserPool"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "secretsmanager:CreateSecret",
                "secretsmanager:GetSecretValue"
            ],
            "Resource": "*"
        }
    ]
}
```

### Clone and Setup the Repository

```bash
# Clone the repository
git clone <your-repo-url>
cd aws-finops-mcp-server

# Install dependencies
./setup.sh

# Or manually
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

---

## Deployment Method 1: AgentCore Gateway (Lambda-based)

This method wraps your MCP server tools as Lambda functions and exposes them through AgentCore Gateway.

### Step 1: Prepare Lambda Function

Create a Lambda-compatible version of your MCP server:

```bash
# Create deployment directory
mkdir -p lambda-deployment
cd lambda-deployment
```

Create `lambda_handler.py`:

```python
"""Lambda handler for AWS FinOps MCP Server."""

import json
import logging
from typing import Any

# Import your MCP server tools
from aws_finops_mcp.session import get_aws_session
from aws_finops_mcp.tools import (
    cleanup, capacity, cost, cost_explorer, 
    network, storage, performance, security
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def lambda_handler(event, context):
    """
    Lambda handler for MCP tool execution.
    
    Expected event format:
    {
        "tool": "find_unused_lambda_functions",
        "arguments": {
            "region_name": "us-east-1",
            "period": 90
        }
    }
    """
    try:
        # Extract tool name and arguments
        tool_name = event.get('tool')
        arguments = event.get('arguments', {})
        
        if not tool_name:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing tool parameter'})
            }
        
        # Create AWS session (uses Lambda execution role)
        region = arguments.get('region_name', 'us-east-1')
        session = get_aws_session(region_name=region)
        
        # Route to appropriate tool
        result = execute_tool(tool_name, session, arguments)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'tool': tool_name,
                'result': result
            })
        }
        
    except Exception as e:
        logger.error(f"Error executing tool: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }


def execute_tool(tool_name: str, session: Any, arguments: dict) -> dict:
    """Execute the specified tool."""
    
    # Cleanup tools
    if tool_name == 'find_unused_lambda_functions':
        return cleanup.find_unused_lambda_functions(
            session, 
            arguments.get('region_name', 'us-east-1'),
            arguments.get('period', 90),
            arguments.get('max_results', 100)
        )
    
    elif tool_name == 'find_unused_elastic_ips':
        return cleanup.find_unused_elastic_ips(
            session,
            arguments.get('region_name', 'us-east-1')
        )
    
    # Cost tools
    elif tool_name == 'get_cost_by_region':
        return cost_explorer.get_cost_by_region(
            session,
            arguments.get('region_name', 'us-east-1'),
            arguments.get('start_date'),
            arguments.get('end_date')
        )
    
    # Add more tool mappings as needed...
    
    else:
        raise ValueError(f"Unknown tool: {tool_name}")
```

### Step 2: Package Lambda Function

```bash
# Install dependencies to package directory
pip install -t package/ boto3 mcp

# Copy your source code
cp -r ../src/aws_finops_mcp package/

# Create deployment package
cd package
zip -r ../lambda-deployment.zip .
cd ..
zip -g lambda-deployment.zip lambda_handler.py
```

### Step 3: Create IAM Role for Lambda

```bash
# Create trust policy
cat > lambda-trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Create role
aws iam create-role \
  --role-name FinOpsMCPLambdaRole \
  --assume-role-policy-document file://lambda-trust-policy.json

# Attach policies
aws iam attach-role-policy \
  --role-name FinOpsMCPLambdaRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# Attach FinOps policy (use your full policy from iam-policies/)
aws iam attach-role-policy \
  --role-name FinOpsMCPLambdaRole \
  --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/FinOpsFullPolicy
```

### Step 4: Deploy Lambda Function

```bash
# Get role ARN
ROLE_ARN=$(aws iam get-role --role-name FinOpsMCPLambdaRole --query 'Role.Arn' --output text)

# Create Lambda function
aws lambda create-function \
  --function-name aws-finops-mcp-server \
  --runtime python3.13 \
  --role $ROLE_ARN \
  --handler lambda_handler.lambda_handler \
  --zip-file fileb://lambda-deployment.zip \
  --timeout 300 \
  --memory-size 512 \
  --environment Variables="{AWS_REGION=us-east-1}"

# Wait for function to be active
aws lambda wait function-active --function-name aws-finops-mcp-server
```

### Step 5: Create AgentCore Gateway

Using Python with AgentCore Starter Toolkit:

```python
# gateway_setup.py
import boto3
from bedrock_agentcore_starter_toolkit import AgentCoreClient

# Initialize client
client = AgentCoreClient(region_name='us-east-1')

# Create gateway
gateway_response = client.create_gateway(
    name='finops-mcp-gateway',
    description='AWS FinOps MCP Server Gateway',
    protocol_version='2025-03-26'
)

gateway_id = gateway_response['gatewayId']
gateway_url = gateway_response['gatewayUrl']

print(f"Gateway created: {gateway_id}")
print(f"Gateway URL: {gateway_url}")

# Add Lambda target
target_response = client.create_gateway_target(
    gateway_id=gateway_id,
    name='finops-lambda-target',
    target_type='lambda',
    lambda_arn='arn:aws:lambda:us-east-1:YOUR_ACCOUNT_ID:function:aws-finops-mcp-server'
)

print(f"Target created: {target_response['targetId']}")

# Synchronize to discover tools
client.synchronize_gateway_targets(
    gateway_id=gateway_id,
    target_ids=[target_response['targetId']]
)

print("Gateway setup complete!")
print(f"Use this URL in your MCP client: {gateway_url}")
```

Run the setup:

```bash
python gateway_setup.py
```

### Step 6: Configure Authentication (Optional but Recommended)

```bash
# Create Cognito User Pool for OAuth
aws cognito-idp create-user-pool \
  --pool-name finops-mcp-users \
  --auto-verified-attributes email \
  --policies '{
    "PasswordPolicy": {
      "MinimumLength": 8,
      "RequireUppercase": true,
      "RequireLowercase": true,
      "RequireNumbers": true,
      "RequireSymbols": false
    }
  }'

# Create app client
aws cognito-idp create-user-pool-client \
  --user-pool-id <USER_POOL_ID> \
  --client-name finops-mcp-client \
  --generate-secret \
  --allowed-o-auth-flows authorization_code \
  --allowed-o-auth-scopes openid profile email
```

---

## Deployment Method 2: AgentCore Runtime (Containerized)

This method deploys your MCP server as a containerized application on AgentCore Runtime.

### Step 1: Create Dockerfile

The MCP server must be available at `0.0.0.0:8000/mcp` for AgentCore Runtime.

Create `Dockerfile.agentcore`:

```dockerfile
# Use Python 3.13 slim image for ARM64
FROM --platform=linux/arm64 python:3.13-slim-bookworm

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY pyproject.toml ./
COPY src/ ./src/

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Expose port 8000
EXPOSE 8000

# Set environment variables
ENV MCP_SERVER_MODE=http
ENV MCP_SERVER_HOST=0.0.0.0
ENV MCP_SERVER_PORT=8000
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Run the server
CMD ["python", "-m", "aws_finops_mcp"]
```

### Step 2: Update HTTP Server for AgentCore

Modify `src/aws_finops_mcp/http_server.py` to ensure `/mcp` endpoint compatibility:

```python
# Add this to your MCPHTTPHandler class

def do_POST(self) -> None:
    """Handle POST requests (MCP tool calls)."""
    # Support both /mcp and root path
    if self.path in ["/mcp", "/"]:
        try:
            # Add session ID support for AgentCore
            session_id = self.headers.get("Mcp-Session-Id", "default")
            
            # Read request body
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            request_data = json.loads(body.decode())

            # Handle MCP JSON-RPC format
            if "jsonrpc" in request_data:
                result = self._handle_jsonrpc(request_data, session_id)
            else:
                # Legacy format
                result = self._handle_legacy(request_data)

            # Send response
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result, indent=2).encode())

        except json.JSONDecodeError:
            self.send_error_response(400, "Invalid JSON")
        except Exception as e:
            logger.error(f"Error executing tool: {e}")
            self.send_error_response(500, str(e))
    else:
        self.send_response(404)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        response = {"error": "Not found"}
        self.wfile.write(json.dumps(response).encode())

def _handle_jsonrpc(self, request: dict, session_id: str) -> dict:
    """Handle JSON-RPC 2.0 format requests."""
    method = request.get("method")
    params = request.get("params", {})
    request_id = request.get("id")
    
    # Handle different MCP methods
    if method == "tools/list":
        tools = self._get_available_tools()
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {"tools": tools}
        }
    elif method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        result = self._execute_tool(tool_name, arguments)
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }
    else:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"}
        }
```

### Step 3: Build and Test Docker Image Locally

```bash
# Build for ARM64 (required by AgentCore)
docker buildx build --platform linux/arm64 \
  -t aws-finops-mcp-server:latest \
  -f Dockerfile.agentcore .

# Test locally
docker run -p 8000:8000 \
  -e AWS_REGION=us-east-1 \
  -e AWS_ACCESS_KEY_ID=your-key \
  -e AWS_SECRET_ACCESS_KEY=your-secret \
  aws-finops-mcp-server:latest

# Test health endpoint
curl http://localhost:8000/health

# Test MCP endpoint
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {}
  }'
```

### Step 4: Push to Amazon ECR

```bash
# Set variables
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPO_NAME=aws-finops-mcp-server

# Create ECR repository
aws ecr create-repository \
  --repository-name $ECR_REPO_NAME \
  --region $AWS_REGION

# Authenticate Docker to ECR
aws ecr get-login-password --region $AWS_REGION | \
  docker login --username AWS --password-stdin \
  $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Tag image
docker tag aws-finops-mcp-server:latest \
  $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME:latest

# Push image
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME:latest

# Save image URI
IMAGE_URI=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME:latest
echo "Image URI: $IMAGE_URI"
```

### Step 5: Deploy to AgentCore Runtime

Using Python with AgentCore Starter Toolkit:

```python
# runtime_deployment.py
import boto3
from bedrock_agentcore_starter_toolkit import AgentCoreClient

# Initialize client
client = AgentCoreClient(region_name='us-east-1')

# Image URI from ECR
image_uri = 'YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/aws-finops-mcp-server:latest'

# Create runtime
runtime_response = client.create_runtime(
    name='finops-mcp-runtime',
    description='AWS FinOps MCP Server Runtime',
    image_uri=image_uri,
    protocol_version='2025-03-26',
    environment_variables={
        'AWS_REGION': 'us-east-1',
        'MCP_SERVER_MODE': 'http',
        'MCP_SERVER_HOST': '0.0.0.0',
        'MCP_SERVER_PORT': '8000'
    }
)

runtime_id = runtime_response['runtimeId']
runtime_url = runtime_response['runtimeUrl']

print(f"Runtime created: {runtime_id}")
print(f"Runtime URL: {runtime_url}")
print(f"Use this URL in your MCP client: {runtime_url}")
```

Run the deployment:

```bash
python runtime_deployment.py
```

### Step 6: Configure Authentication with Cognito

```python
# auth_setup.py
import boto3

cognito = boto3.client('cognito-idp', region_name='us-east-1')

# Create user pool
user_pool = cognito.create_user_pool(
    PoolName='finops-mcp-runtime-users',
    AutoVerifiedAttributes=['email'],
    Policies={
        'PasswordPolicy': {
            'MinimumLength': 8,
            'RequireUppercase': True,
            'RequireLowercase': True,
            'RequireNumbers': True,
            'RequireSymbols': False
        }
    }
)

user_pool_id = user_pool['UserPool']['Id']

# Create app client
app_client = cognito.create_user_pool_client(
    UserPoolId=user_pool_id,
    ClientName='finops-mcp-runtime-client',
    GenerateSecret=True,
    AllowedOAuthFlows=['authorization_code'],
    AllowedOAuthScopes=['openid', 'profile', 'email'],
    CallbackURLs=['https://your-callback-url.com'],
    AllowedOAuthFlowsUserPoolClient=True
)

print(f"User Pool ID: {user_pool_id}")
print(f"Client ID: {app_client['UserPoolClient']['ClientId']}")
```

---

## Testing Your Deployment

### Test with MCP Inspector

```bash
# Install MCP Inspector
npm install -g @modelcontextprotocol/inspector

# Test Gateway deployment
mcp-inspector https://your-gateway-url.amazonaws.com

# Test Runtime deployment
mcp-inspector https://your-runtime-url.amazonaws.com
```

### Test with Python Client

```python
# test_deployment.py
import requests
import json

# Your gateway or runtime URL
MCP_URL = "https://your-deployment-url.amazonaws.com/mcp"

# Test tools/list
response = requests.post(
    MCP_URL,
    headers={"Content-Type": "application/json"},
    json={
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {}
    }
)

print("Available tools:")
print(json.dumps(response.json(), indent=2))

# Test tool execution
response = requests.post(
    MCP_URL,
    headers={"Content-Type": "application/json"},
    json={
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "find_unused_lambda_functions",
            "arguments": {
                "region_name": "us-east-1",
                "period": 90
            }
        }
    }
)

print("\nTool execution result:")
print(json.dumps(response.json(), indent=2))
```

### Test with Kiro or Cursor

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "aws-finops-agentcore": {
      "command": "mcp-client",
      "args": ["--url", "https://your-deployment-url.amazonaws.com"],
      "env": {
        "MCP_AUTH_TOKEN": "your-oauth-token"
      }
    }
  }
}
```

---

## Monitoring and Observability

### CloudWatch Metrics

Monitor your deployment with CloudWatch:

```bash
# View Lambda metrics (Gateway method)
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=aws-finops-mcp-server \
  --start-time 2025-01-28T00:00:00Z \
  --end-time 2025-01-28T23:59:59Z \
  --period 3600 \
  --statistics Sum

# View AgentCore Gateway metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/BedrockAgentCore \
  --metric-name GatewayInvocations \
  --dimensions Name=GatewayId,Value=your-gateway-id \
  --start-time 2025-01-28T00:00:00Z \
  --end-time 2025-01-28T23:59:59Z \
  --period 3600 \
  --statistics Sum
```

### CloudWatch Logs

```bash
# View Lambda logs
aws logs tail /aws/lambda/aws-finops-mcp-server --follow

# View AgentCore Runtime logs
aws logs tail /aws/bedrock-agentcore/runtime/finops-mcp-runtime --follow
```

### CloudTrail Auditing

```bash
# View API calls
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=ResourceName,AttributeValue=finops-mcp-gateway \
  --max-results 50
```

---

## Troubleshooting

### Common Issues

#### 1. Lambda Timeout

**Problem**: Lambda function times out after 15 minutes

**Solution**: 
- Use AgentCore Runtime for long-running operations
- Optimize tool execution time
- Increase Lambda timeout (max 15 minutes)

```bash
aws lambda update-function-configuration \
  --function-name aws-finops-mcp-server \
  --timeout 900
```

#### 2. Permission Denied

**Problem**: IAM permission errors

**Solution**: Verify IAM roles have correct policies

```bash
# Check Lambda execution role
aws iam get-role --role-name FinOpsMCPLambdaRole

# List attached policies
aws iam list-attached-role-policies --role-name FinOpsMCPLambdaRole
```

#### 3. Container Fails to Start

**Problem**: Docker container exits immediately

**Solution**: Check logs and environment variables

```bash
# View container logs
docker logs <container-id>

# Test locally with verbose logging
docker run -e PYTHONUNBUFFERED=1 aws-finops-mcp-server:latest
```

#### 4. Tools Not Discovered

**Problem**: Gateway doesn't show tools

**Solution**: Synchronize gateway targets

```python
from bedrock_agentcore_starter_toolkit import AgentCoreClient

client = AgentCoreClient(region_name='us-east-1')
client.synchronize_gateway_targets(
    gateway_id='your-gateway-id',
    target_ids=['your-target-id']
)
```

#### 5. Authentication Failures

**Problem**: 401 Unauthorized errors

**Solution**: Verify OAuth configuration

```bash
# Test Cognito token
aws cognito-idp initiate-auth \
  --auth-flow USER_PASSWORD_AUTH \
  --client-id your-client-id \
  --auth-parameters USERNAME=user@example.com,PASSWORD=YourPassword123
```

### Debug Mode

Enable debug logging:

```python
# For Lambda
import logging
logging.basicConfig(level=logging.DEBUG)

# For Docker
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=DEBUG
```

### Health Checks

```bash
# Gateway health
curl https://your-gateway-url.amazonaws.com/health

# Runtime health
curl https://your-runtime-url.amazonaws.com/health

# Lambda health
aws lambda invoke \
  --function-name aws-finops-mcp-server \
  --payload '{"tool":"health_check"}' \
  response.json
```

---

## Next Steps

1. **Configure Category Filtering**: Use `MCP_TOOL_CATEGORIES` environment variable to load only needed tools
2. **Set Up Monitoring**: Create CloudWatch dashboards for your deployment
3. **Implement CI/CD**: Automate deployments with AWS CodePipeline
4. **Scale**: Add multiple regions or accounts
5. **Optimize Costs**: Use Reserved Instances or Savings Plans for Lambda

## Additional Resources

- [Amazon Bedrock AgentCore Documentation](https://docs.aws.amazon.com/bedrock-agentcore/)
- [AgentCore Gateway Guide](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html)
- [AgentCore Runtime Guide](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-mcp.html)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [AWS FinOps MCP Server Documentation](./README.md)

---

**Need Help?** Open an issue in the repository or consult the AWS Bedrock AgentCore documentation.
