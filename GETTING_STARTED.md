# Getting Started with AWS FinOps MCP Server

Welcome! This guide will help you get up and running with the AWS FinOps MCP Server in minutes.

## Prerequisites

- Python ≥3.13
- AWS Account with appropriate permissions
- AWS CLI configured (optional but recommended)
- MCP client (Kiro, Claude Desktop, etc.)

## Quick Start

### 1. Install the Package

```bash
# Navigate to the project directory
cd aws-finops-mcp-server

# Install the package
pip install .

# Or for development
pip install -e ".[dev]"
```

### 2. Configure AWS Credentials

```bash
# Configure AWS profile
aws configure --profile finops

# Or use default profile
aws configure
```

### 3. Configure MCP Client

**For Kiro** - Edit `~/.kiro/settings/mcp.json`:

```json
{
  "mcpServers": {
    "aws-finops": {
      "command": "python",
      "args": ["-m", "aws_finops_mcp"],
      "env": {
        "AWS_PROFILE": "default",
        "AWS_REGION": "us-east-1"
      }
    }
  }
}
```

**For Claude Desktop** - Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "aws-finops": {
      "command": "python",
      "args": ["-m", "aws_finops_mcp"],
      "env": {
        "AWS_PROFILE": "default",
        "AWS_REGION": "us-east-1"
      }
    }
  }
}
```

### 4. Restart Your MCP Client

Restart Kiro or Claude Desktop to load the new configuration.

### 5. Test It

Ask your MCP client:
```
Can you list all AWS FinOps tools available?
```

or

```
Can you get the cost breakdown by region for us-east-1?
```

---

## Detailed Setup

### Installation Options

#### Option 1: Quick Setup Script

```bash
./setup.sh
```

This will:
- Create a virtual environment
- Install all dependencies
- Verify the installation

#### Option 2: Manual Installation

```bash
# Using pip
pip install .

# Using uv
uv pip install .

# For development
pip install -e ".[dev]"
```

#### Option 3: Docker

```bash
# Build and run
./docker-run.sh run

# Or use Docker Compose
docker-compose up -d
```

### Verify Installation

```bash
python verify_installation.py
```

This will check:
- ✅ Python version
- ✅ Dependencies
- ✅ Package structure
- ✅ Tool availability
- ✅ AWS credentials (optional)

---

## AWS Configuration

### Option 1: AWS Profile (Recommended)

Configure an AWS profile:

```bash
aws configure --profile finops
```

Then use it in your MCP client config:

```json
{
  "env": {
    "AWS_PROFILE": "finops",
    "AWS_REGION": "us-east-1"
  }
}
```

```json
{
  "tool": "find_unused_lambda_functions",
  "arguments": {
    "profile_name": "finops",
    "region_name": "us-east-1"
  }
}
```

### Option 2: Environment Variables

```bash
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
export AWS_DEFAULT_REGION=us-east-1
```

### Option 3: IAM Role (for EC2/ECS)

No configuration needed - the server will automatically use instance profile credentials.

## MCP Client Setup

### For Kiro

Add to `~/.kiro/settings/mcp.json`:

```json
{
  "mcpServers": {
    "aws-finops": {
      "command": "python",
      "args": ["-m", "aws_finops_mcp"],
      "env": {
        "AWS_PROFILE": "finops",
        "AWS_REGION": "us-east-1"
      },
      "disabled": false
    }
  }
}
```

### For Claude Desktop

Add to Claude Desktop MCP configuration:

```json
{
  "mcpServers": {
    "aws-finops": {
      "command": "python",
      "args": ["-m", "aws_finops_mcp"]
    }
  }
}
```

## Your First Tool Call

### Via MCP Client

Ask your AI assistant:

> "Find unused Lambda functions in us-east-1 from the last 90 days"

The assistant will call:

```json
{
  "tool": "find_unused_lambda_functions",
  "arguments": {
    "profile_name": "finops",
    "region_name": "us-east-1",
    "period": 90
  }
}
```

### Via Python

```python
from aws_finops_mcp.session import get_aws_session
from aws_finops_mcp.tools import cleanup

# Create session
session = get_aws_session(
    profile_name="finops",
    region_name="us-east-1"
)

# Find unused Lambda functions
result = cleanup.find_unused_lambda_functions(
    session=session,
    region_name="us-east-1",
    period=90,
    max_results=100
)

# Display results
print(f"Found {result['count']} unused Lambda functions:")
for func in result['resource']:
    print(f"  - {func['FunctionName']}")
    print(f"    Runtime: {func['Runtime']}")
    print(f"    Memory: {func['MemorySize']} MB")
    print(f"    {func['Description']}")
    print()
```

## Common Use Cases

### 1. Cost Cleanup Analysis

Find all unused resources that can be deleted:

```python
from aws_finops_mcp.session import get_aws_session
from aws_finops_mcp.tools import cleanup

