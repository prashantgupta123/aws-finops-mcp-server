# AWS FinOps MCP Server - AgentCore Deployment Checklist

Use this checklist to ensure a successful deployment to Amazon Bedrock AgentCore.

## Pre-Deployment Checklist

### ☐ Prerequisites

- [ ] AWS Account with appropriate permissions
- [ ] AWS CLI installed and configured (`aws --version`)
- [ ] AWS credentials configured (`aws sts get-caller-identity`)
- [ ] Python 3.10+ installed (`python3 --version`)
- [ ] Git installed (`git --version`)
- [ ] Repository cloned locally

### ☐ IAM Permissions

- [ ] Created IAM policy with required permissions
- [ ] Attached policy to IAM role or user
- [ ] Verified permissions with `aws iam simulate-principal-policy`
- [ ] Documented IAM role ARN for reference

### ☐ Decision Made

- [ ] Read [AGENTCORE_COMPARISON.md](./AGENTCORE_COMPARISON.md)
- [ ] Decided on deployment method (Gateway or Runtime)
- [ ] Understood cost implications
- [ ] Reviewed architecture diagrams

---

## Gateway (Lambda) Deployment Checklist

### ☐ Step 1: Prepare Environment

- [ ] Activated Python virtual environment
- [ ] Installed dependencies (`pip install -e .`)
- [ ] Verified installation (`python -c "import aws_finops_mcp"`)

### ☐ Step 2: Create Lambda Package

- [ ] Created `lambda-deployment` directory
- [ ] Installed dependencies to package directory
- [ ] Copied source code to package
- [ ] Created `lambda_handler.py`
- [ ] Created deployment ZIP file
- [ ] Verified ZIP file size (< 50MB uncompressed)

### ☐ Step 3: IAM Role Setup

- [ ] Created Lambda execution role
- [ ] Attached `AWSLambdaBasicExecutionRole` policy
- [ ] Attached FinOps policy (from `iam-policies/`)
- [ ] Verified role trust relationship
- [ ] Noted role ARN

### ☐ Step 4: Deploy Lambda Function

- [ ] Created Lambda function
- [ ] Uploaded deployment package
- [ ] Configured timeout (300 seconds)
- [ ] Configured memory (512 MB minimum)
- [ ] Set environment variables
- [ ] Tested Lambda function locally
- [ ] Verified function is active

### ☐ Step 5: Create AgentCore Gateway

- [ ] Installed AgentCore starter toolkit
- [ ] Created gateway with Python script
- [ ] Noted gateway ID
- [ ] Noted gateway URL
- [ ] Added Lambda as target
- [ ] Synchronized gateway targets
- [ ] Verified tools are discovered

### ☐ Step 6: Configure Authentication (Optional)

- [ ] Created Cognito User Pool
- [ ] Created User Pool Client
- [ ] Configured OAuth settings
- [ ] Created test user
- [ ] Tested authentication flow

### ☐ Step 7: Testing

- [ ] Health check passes (`curl .../health`)
- [ ] Tools list returns results
- [ ] Sample tool execution succeeds
- [ ] Verified CloudWatch logs
- [ ] Checked CloudWatch metrics

---

## Runtime (Container) Deployment Checklist

### ☐ Step 1: Docker Setup

- [ ] Docker installed (`docker --version`)
- [ ] Docker daemon running
- [ ] Docker buildx available
- [ ] Tested Docker with hello-world

### ☐ Step 2: Create Dockerfile

- [ ] Created `Dockerfile.agentcore`
- [ ] Configured for ARM64 platform
- [ ] Set correct port (8000)
- [ ] Set correct host (0.0.0.0)
- [ ] Added health check
- [ ] Set environment variables

### ☐ Step 3: Update HTTP Server

- [ ] Modified `http_server.py` for `/mcp` endpoint
- [ ] Added JSON-RPC 2.0 support
- [ ] Added session ID handling
- [ ] Tested locally with curl

### ☐ Step 4: Build Docker Image

- [ ] Built image for ARM64
- [ ] Tagged image appropriately
- [ ] Tested image locally
- [ ] Verified health endpoint works
- [ ] Verified MCP endpoint works
- [ ] Checked image size (< 10GB)

### ☐ Step 5: Push to ECR

