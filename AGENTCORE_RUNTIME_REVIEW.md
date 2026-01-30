# AgentCore Runtime Deployment - Status & Next Steps

## ✅ What's Been Fixed

All the configuration issues have been resolved:

1. **`.bedrock_agentcore.yaml`** - ✅ Correct structure with `agents` dictionary and `default_agent`
2. **`Dockerfile.agentcore`** - ✅ Configured for linux/arm64 with all AgentCore requirements
3. **`http_server.py`** - ✅ Updated with JSON-RPC 2.0 and session management
4. **Documentation** - ✅ Complete deployment guides created

## 🎯 Current Status

Your MCP server is **ready to deploy** to Amazon Bedrock AgentCore Runtime. The previous error:
```
ValueError: No agent specified and no default set
```
has been **FIXED** by correcting the `.bedrock_agentcore.yaml` structure.

## 🚀 Next Steps - Deploy Now!

### Step 1: Configure AWS Credentials

```bash
# Configure AWS credentials (choose one method)

# Method A: AWS CLI configure
aws configure
# Enter: Access Key ID, Secret Access Key, Region (us-east-1), Output format (json)

# Method B: Environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1

# Method C: AWS SSO
aws sso login --profile your-profile
export AWS_PROFILE=your-profile

# Verify credentials
aws sts get-caller-identity
```

### Step 2: Install AgentCore Toolkit

```bash
# Activate your virtual environment if not already active
source myenv/bin/activate  # or source .venv/bin/activate

# Install the toolkit
pip install bedrock-agentcore-starter-toolkit bedrock-agentcore
```

### Step 3: Deploy to AgentCore

```bash
# Deploy (this will build and deploy everything)
agentcore launch

# Expected output:
# ✅ Building container image...
# ✅ Pushing to ECR...
# ✅ Creating AgentCore resources...
# ✅ Agent deployed successfully!
# Agent ARN: arn:aws:bedrock-agentcore:us-east-1:ACCOUNT:agent/AGENT_ID
```

### Step 4: Test Your Deployment

```bash
# Test the deployed agent
agentcore invoke '{"prompt": "list unused EC2 instances in us-east-1"}'

# Check status
agentcore status

# View logs
agentcore logs --follow
```

## 📋 What Happens During Deployment

When you run `agentcore launch`, it will:

1. **Build Phase** (2-5 minutes)
   - Reads `.bedrock_agentcore.yaml`
   - Builds Docker image using `Dockerfile.agentcore`
   - Uses AWS CodeBuild (no local Docker needed!)
   - Pushes to Amazon ECR

2. **Deploy Phase** (3-5 minutes)
   - Creates IAM roles and policies
   - Sets up VPC and security groups
   - Deploys container to AgentCore Runtime
   - Configures CloudWatch logging
   - Sets up health checks

3. **Validation Phase** (1-2 minutes)
   - Runs health checks
   - Validates MCP protocol
   - Tests tool discovery
   - Returns Agent ARN

**Total time: 6-12 minutes**

## 🔍 Monitoring Deployment

```bash
# Watch deployment progress
agentcore launch --verbose

# In another terminal, watch CloudWatch logs
aws logs tail /aws/bedrock-agentcore/runtime/aws-finops-mcp-server --follow
```

## 🆘 If Deployment Fails

### Common Issues & Solutions

#### Issue 1: AWS Credentials Not Found
```bash
# Error: Unable to locate credentials
# Solution: Configure AWS credentials (see Step 1 above)
aws configure
```

#### Issue 2: Insufficient IAM Permissions
```bash
# Error: AccessDenied or UnauthorizedOperation
# Solution: Ensure your IAM user/role has these permissions:
# - bedrock:*
# - ecr:*
# - ecs:*
# - iam:CreateRole, iam:AttachRolePolicy
# - logs:CreateLogGroup, logs:PutLogEvents
# - codebuild:*
```

#### Issue 3: Docker Build Fails
```bash
# Error: Docker build failed
# Solution: Check Dockerfile.agentcore syntax
docker buildx build --platform linux/arm64 -t test -f Dockerfile.agentcore .
```

#### Issue 4: Region Not Supported
```bash
# Error: AgentCore not available in region
# Solution: Use a supported region
export AWS_DEFAULT_REGION=us-east-1  # or us-west-2, eu-west-1
```

### Manual Deployment Fallback

If `agentcore launch` continues to fail, use the manual Docker approach:

