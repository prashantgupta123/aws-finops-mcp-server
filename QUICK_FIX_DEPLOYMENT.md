# Quick Fix: Deploy to AgentCore Runtime

The automated script has API compatibility issues. Use this quick manual deployment instead.

## ⚡ Quick Deploy (5 Commands)

```bash
# 1. Install toolkit
pip install bedrock-agentcore-starter-toolkit bedrock-agentcore

# 2. Create config file
cat > .bedrock_agentcore.yaml << 'EOF'
agents:
  aws-finops-mcp:
    name: aws-finops-mcp-server
    description: AWS FinOps MCP Server for cost optimization
    entrypoint: src/aws_finops_mcp/__main__.py
    aws:
      account: null  # Auto-filled by toolkit
      region: us-east-1
    deployment_type: container
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
EOF

# 3. Test locally (optional)
agentcore dev
# In another terminal: agentcore invoke --dev "Hello!"

# 4. Deploy to AWS
agentcore launch

# 5. Test deployed agent
agentcore invoke '{"prompt": "list unused resources"}'
```

## ✅ That's It!

The `agentcore launch` command will:
- Build your container using AWS CodeBuild (no Docker needed locally!)
- Create all necessary AWS resources
- Deploy to AgentCore Runtime
- Configure CloudWatch logging

## 📋 What You Get

After deployment, you'll see:
```
✅ Agent deployed successfully!
Agent ARN: arn:aws:bedrock-agentcore:us-east-1:ACCOUNT:agent/AGENT_ID
Agent URL: https://...amazonaws.com

Test with:
  agentcore invoke '{"prompt": "your prompt here"}'
```

## 🔧 If `agentcore launch` Fails

Use the manual Docker approach:

```bash
# Set variables
export AWS_REGION=us-east-1
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Build and push to ECR
docker buildx build --platform linux/arm64 -t aws-finops-mcp:latest -f Dockerfile.agentcore .

aws ecr create-repository --repository-name aws-finops-mcp-server --region $AWS_REGION

aws ecr get-login-password --region $AWS_REGION | \
  docker login --username AWS --password-stdin \
  $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

docker tag aws-finops-mcp:latest \
  $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/aws-finops-mcp-server:latest

docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/aws-finops-mcp-server:latest

# Deploy using Python
python3 << 'EOF'
from bedrock_agentcore_starter_toolkit import Runtime
import os

runtime = Runtime()
runtime.configure(
    image_uri=f"{os.getenv('AWS_ACCOUNT_ID')}.dkr.ecr.{os.getenv('AWS_REGION')}.amazonaws.com/aws-finops-mcp-server:latest",
    env_vars={'AWS_REGION': os.getenv('AWS_REGION'), 'MCP_SERVER_MODE': 'http'}
)
result = runtime.launch(local=False)
print(f"Agent ARN: {result.agent_arn}")
EOF
```

## 🎯 Test Your Deployment

```bash
# Using CLI
agentcore invoke '{"prompt": "find unused lambda functions in us-east-1"}'

# Using Python
python3 << 'EOF'
import boto3
client = boto3.client('bedrock-agentcore-runtime')
response = client.invoke_agent_runtime(
    agentArn='YOUR_AGENT_ARN',
    inputText='list unused resources'
)
print(response)
EOF
```

## 📊 View Logs

```bash
# View logs
agentcore status

# Or use CloudWatch
aws logs tail /aws/bedrock-agentcore/runtime/aws-finops-mcp-server --follow
```

## 🆘 Still Having Issues?

See [MANUAL_AGENTCORE_DEPLOY.md](./MANUAL_AGENTCORE_DEPLOY.md) for detailed troubleshooting.

---

**The key is using `agentcore launch` - it handles everything for you!** 🚀