- [ ] Created ECR repository
- [ ] Authenticated Docker to ECR
- [ ] Tagged image with ECR URI
- [ ] Pushed image to ECR
- [ ] Verified image in ECR console
- [ ] Noted image URI

### ☐ Step 6: Deploy to AgentCore Runtime

- [ ] Installed AgentCore starter toolkit
- [ ] Created runtime with Python script
- [ ] Noted runtime ID
- [ ] Noted runtime URL
- [ ] Configured environment variables
- [ ] Verified runtime is active

### ☐ Step 7: Configure Authentication (Optional)

- [ ] Created Cognito User Pool
- [ ] Created User Pool Client
- [ ] Configured OAuth settings
- [ ] Created test user
- [ ] Tested authentication flow

### ☐ Step 8: Testing

- [ ] Health check passes (`curl .../health`)
- [ ] Tools list returns results
- [ ] Sample tool execution succeeds
- [ ] Verified CloudWatch logs
- [ ] Checked CloudWatch metrics
- [ ] Tested session management

---

## Post-Deployment Checklist

### ☐ Configuration

- [ ] Configured MCP client (Kiro/Cursor/Claude)
- [ ] Added deployment URL to client config
- [ ] Configured authentication if enabled
- [ ] Tested connection from client
- [ ] Verified tools are accessible

### ☐ Monitoring Setup

- [ ] Created CloudWatch dashboard
- [ ] Set up CloudWatch alarms
  - [ ] High error rate alarm
  - [ ] High latency alarm
  - [ ] Cost threshold alarm
- [ ] Configured SNS notifications
- [ ] Tested alarm notifications

### ☐ Security

- [ ] Reviewed IAM policies (least privilege)
- [ ] Enabled CloudTrail logging
- [ ] Configured VPC (if required)
- [ ] Reviewed security group rules
- [ ] Enabled encryption at rest
- [ ] Enabled encryption in transit
- [ ] Documented security configuration

### ☐ Cost Management

- [ ] Set up AWS Budgets
- [ ] Configured cost alerts
- [ ] Reviewed pricing estimates
- [ ] Documented expected costs
- [ ] Set up cost allocation tags

### ☐ Documentation

- [ ] Documented deployment details
  - [ ] Gateway/Runtime ID
  - [ ] Deployment URL
  - [ ] IAM role ARNs
  - [ ] Cognito User Pool ID (if used)
- [ ] Created runbook for common operations
- [ ] Documented troubleshooting steps
- [ ] Shared access with team members

### ☐ Testing & Validation

- [ ] Tested all critical tools
- [ ] Verified error handling
- [ ] Tested authentication flow
- [ ] Verified logging works
- [ ] Tested from multiple clients
- [ ] Load tested (if production)

---

## Operational Checklist

### ☐ Daily Operations

- [ ] Check CloudWatch dashboard
- [ ] Review error logs
- [ ] Monitor costs
- [ ] Check alarm status

### ☐ Weekly Operations

- [ ] Review usage patterns
- [ ] Analyze performance metrics
- [ ] Check for updates
- [ ] Review security logs

### ☐ Monthly Operations

- [ ] Review and optimize costs
- [ ] Update dependencies
- [ ] Review IAM policies
- [ ] Backup configuration
- [ ] Update documentation

---

## Troubleshooting Checklist

### ☐ If Deployment Fails

- [ ] Check AWS CLI credentials
- [ ] Verify IAM permissions
- [ ] Check CloudWatch logs
- [ ] Review error messages
- [ ] Consult [BEDROCK_AGENTCORE_DEPLOYMENT.md](./BEDROCK_AGENTCORE_DEPLOYMENT.md)

### ☐ If Tools Not Found

- [ ] Synchronize gateway targets
- [ ] Check Lambda/container logs
- [ ] Verify MCP protocol version
- [ ] Test tool registration
- [ ] Check tool schema

### ☐ If Authentication Fails

- [ ] Verify Cognito configuration
- [ ] Check OAuth settings
- [ ] Test token generation
- [ ] Review IAM policies
- [ ] Check CloudTrail logs

### ☐ If Performance Issues

- [ ] Check CloudWatch metrics
- [ ] Review Lambda timeout settings
- [ ] Check container resources
- [ ] Analyze slow queries
- [ ] Consider scaling options