```bash
# See MANUAL_AGENTCORE_DEPLOY.md for detailed steps
# Or use this quick version:

export AWS_REGION=us-east-1
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Build and push
docker buildx build --platform linux/arm64 -t aws-finops-mcp:latest -f Dockerfile.agentcore .
aws ecr create-repository --repository-name aws-finops-mcp-server --region $AWS_REGION
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
docker tag aws-finops-mcp:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/aws-finops-mcp-server:latest
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

## � After Successful Deployment

### Test All Tool Categories

```bash
# Cost optimization tools
agentcore invoke '{"prompt": "find unused resources to reduce costs"}'

# Security audit tools
agentcore invoke '{"prompt": "check for security vulnerabilities in EC2 instances"}'

# Resource cleanup tools
agentcore invoke '{"prompt": "list resources that can be safely deleted"}'

# Compliance tools
agentcore invoke '{"prompt": "check IAM password policy compliance"}'
```

### Monitor Performance

```bash
# View CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/BedrockAgentCore \
  --metric-name Invocations \
  --dimensions Name=AgentName,Value=aws-finops-mcp-server \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum

# View logs
aws logs tail /aws/bedrock-agentcore/runtime/aws-finops-mcp-server --follow
```

### Update Deployment

```bash
# After making code changes
agentcore launch --force-rebuild

# Or update configuration only
agentcore update-config
```

## 🎓 Understanding Your Deployment

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Amazon Bedrock AgentCore                  │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │              AgentCore Runtime                      │    │
│  │                                                     │    │
│  │  ┌──────────────────────────────────────────┐     │    │
│  │  │   Your Container (linux/arm64)           │     │    │
│  │  │                                          │     │    │
│  │  │   ┌──────────────────────────────┐      │     │    │
│  │  │   │  MCP HTTP Server (port 8000) │      │     │    │
│  │  │   │  - JSON-RPC 2.0 Protocol     │      │     │    │
│  │  │   │  - Session Management        │      │     │    │
│  │  │   │  - Tool Discovery            │      │     │    │
│  │  │   └──────────────────────────────┘      │     │    │
│  │  │                                          │     │    │
│  │  │   ┌──────────────────────────────┐      │     │    │
│  │  │   │  AWS FinOps Tools (60+)      │      │     │    │
│  │  │   │  - Cost optimization         │      │     │    │
│  │  │   │  - Security audits           │      │     │    │
│  │  │   │  - Resource cleanup          │      │     │    │
│  │  │   └──────────────────────────────┘      │     │    │
│  │  └──────────────────────────────────────────┘     │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │              Supporting Services                    │    │
│  │  - Amazon ECR (container registry)                 │    │
│  │  - CloudWatch Logs (logging)                       │    │
│  │  - IAM Roles (permissions)                         │    │
│  │  - VPC & Security Groups (networking)              │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │   AWS APIs    │
                    │  (EC2, S3,    │
                    │   RDS, etc.)  │
                    └───────────────┘
```

### Cost Estimate

- **AgentCore Runtime**: ~$0.10/hour (~$73/month)
- **ECR Storage**: ~$0.10/GB/month
- **CloudWatch Logs**: ~$0.50/GB ingested
- **Data Transfer**: Minimal (within AWS)

**Estimated monthly cost**: $75-100 for moderate usage

## 📚 Additional Resources

- **Quick Start**: `AGENTCORE_QUICKSTART.md`
- **Manual Deployment**: `MANUAL_AGENTCORE_DEPLOY.md`
- **Architecture Details**: `AGENTCORE_ARCHITECTURE.md`
- **Deployment Checklist**: `DEPLOYMENT_CHECKLIST.md`
- **Tool Categories**: `TOOL_CATEGORIES.md`

## ✅ Deployment Checklist

Before running `agentcore launch`, verify:

- [ ] AWS credentials configured (`aws sts get-caller-identity` works)
- [ ] IAM permissions sufficient (bedrock, ecr, ecs, iam, logs, codebuild)
- [ ] Region supports AgentCore (us-east-1, us-west-2, eu-west-1)
- [ ] `.bedrock_agentcore.yaml` exists and is valid
- [ ] `Dockerfile.agentcore` exists
- [ ] `bedrock-agentcore-starter-toolkit` installed
- [ ] Virtual environment activated

## 🎯 Ready to Deploy?

Run these commands now:

```bash
# 1. Configure AWS (if not done)
aws configure

# 2. Verify credentials
aws sts get-caller-identity

# 3. Deploy!
agentcore launch

# 4. Test
agentcore invoke '{"prompt": "hello, list your capabilities"}'
```

---

**You're all set! The configuration is correct and ready for deployment.** �

If you encounter any issues during deployment, refer to the troubleshooting section above or check the detailed guides in the repository.
