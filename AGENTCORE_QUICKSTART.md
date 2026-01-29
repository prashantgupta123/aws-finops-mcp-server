# AWS FinOps MCP Server - AgentCore Quick Start

Get your AWS FinOps MCP Server running on Amazon Bedrock AgentCore in minutes!

## 🚀 Quick Deploy (Automated)

### Prerequisites
- AWS CLI configured with credentials
- Python 3.10+ installed
- Docker installed (for Runtime method only)

### One-Command Deploy

```bash
# Run the automated deployment script
./deploy-to-agentcore.sh
```

The script will:
1. Check prerequisites
2. Let you choose deployment method (Gateway or Runtime)
3. Automatically deploy everything
4. Provide you with the MCP server URL

## 📋 Manual Deploy (Step-by-Step)

### Method 1: Gateway (Lambda) - 5 Minutes

**Best for**: Quick setup, testing, individual tools

```bash
# 1. Install dependencies
pip install bedrock-agentcore-starter-toolkit

# 2. Create Lambda package
mkdir -p lambda-deployment
# ... (see BEDROCK_AGENTCORE_DEPLOYMENT.md for details)

# 3. Deploy Lambda
aws lambda create-function \
  --function-name aws-finops-mcp-server \
  --runtime python3.13 \
  --role arn:aws:iam::YOUR_ACCOUNT:role/FinOpsMCPLambdaRole \
  --handler lambda_handler.lambda_handler \
  --zip-file fileb://lambda-deployment.zip

# 4. Create Gateway
python3 << 'EOF'
from bedrock_agentcore_starter_toolkit import AgentCoreClient

client = AgentCoreClient(region_name='us-east-1')
gateway = client.create_gateway(
    name='finops-mcp-gateway',
    protocol_version='2025-03-26'
)
print(f"Gateway URL: {gateway['gatewayUrl']}")
EOF
```

### Method 2: Runtime (Container) - 10 Minutes

**Best for**: Production, complex workflows, long-running operations

```bash
# 1. Build Docker image
docker buildx build --platform linux/arm64 \
  -t aws-finops-mcp-server:latest \
  -f Dockerfile.agentcore .

# 2. Push to ECR
aws ecr create-repository --repository-name aws-finops-mcp-server
aws ecr get-login-password | docker login --username AWS --password-stdin \
  YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com

docker tag aws-finops-mcp-server:latest \
  YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/aws-finops-mcp-server:latest
docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/aws-finops-mcp-server:latest

# 3. Deploy to Runtime
python3 << 'EOF'
from bedrock_agentcore_starter_toolkit import AgentCoreClient

client = AgentCoreClient(region_name='us-east-1')
runtime = client.create_runtime(
    name='finops-mcp-runtime',
    image_uri='YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/aws-finops-mcp-server:latest',
    protocol_version='2025-03-26'
)
print(f"Runtime URL: {runtime['runtimeUrl']}")
EOF
```

## 🔧 Configure Your MCP Client

### For Kiro

Add to `~/.kiro/settings/mcp.json`:

```json
{
  "mcpServers": {
    "aws-finops-agentcore": {
      "command": "mcp-client",
      "args": ["--url", "https://your-deployment-url.amazonaws.com"],
      "env": {
        "AWS_REGION": "us-east-1"
      }
    }
  }
}
```

### For Cursor

Add to Cursor settings:

```json
{
  "mcp": {
    "servers": {
      "aws-finops-agentcore": {
        "url": "https://your-deployment-url.amazonaws.com"
      }
    }
  }
}
```

### For Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "aws-finops-agentcore": {
      "command": "mcp-client",
      "args": ["--url", "https://your-deployment-url.amazonaws.com"]
    }
  }
}
```

## ✅ Test Your Deployment

### Quick Health Check

```bash
# Test health endpoint
curl https://your-deployment-url.amazonaws.com/health

# Expected response:
# {"status": "healthy", "server": "aws-finops-mcp"}
```

### Test Tool Discovery

```bash
# List available tools
curl -X POST https://your-deployment-url.amazonaws.com/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {}
  }'
```

### Test Tool Execution

```bash
# Find unused Lambda functions
curl -X POST https://your-deployment-url.amazonaws.com/mcp \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

## 🎯 Use Cases

### 1. Cost Optimization

```bash
# Get cost by region
curl -X POST https://your-deployment-url.amazonaws.com/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "get_cost_by_region",
      "arguments": {"region_name": "us-east-1"}
    }
  }'
```

