# AgentCore Deployment - Final Steps

## Current Status

Your configuration is **almost ready**! The toolkit is having trouble with the `ecr: auto` setting. Here are two solutions:

## ✅ Solution 1: Create ECR Repository Manually (RECOMMENDED)

Run this on your EC2 instance:

```bash
# Create ECR repository
./create-ecr-repo.sh

# Get the repository URI
REPO_URI=$(aws ecr describe-repositories --repository-names aws-finops-mcp-server --region us-east-1 --query 'repositories[0].repositoryUri' --output text)
echo "Repository URI: $REPO_URI"
```

Then update `.bedrock_agentcore.yaml` to use the repository URI instead of `auto`:

```yaml
agents:
  aws-finops-mcp:
    name: aws-finops-mcp-server
    description: AWS FinOps MCP Server for cost optimization and resource management
    entrypoint: src/aws_finops_mcp/__main__.py
    deployment_type: container
    aws:
      account: null
      region: us-east-1
      execution_role: auto
      ecr: aws-finops-mcp-server  # Use repository name instead of 'auto'
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

Then deploy:

```bash
agentcore launch
```

## ✅ Solution 2: Use CLI Configure Command

Instead of manually editing the YAML, use the CLI to configure everything:

```bash
# Configure the agent with all required settings
agentcore configure \
  --entrypoint src/aws_finops_mcp/__main__.py \
  --name aws-finops-mcp-server \
  --deployment-type container \
  --ecr auto \
  --execution-role auto \
  --region us-east-1 \
  --protocol MCP \
  --non-interactive

# Then deploy
agentcore launch
```

## 🔍 Understanding the Error

The error `ECR repository not configured and auto-create not enabled` suggests that:

1. The toolkit might not support `ecr: auto` in YAML format
2. OR it needs to be configured via CLI first
3. OR there's a version mismatch in the toolkit

## 📋 Complete Deployment Steps

### Step 1: Create ECR Repository

```bash
# On your EC2 instance
cd /root/aws-finops-mcp-server

# Create the repository
aws ecr create-repository \
  --repository-name aws-finops-mcp-server \
  --region us-east-1 \
  --image-scanning-configuration scanOnPush=true \
  --encryption-configuration encryptionType=AES256

# Verify it was created
aws ecr describe-repositories \
  --repository-names aws-finops-mcp-server \
  --region us-east-1
```

### Step 2: Update Configuration

Edit `.bedrock_agentcore.yaml` and change:

```yaml
ecr: auto
```

To:

```yaml
ecr: aws-finops-mcp-server
```

### Step 3: Deploy

```bash
agentcore launch
```

## 🎯 Expected Deployment Flow

Once the ECR issue is resolved, you should see:

```
🚀 Launching Bedrock AgentCore (codebuild mode - RECOMMENDED)...
Memory disabled - skipping memory creationStarting CodeBuild ARM64 deployment for agent 'aws-finops-mcp-server' to account 058029412961 (us-east-1)
Generated image tag: 20260129-XXXXXX-XXX
Setting up AWS resources (ECR repository, execution roles)...
✅ ECR repository configured: aws-finops-mcp-server
✅ Creating execution role...
✅ Starting CodeBuild project...
⏳ Building container image (this takes 5-10 minutes)...
✅ Container image built and pushed to ECR
✅ Creating AgentCore Runtime...
✅ Deploying agent...
✅ Agent deployed successfully!

Agent ARN: arn:aws:bedrock-agentcore:us-east-1:058029412961:agent/XXXXX
Agent URL: https://XXXXX.execute-api.us-east-1.amazonaws.com

Test with:
  agentcore invoke '{"prompt": "list unused resources"}'
```

## 🆘 Alternative: Manual Docker Deployment

If `agentcore launch` continues to have issues, you can deploy manually:

```bash
# Set variables
export AWS_REGION=us-east-1
export AWS_ACCOUNT_ID=058029412961

# Create ECR repository (if not exists)
aws ecr create-repository --repository-name aws-finops-mcp-server --region $AWS_REGION || true

# Build for ARM64
docker buildx build --platform linux/arm64 -t aws-finops-mcp:latest -f Dockerfile.agentcore .

# Login to ECR
aws ecr get-login-password --region $AWS_REGION | \
  docker login --username AWS --password-stdin \
  $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Tag and push
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
    env_vars={
        'AWS_REGION': os.getenv('AWS_REGION'),
        'MCP_SERVER_MODE': 'http',
        'MCP_SERVER_HOST': '0.0.0.0',
        'MCP_SERVER_PORT': '8000'
    }
)
result = runtime.launch(local=False)
print(f"✅ Agent deployed!")
print(f"Agent ARN: {result.agent_arn}")
EOF
```

## 📊 After Successful Deployment

### Test Your Agent

```bash
# Basic test
agentcore invoke '{"prompt": "hello, what can you do?"}'

# Cost optimization test
agentcore invoke '{"prompt": "find unused EC2 instances in us-east-1"}'

# Security audit test
agentcore invoke '{"prompt": "check for security vulnerabilities"}'
```

### Monitor Logs

```bash
# View logs
agentcore logs --follow

# Or use CloudWatch
aws logs tail /aws/bedrock-agentcore/runtime/aws-finops-mcp-server --follow
```

### Check Status

```bash
agentcore status
```

## 🔧 Troubleshooting

### Issue: "ECR repository not configured"

**Solution**: Create the ECR repository manually first (see Step 1 above)

### Issue: "execution_role not configured"

**Solution**: The `execution_role: auto` should work, but if not, create manually:

```bash
# Create execution role
aws iam create-role \
  --role-name bedrock-agentcore-execution-role \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "bedrock-agentcore.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'

# Attach policies
aws iam attach-role-policy \
  --role-name bedrock-agentcore-execution-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess

# Update config with role ARN
```

### Issue: CodeBuild fails

**Solution**: Check CodeBuild logs:

```bash
aws codebuild list-builds --region us-east-1
aws codebuild batch-get-builds --ids <build-id> --region us-east-1
```

### Issue: Container fails health check

**Solution**: Test locally first:

```bash
# Build and run locally
docker build -t test -f Dockerfile.agentcore .
docker run -p 8000:8000 -e MCP_SERVER_MODE=http test

# Test health endpoint
curl http://localhost:8000/health
```

## 📚 Next Steps After Deployment

1. **Test all tool categories**:
   ```bash
   agentcore invoke '{"prompt": "list all available tools"}'
   ```

2. **Set up monitoring**:
   - CloudWatch dashboards
   - Log insights
   - Alarms for errors

3. **Configure authentication** (optional):
   - OAuth with Cognito
   - API keys
   - IAM authentication

4. **Optimize costs**:
   - Monitor usage
   - Adjust idle timeout
   - Use reserved capacity

## 🎓 Summary

The key issue is that `ecr: auto` might not be working as expected. The simplest solution is:

1. **Create ECR repository manually**: `./create-ecr-repo.sh`
2. **Update config**: Change `ecr: auto` to `ecr: aws-finops-mcp-server`
3. **Deploy**: `agentcore launch`

This should get your agent deployed successfully!

---

**Need help?** Check the other guides:
- `MANUAL_AGENTCORE_DEPLOY.md` - Detailed manual deployment
- `AGENTCORE_RUNTIME_REVIEW.md` - Status and troubleshooting
- `QUICK_FIX_DEPLOYMENT.md` - Quick deployment guide