session = get_aws_session(profile_name="finops", region_name="us-east-1")

# Run all cleanup tools
results = {
    "Lambda Functions": cleanup.find_unused_lambda_functions(session, "us-east-1", 90),
    "Elastic IPs": cleanup.find_unused_elastic_ips(session, "us-east-1"),
    "AMIs": cleanup.find_unused_amis(session, "us-east-1", 90),
    "Load Balancers": cleanup.find_unused_load_balancers(session, "us-east-1", 90),
    "Security Groups": cleanup.find_unused_security_groups(session, "us-east-1"),
}

# Print summary
print("Cleanup Opportunities:")
for name, result in results.items():
    print(f"  {name}: {result['count']} unused")
```

### 2. Capacity Right-Sizing

Identify instances that need resizing:

```python
from aws_finops_mcp.session import get_aws_session
from aws_finops_mcp.tools import capacity

session = get_aws_session(profile_name="finops", region_name="us-east-1")

# Find underutilized instances
underutilized = capacity.find_underutilized_ec2_instances(session, "us-east-1", 30)

print(f"Underutilized EC2 Instances: {underutilized['count']}")
for instance in underutilized['resource']:
    print(f"\n  Instance: {instance['InstanceName']}")
    print(f"  Type: {instance['InstanceType']}")
    print(f"  Max CPU: {instance['MaxCPUUtilization']}%")
    print(f"  Max Memory: {instance['MaxMemoryUtilization']}%")
    print(f"  Recommendation: Downsize to save costs")
```

### 3. Cost Optimization

Get AWS-recommended cost optimizations:

```python
from aws_finops_mcp.session import get_aws_session
from aws_finops_mcp.tools import cost

session = get_aws_session(profile_name="finops", region_name="us-east-1")

# Get EC2 cost recommendations
ec2_recs = cost.get_cost_optimization_recommendations(
    session, "us-east-1", "Ec2Instance"
)

total_savings = sum(r['EstimatedMonthlySavings'] for r in ec2_recs['resource'])

print(f"EC2 Cost Optimization Recommendations: {ec2_recs['count']}")
print(f"Potential Monthly Savings: ${total_savings:.2f}")

for rec in ec2_recs['resource'][:5]:  # Show first 5
    print(f"\n  Resource: {rec['ResourceId']}")
    print(f"  Current: {rec['CurrentResourceSummary']}")
    print(f"  Recommended: {rec['RecommendedResourceSummary']}")
    print(f"  Monthly Savings: ${rec['EstimatedMonthlySavings']:.2f}")
    print(f"  Action: {rec['ActionType']}")
```

### 4. Multi-Region Analysis

Analyze multiple regions:

```python
from aws_finops_mcp.session import get_aws_session
from aws_finops_mcp.tools import cleanup

regions = ["us-east-1", "us-west-2", "eu-west-1"]

print("Multi-Region Unused Lambda Functions:")
for region in regions:
    session = get_aws_session(profile_name="finops", region_name=region)
    result = cleanup.find_unused_lambda_functions(session, region, 90)
    print(f"  {region}: {result['count']} unused functions")
```

## IAM Permissions

Create an IAM policy with minimum required permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:Describe*",
        "rds:Describe*",
        "lambda:List*",
        "elasticloadbalancing:Describe*",
        "ecs:Describe*",
        "ecs:List*",
        "logs:Describe*",
        "cloudwatch:GetMetricStatistics",
        "cloudwatch:Describe*",
        "autoscaling:Describe*",
        "cost-optimization-hub:ListRecommendations",
        "sts:AssumeRole",
        "sts:GetCallerIdentity"
      ],
      "Resource": "*"
    }
  ]
}
```

Attach this policy to your IAM user or role.

## Troubleshooting

### "Module not found" error

```bash
# Reinstall the package
pip install --force-reinstall .
```

### "AWS credentials not found" error

```bash
# Check AWS configuration
aws sts get-caller-identity

# Or configure credentials
aws configure
```

### "Permission denied" error

Check your IAM permissions match the required permissions above.

### "No resources found"

- Verify you're checking the correct region
- Ensure resources exist in that region
- Try increasing the `period` parameter
- Check if resources have the "Neglect" tag (for EC2)

## Next Steps

1. **Explore All Tools**: See [TOOLS_REFERENCE.md](TOOLS_REFERENCE.md) for complete tool documentation
2. **Read Examples**: Check [examples/tool_usage.md](examples/tool_usage.md) for more examples
3. **Understand Architecture**: Review [ARCHITECTURE.md](ARCHITECTURE.md) for system design
4. **Automate**: Create scripts to run regular analyses
5. **Integrate**: Connect with your monitoring and alerting systems

## Quick Reference

### All Tool Categories

