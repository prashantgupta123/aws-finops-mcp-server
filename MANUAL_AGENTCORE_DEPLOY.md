# Manual AgentCore Runtime Deployment Guide

Since the automated script has API compatibility issues, follow these manual steps to deploy to Amazon Bedrock AgentCore Runtime.

## Prerequisites

```bash
# Install required packages
pip install bedrock-agentcore-starter-toolkit bedrock-agentcore strands-agents boto3

# Verify installation
agentcore --help
```

## Step 1: Create AgentCore Configuration

Create `.bedrock_agentcore.yaml` in your project root:

```yaml
agents:
  aws-finops-mcp:
    name: aws-finops-mcp-server
    description: AWS FinOps MCP Server for cost optimization
    runtime:
      type: container
      dockerfile: Dockerfile.agentcore
      platform: linux/arm64
      port: 8000
      health_check:
        path: /health
        interval: 30
        timeout: 10
        retries: 3
    environment:
      MCP_SERVER_MODE: http
      MCP_SERVER_HOST: 0.0.0.0
      MCP_SERVER_PORT: "8000"
      PYTHONUNBUFFERED: "1"
      AWS_REGION: us-east-1

default_agent: aws-finops-mcp
```

## Step 2: Verify Dockerfile

Ensure `Dockerfile.agentcore` exists (it should already be created):

```bash
ls -la Dockerfile.agentcore
```

## Step 3: Test Locally (Optional)

```bash
# Start local development server
agentcore dev

# In another terminal, test
agentcore invoke --dev "Hello!"
```

## Step 4: Deploy to AgentCore Runtime

### Option A: Using AgentCore CLI (Recommended)

```bash
# Deploy to AWS
agentcore launch

# This will:
# 1. Build your container using AWS CodeBuild
# 2. Create necessary AWS resources
# 3. Deploy to AgentCore Runtime
# 4. Configure CloudWatch logging
```

### Option B: Using Docker + ECR + AWS CLI

If `agentcore launch` doesn't work, use this manual approach:

```bash
# 1. Set variables
export AWS_REGION=us-east-1
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export ECR_REPO_NAME=aws-finops-mcp-server

# 2. Build Docker image
docker buildx build --platform linux/arm64 \
  -t $ECR_REPO_NAME:latest \
  -f Dockerfile.agentcore .

# 3. Create ECR repository
aws ecr create-repository \
  --repository-name $ECR_REPO_NAME \
  --region $AWS_REGION

# 4. Authenticate Docker to ECR
aws ecr get-login-password --region $AWS_REGION | \
  docker login --username AWS --password-stdin \
  $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# 5. Tag and push image
docker tag $ECR_REPO_NAME:latest \
  $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME:latest

docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME:latest

# 6. Deploy using Python SDK
python3 << 'EOF'
import boto3
from bedrock_agentcore_starter_toolkit import Runtime
import os

# Get environment variables
aws_region = os.getenv('AWS_REGION', 'us-east-1')
aws_account_id = os.getenv('AWS_ACCOUNT_ID')
ecr_repo_name = os.getenv('ECR_REPO_NAME', 'aws-finops-mcp-server')

image_uri = f"{aws_account_id}.dkr.ecr.{aws_region}.amazonaws.com/{ecr_repo_name}:latest"

print(f"Deploying image: {image_uri}")

# Initialize Runtime
runtime = Runtime()

# Configure
runtime.configure(
    image_uri=image_uri,
    env_vars={
        'AWS_REGION': aws_region,
        'MCP_SERVER_MODE': 'http',
        'MCP_SERVER_HOST': '0.0.0.0',
        'MCP_SERVER_PORT': '8000'
    }
)

# Launch to AgentCore Runtime
result = runtime.launch(local=False)

print(f"\n✅ Deployment successful!")
print(f"Agent ARN: {result.agent_arn}")
print(f"Agent URL: {result.agent_url}")
print(f"\nTest with: agentcore invoke '{{\"prompt\": \"list unused resources\"}}'")
EOF
```

## Step 5: Test Deployed Agent

```bash
# Test using CLI
agentcore invoke '{"prompt": "list unused lambda functions in us-east-1"}'

# Or use AWS SDK
python3 << 'EOF'
import boto3
import json

client = boto3.client('bedrock-agentcore-runtime', region_name='us-east-1')

# Replace with your agent ARN from deployment
agent_arn = "arn:aws:bedrock-agentcore:us-east-1:ACCOUNT:agent/AGENT_ID"

response = client.invoke_agent_runtime(
    agentArn=agent_arn,
    inputText='list unused lambda functions'
)

print(json.dumps(response, indent=2, default=str))
EOF
```

## Step 6: View Logs

```bash
# View CloudWatch logs
aws logs tail /aws/bedrock-agentcore/runtime/aws-finops-mcp-server --follow

# Or use agentcore CLI
agentcore status
```

## Troubleshooting

### Issue: `agentcore launch` fails

**Solution**: Use Option B (Docker + ECR + AWS CLI) above

### Issue: Permission denied

**Solution**: Ensure your IAM user/role has these permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock-agentcore:*",
        "ecr:*",
        "iam:CreateRole",
        "iam:AttachRolePolicy",
        "iam:PassRole",
        "logs:*",
        "codebuild:*"
      ],
      "Resource": "*"
    }
  ]
}
```

### Issue: Docker build fails

**Solution**: Ensure Docker is running and you have ARM64 support:

```bash
docker buildx ls
# Should show linux/arm64 platform
```

### Issue: Image push fails

**Solution**: Re-authenticate to ECR:

```bash
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  $(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com
```

## Alternative: AWS Console Deployment

1. **Build and push image** (Steps 1-5 from Option B above)

2. **Go to AWS Console**:
   - Navigate to Amazon Bedrock
   - Go to AgentCore → Runtime
   - Click "Create runtime"

3. **Configure runtime**:
   - Name: `aws-finops-mcp-server`
   - Image URI: `YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/aws-finops-mcp-server:latest`
   - Environment variables:
     - `MCP_SERVER_MODE=http`
     - `MCP_SERVER_HOST=0.0.0.0`
     - `MCP_SERVER_PORT=8000`
     - `AWS_REGION=us-east-1`

4. **Create and wait** for deployment to complete

5. **Test** using the console or CLI

## Next Steps

Once deployed:

1. **Monitor**: Check CloudWatch logs and metrics
2. **Test**: Invoke your agent with various prompts
3. **Optimize**: Adjust container resources if needed
4. **Scale**: Configure auto-scaling if needed

## Resources

- [AgentCore Documentation](https://docs.aws.amazon.com/bedrock-agentcore/)
- [Starter Toolkit GitHub](https://github.com/aws/bedrock-agentcore-starter-toolkit)
- [Runtime Guide](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-get-started-toolkit.html)

---

**Need Help?** See [BEDROCK_AGENTCORE_DEPLOYMENT.md](./BEDROCK_AGENTCORE_DEPLOYMENT.md) for more details.