### 2. Resource Cleanup

```bash
# Find unused resources
curl -X POST https://your-deployment-url.amazonaws.com/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "find_unused_elastic_ips",
      "arguments": {"region_name": "us-east-1"}
    }
  }'
```

### 3. Security Audit

```bash
# Find unencrypted resources
curl -X POST https://your-deployment-url.amazonaws.com/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "find_unencrypted_ebs_volumes",
      "arguments": {"region_name": "us-east-1"}
    }
  }'
```

## 🔐 Security Best Practices

### 1. Enable OAuth Authentication

```bash
# Create Cognito User Pool
aws cognito-idp create-user-pool \
  --pool-name finops-mcp-users \
  --auto-verified-attributes email

# Create app client
aws cognito-idp create-user-pool-client \
  --user-pool-id YOUR_POOL_ID \
  --client-name finops-mcp-client \
  --generate-secret
```

### 2. Use IAM Roles (Not Access Keys)

```bash
# Attach IAM role to Lambda or ECS task
# Never hardcode credentials in environment variables
```

### 3. Enable CloudTrail Logging

```bash
# Monitor all API calls
aws cloudtrail create-trail \
  --name finops-mcp-audit \
  --s3-bucket-name your-audit-bucket
```

## 📊 Monitoring

### CloudWatch Dashboard

```bash
# Create dashboard
aws cloudwatch put-dashboard \
  --dashboard-name FinOpsMCP \
  --dashboard-body file://dashboard.json
```

### View Logs

```bash
# Lambda logs
aws logs tail /aws/lambda/aws-finops-mcp-server --follow

# Runtime logs
aws logs tail /aws/bedrock-agentcore/runtime/finops-mcp-runtime --follow
```

### Metrics

```bash
# View invocations
aws cloudwatch get-metric-statistics \
  --namespace AWS/BedrockAgentCore \
  --metric-name GatewayInvocations \
  --dimensions Name=GatewayId,Value=YOUR_GATEWAY_ID \
  --start-time 2025-01-28T00:00:00Z \
  --end-time 2025-01-28T23:59:59Z \
  --period 3600 \
  --statistics Sum
```

## 🐛 Troubleshooting

### Issue: "Permission Denied"

**Solution**: Check IAM policies

```bash
# Verify role permissions
aws iam get-role --role-name FinOpsMCPLambdaRole
aws iam list-attached-role-policies --role-name FinOpsMCPLambdaRole
```

### Issue: "Tools Not Found"

**Solution**: Synchronize gateway

```python
from bedrock_agentcore_starter_toolkit import AgentCoreClient

client = AgentCoreClient(region_name='us-east-1')
client.synchronize_gateway_targets(
    gateway_id='your-gateway-id',
    target_ids=['your-target-id']
)
```

### Issue: "Container Fails to Start"

**Solution**: Check logs and environment

```bash
# View logs
docker logs <container-id>

# Test locally
docker run -p 8000:8000 \
  -e AWS_REGION=us-east-1 \
  aws-finops-mcp-server:latest
```

## 📚 Next Steps

1. **Explore Tools**: See [TOOLS_REFERENCE.md](./TOOLS_REFERENCE.md) for all 76 tools
2. **Category Filtering**: Use `MCP_TOOL_CATEGORIES` to load only needed tools
3. **Production Setup**: See [BEDROCK_AGENTCORE_DEPLOYMENT.md](./BEDROCK_AGENTCORE_DEPLOYMENT.md)
4. **IAM Policies**: Review [IAM_SETUP_GUIDE.md](./IAM_SETUP_GUIDE.md)

## 🆘 Need Help?

- **Documentation**: [BEDROCK_AGENTCORE_DEPLOYMENT.md](./BEDROCK_AGENTCORE_DEPLOYMENT.md)
- **AWS Docs**: [Amazon Bedrock AgentCore](https://docs.aws.amazon.com/bedrock-agentcore/)
- **Issues**: Open an issue in the repository

## 🎉 Success!

You now have a fully functional AWS FinOps MCP Server running on Amazon Bedrock AgentCore!

Try asking your AI assistant:
- "Show me unused Lambda functions in us-east-1"
- "What's my AWS cost by region this month?"
- "Find all unencrypted EBS volumes"
- "List underutilized EC2 instances"

Happy optimizing! 🚀