1. **Cleanup** (9 tools): Find unused resources
2. **Capacity** (4 tools): Analyze utilization
3. **Cost** (5 tools): Get optimization recommendations
4. **Application** (2 tools): Monitor performance
5. **Upgrade** (1 tool): Find outdated configurations

### Common Parameters

- `profile_name`: AWS profile name
- `region_name`: AWS region (default: "us-east-1")
- `period`: Lookback period in days (default: 90)
- `max_results`: Maximum results (default: 100)

### Authentication Methods

1. Profile: `profile_name="finops"`
2. Role: `role_arn="arn:aws:iam::123456789012:role/FinOps"`
3. Keys: `access_key="AKIA..."`, `secret_access_key="..."`
4. Temporary: Add `session_token="..."`

## Support

- **Documentation**: See README.md, QUICKSTART.md, ARCHITECTURE.md
- **Examples**: Check examples/ directory
- **Issues**: Review common troubleshooting steps above

## What's Next?

Now that you're set up, try:

1. Run a cleanup analysis on your AWS account
2. Identify underutilized resources
3. Get cost optimization recommendations
4. Set up automated weekly reports
5. Integrate with your FinOps workflow

Happy optimizing! 🚀


---

## Troubleshooting

### Issue: "Request timed out" or "Connection error"

**Cause**: Incorrect MCP configuration

**Solution**: Make sure you're using stdio mode (not HTTP mode) for MCP clients:

```json
{
  "mcpServers": {
    "aws-finops": {
      "command": "python",
      "args": ["-m", "aws_finops_mcp"],
      "env": {
        "AWS_PROFILE": "default",
        "AWS_REGION": "us-east-1"
      }
    }
  }
}
```

**Don't use**: HTTP wrapper scripts or `MCP_SERVER_URL` for MCP clients!

---

### Issue: "Module not found"

**Cause**: Package not installed

**Solution**:
```bash
cd aws-finops-mcp-server
pip install -e .
```

---

### Issue: "AWS credentials not found"

**Cause**: AWS profile not configured

**Solution**:
```bash
aws configure --profile your-profile
```

Or set environment variables:
```bash
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
export AWS_REGION=us-east-1
```

---

### Issue: "Access Denied" errors

**Cause**: Insufficient IAM permissions

**Solution**: See [IAM_SETUP_GUIDE.md](IAM_SETUP_GUIDE.md) for required permissions.

Quick fix:
```bash
# Use the automated IAM setup script
cd iam-policies/examples
./create-iam-role.sh finops-mcp-role full ec2
```

---

## Understanding the Two Modes

### stdio Mode (For MCP Clients) ✅

**Use for**: Kiro, Claude Desktop, any MCP client

**How it works**: Direct stdin/stdout communication

**Configuration**:
```json
{
  "command": "python",
  "args": ["-m", "aws_finops_mcp"]
}
```

**When to use**: Always for MCP clients!

---

### HTTP Mode (For Remote Access) 🌐

**Use for**: Remote access, REST API, curl commands

**How it works**: HTTP server with REST API

**Start server**:
```bash
export MCP_SERVER_MODE=http
python -m aws_finops_mcp

# Or with Docker
docker-compose -f docker-compose-http.yml up -d
```

**Access**:
```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/mcp -d '{"tool":"...","arguments":{...}}'
```

**When to use**: When you need remote access or REST API

**See**: [REMOTE_ACCESS_GUIDE.md](REMOTE_ACCESS_GUIDE.md) for complete HTTP mode setup

---

## Next Steps

1. ✅ **Explore Tools**: See [TOOLS_REFERENCE.md](TOOLS_REFERENCE.md) for all 24 tools
2. ✅ **Setup IAM**: See [IAM_SETUP_GUIDE.md](IAM_SETUP_GUIDE.md) for permissions
3. ✅ **Deploy**: See [DEPLOYMENT.md](DEPLOYMENT.md) for deployment options
4. ✅ **Remote Access**: See [REMOTE_ACCESS_GUIDE.md](REMOTE_ACCESS_GUIDE.md) for HTTP mode

---

## Quick Reference

### MCP Client Config (stdio mode)
```json
{
  "mcpServers": {
    "aws-finops": {
      "command": "python",
      "args": ["-m", "aws_finops_mcp"],
      "env": {
        "AWS_PROFILE": "default",
        "AWS_REGION": "us-east-1"
      }
    }
  }
}
```

### Test Commands
```bash
# Verify installation
python verify_installation.py

# Test AWS credentials
aws sts get-caller-identity

# Run in stdio mode (default)
python -m aws_finops_mcp

# Run in HTTP mode
MCP_SERVER_MODE=http python -m aws_finops_mcp
```

---

**Need Help?** Check the troubleshooting section above or see the other documentation files!

**Last Updated**: January 22, 2026