---

## Rollback Checklist

### ☐ If Rollback Needed

- [ ] Identify issue and impact
- [ ] Document reason for rollback
- [ ] Backup current configuration

**For Gateway:**
- [ ] Update Lambda function code to previous version
- [ ] Verify Lambda function works
- [ ] Test gateway connectivity

**For Runtime:**
- [ ] Tag previous working image
- [ ] Update runtime to use previous image
- [ ] Verify container starts
- [ ] Test runtime connectivity

**Post-Rollback:**
- [ ] Verify functionality restored
- [ ] Update documentation
- [ ] Analyze root cause
- [ ] Plan fix for next deployment

---

## Cleanup Checklist (If Removing Deployment)

### ☐ Gateway Cleanup

- [ ] Delete gateway targets
- [ ] Delete gateway
- [ ] Delete Lambda function
- [ ] Delete Lambda execution role
- [ ] Delete CloudWatch log groups
- [ ] Delete Cognito User Pool (if created)

### ☐ Runtime Cleanup

- [ ] Delete runtime
- [ ] Delete ECR images
- [ ] Delete ECR repository
- [ ] Delete CloudWatch log groups
- [ ] Delete Cognito User Pool (if created)

### ☐ General Cleanup

- [ ] Remove IAM policies
- [ ] Delete CloudWatch alarms
- [ ] Delete CloudWatch dashboards
- [ ] Remove cost budgets
- [ ] Update documentation

---

## Success Criteria

Your deployment is successful when:

✅ **Functional**
- [ ] Health check returns 200 OK
- [ ] Tools list returns all expected tools
- [ ] Sample tool executions succeed
- [ ] Authentication works (if enabled)
- [ ] MCP client can connect

✅ **Monitored**
- [ ] CloudWatch logs are being generated
- [ ] CloudWatch metrics are being recorded
- [ ] Alarms are configured and working
- [ ] CloudTrail is logging API calls

✅ **Secure**
- [ ] IAM policies follow least privilege
- [ ] Authentication is enabled (production)
- [ ] Encryption is enabled
- [ ] Security groups are configured
- [ ] CloudTrail is enabled

✅ **Cost-Optimized**
- [ ] Cost alerts are configured
- [ ] Usage is within budget
- [ ] Right-sized resources
- [ ] Category filtering enabled (if applicable)

✅ **Documented**
- [ ] Deployment details documented
- [ ] Runbook created
- [ ] Team members have access
- [ ] Troubleshooting guide available

---

## Quick Reference

### Automated Deployment
```bash
./deploy-to-agentcore.sh
```

### Manual Gateway Deployment
```bash
# See AGENTCORE_QUICKSTART.md - Method 1
```

### Manual Runtime Deployment
```bash
# See AGENTCORE_QUICKSTART.md - Method 2
```

### Health Check
```bash
curl https://your-deployment-url.amazonaws.com/health
```

### View Logs
```bash
# Gateway (Lambda)
aws logs tail /aws/lambda/aws-finops-mcp-server --follow

# Runtime (Container)
aws logs tail /aws/bedrock-agentcore/runtime/finops-mcp-runtime --follow
```

### Synchronize Gateway
```python
from bedrock_agentcore_starter_toolkit import AgentCoreClient
client = AgentCoreClient(region_name='us-east-1')
client.synchronize_gateway_targets(
    gateway_id='your-gateway-id',
    target_ids=['your-target-id']
)
```

---

## Additional Resources

- [AGENTCORE_QUICKSTART.md](./AGENTCORE_QUICKSTART.md) - Quick start guide
- [BEDROCK_AGENTCORE_DEPLOYMENT.md](./BEDROCK_AGENTCORE_DEPLOYMENT.md) - Complete guide
- [AGENTCORE_COMPARISON.md](./AGENTCORE_COMPARISON.md) - Method comparison
- [AGENTCORE_ARCHITECTURE.md](./AGENTCORE_ARCHITECTURE.md) - Architecture diagrams
- [IAM_SETUP_GUIDE.md](./IAM_SETUP_GUIDE.md) - IAM configuration

---

**Pro Tip**: Print this checklist and check off items as you complete them. It helps ensure nothing is missed!

Good luck with your deployment! 🚀
