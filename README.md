# AWS FinOps MCP Server

Model Context Protocol (MCP) server for AWS Financial Operations (FinOps) - providing comprehensive tools for cloud resource optimization, cost management, and performance monitoring.

## Features

### 🧹 Cleanup Tools (17 tools - 7 NEW!)
Identify unused AWS resources with comprehensive details including cost estimates, tags, and configuration:

**Compute & Storage (10 tools):**
- **Unused Lambda Functions** - 13 fields including ARN, code size, timeout, role, VPC, cost estimate, tags
- **Unused Elastic IPs** - 10 fields including allocation ID, network border group, cost estimate ($3.60/month), tags
- **Unused AMIs** - 14 fields including snapshots, architecture, virtualization, storage cost, tags
- **Unused Snapshots** - 13 fields including size, encryption, owner, cost estimate ($0.05/GB/month), tags
- **Unused Load Balancers** - 16 fields including ARN, state, AZs, security groups, cost estimate (ALB $22.50, NLB $32.40/month), tags
- **Unused Target Groups** - 14 fields including ARN, target type, health check config, attached LBs, tags
- **Unused CloudWatch Log Groups** - 12 fields including ARN, age, storage size, KMS key, metric filters, cost estimate, tags
- **Unused Security Groups** - 11 fields including owner, rule counts, SG references, tags
- **Unused EBS Volumes** - 19 fields including IOPS, throughput, snapshot ID, encryption, cost estimate, tags
- **Unused ECS Resources** - Task Definitions, Clusters, Services

**Network & Infrastructure (5 NEW tools):**
- **Unused NAT Gateways** ⭐ NEW - 13 fields including state, VPC, subnet, elastic IP, cost estimate ($32.40/month), tags
- **Unused VPC Endpoints** ⭐ NEW - 12 fields including type, service name, subnets, cost estimate ($7.20/month per AZ), tags
- **Unused Internet Gateways** ⭐ NEW - 6 fields including state, VPC, attachments, tags
- **Unused S3 Buckets** ⭐ NEW - 11 fields including region, object count, size, storage class, versioning, cost estimate, tags
- **Unused CloudWatch Alarms** ⭐ NEW - 13 fields including state, metric, namespace, actions, cost estimate ($0.10/month), tags

**Containers & Messaging (6 NEW tools):**
- **Old ECS Task Definitions** ⭐ NEW - 11 fields including family, revision, CPU, memory, network mode
- **Unused ECR Images** ⭐ NEW - 9 fields including repository, digest, tags, size, cost estimate ($0.10/GB/month)
- **Unused Launch Templates** ⭐ NEW - 10 fields including version, creation time, age, tags
- **Unused SQS Queues** ⭐ NEW - 8 fields including URL, message count, retention, queue type, tags
- **Unused SNS Topics** ⭐ NEW - 7 fields including ARN, subscriptions, owner, tags
- **Unused EventBridge Rules** ⭐ NEW - 9 fields including state, event pattern, schedule, target count, tags

**Database & Monitoring (4 NEW tools):**
- **Unused DynamoDB Tables** ⭐ NEW - 12 fields including item count, size, billing mode, capacity, cost estimate, tags
- **Unused CloudWatch Dashboards** ⭐ NEW - 7 fields including last modified, widget count, cost estimate ($3/month)

All cleanup tools include:
- ✅ **Cost Estimates** - Monthly cost savings potential
- ✅ **Full ARNs** - For automation and cross-referencing
- ✅ **Complete Tags** - Cost allocation and ownership tracking
- ✅ **Age Calculations** - Prioritize cleanup efforts
- ✅ **Security Details** - Encryption, KMS keys, ownership
- ✅ **Total Savings** - Aggregate cost savings per tool

### 📊 Capacity Tools (4 tools)
Analyze resource utilization for right-sizing:
- Underutilized EC2 Instances
- Overutilized EC2 Instances
- Underutilized RDS Instances
- Overutilized RDS Instances

### 💰 Cost Optimization Tools (6 tools - 1 NEW!)
AWS Cost Optimization Hub recommendations + Storage optimization:
- EC2 Instance optimization
- Lambda Function optimization
- EBS Volume optimization
- RDS optimization (instances & storage)
- All resource types (19 types)
- **S3 Storage Class Recommendations** ⭐ NEW - Intelligent-Tiering, Glacier recommendations with 30-95% savings

### 📊 Cost Explorer Tools (4 tools)
AWS Cost Explorer analysis:
- Cost breakdown by region
- Cost breakdown by service
- Cost breakdown by region and service
- Daily cost trend analysis

### 🚀 Application Performance Tools (2 tools)
Monitor application health:
- Target Group Error Rate analysis
- Target Group Response Time analysis

### 🔄 Upgrade Tools (1 tool)
Identify outdated configurations:
- Auto Scaling Groups using old AMIs

### 🌐 Deployment Modes

**Standard Mode (stdio)**: Direct integration with MCP clients  
**HTTP Server Mode**: Remote access via REST API for distributed deployments

- Run on EC2 and connect from anywhere
- SSH tunnel for secure development
- HTTPS with Nginx for production
- AWS Systems Manager for no-SSH access
- API endpoints: `/health`, `/tools`, `/mcp`

## Installation

### Quick Start (Virtual Environment)

```bash
# Automated setup
./setup.sh

# Run the server (stdio mode)
./run.sh

# Run tests
./test.sh
```

### Manual Installation

```bash
# Using pip
pip install .

# Using uv
uv pip install .

# For development
pip install -e ".[dev]"
```

### Docker Installation

#### Option 1: Standard Mode (stdio)
```bash
# Build and run with Docker
./docker-run.sh run

# Or use Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f
```

#### Option 2: HTTP Server Mode (Remote Access)
```bash
# Run with HTTP server for remote access
docker-compose -f docker-compose-http.yml up -d

# Test the server
curl http://localhost:8000/health

# View logs
docker-compose -f docker-compose-http.yml logs -f
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment options including EC2, ECS, Lambda, and Kubernetes.

See [REMOTE_ACCESS_GUIDE.md](REMOTE_ACCESS_GUIDE.md) for remote access setup and configuration.

## Usage

### Mode 1: Standard MCP Server (stdio)

Add to your MCP client configuration (e.g., Kiro's `mcp.json`):

```json
{
  "mcpServers": {
    "aws-finops": {
      "command": "python",
      "args": ["-m", "aws_finops_mcp"],
      "env": {
        "AWS_PROFILE": "your-profile",
        "AWS_REGION": "us-east-1"
      }
    }
  }
}
```

Or using uvx:

```json
{
  "mcpServers": {
    "aws-finops": {
      "command": "uvx",
      "args": ["aws-finops-mcp-server"]
    }
  }
}
```

### Mode 2: HTTP Server (Remote Access)

Run the server in HTTP mode for remote access:

```bash
# Set environment variable
export MCP_SERVER_MODE=http
export MCP_SERVER_HOST=0.0.0.0
export MCP_SERVER_PORT=8000

# Run the server
python -m aws_finops_mcp

# Or use Docker
docker-compose -f docker-compose-http.yml up -d
```

#### HTTP API Endpoints

**Health Check**:
```bash
curl http://localhost:8000/health
```

**List Tools**:
```bash
curl http://localhost:8000/tools
```

**Execute Tool**:
```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "get_cost_by_region",
    "arguments": {
      "region_name": "us-east-1"
    }
  }'
```

#### Remote Access Options

**SSH Tunnel** (Recommended for Development):
```bash
# On EC2
docker-compose -f docker-compose-http.yml up -d

# On your laptop
ssh -i your-key.pem -L 8000:localhost:8000 ec2-user@your-ec2-ip -N

# Connect to localhost:8000
curl http://localhost:8000/health
```

**HTTPS with Nginx** (Recommended for Production):
```bash
# Automated setup on EC2
./setup-ec2-remote.sh yes yes your-domain.com

# Access via HTTPS
curl https://your-domain.com/health
```

See [REMOTE_ACCESS_GUIDE.md](REMOTE_ACCESS_GUIDE.md) for complete remote access setup instructions.

### Tool Parameters

All tools accept the following parameters:

**AWS Credentials** (one of):
- `profile_name`: AWS profile name
- `role_arn`: IAM role ARN to assume
- `access_key` + `secret_access_key`: Direct credentials
- `access_key` + `secret_access_key` + `session_token`: Temporary credentials

**Common Parameters**:
- `region_name`: AWS region (default: "us-east-1")
- `period`: Lookback period in days (default: 90)
- `max_results`: Maximum results to return (default: 100)

### Example Tool Calls

#### stdio Mode (MCP Client)

```python
# Find unused Lambda functions
{
  "tool": "find_unused_lambda_functions",
  "arguments": {
    "profile_name": "production",
    "region_name": "us-west-2",
    "period": 90
  }
}

# Find underutilized EC2 instances
{
  "tool": "find_underutilized_ec2_instances",
  "arguments": {
    "role_arn": "arn:aws:iam::123456789012:role/FinOpsRole",
    "region_name": "us-east-1",
    "period": 30
  }
}

# Get cost optimization recommendations
{
  "tool": "get_cost_optimization_ec2",
  "arguments": {
    "access_key": "AKIA...",
    "secret_access_key": "...",
    "region_name": "us-east-1"
  }
}
```

#### HTTP Mode (REST API)

```bash
# Find unused Lambda functions
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "find_unused_lambda_functions",
    "arguments": {
      "region_name": "us-west-2",
      "period": 90
    }
  }'

# Get cost by region
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "get_cost_by_region",
    "arguments": {
      "region_name": "us-east-1"
    }
  }'

# Find underutilized EC2 instances
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "find_underutilized_ec2_instances",
    "arguments": {
      "region_name": "us-east-1",
      "period": 30
    }
  }'
```

## AWS Permissions Required

### Quick Setup

We provide ready-to-use IAM policies for different use cases:

```bash
# Automated setup (recommended)
cd iam-policies/examples
./create-iam-role.sh finops-mcp-role full ec2

# Or create IAM user
./create-iam-user.sh finops-mcp-user full
```

### Available Policies

| Policy | Use Case | Tools Enabled |
|--------|----------|---------------|
| **Full Policy** | Production (recommended) | All 74 tools |
| **Minimal Policy** | Testing/Development | All 74 tools (basic) |
| **Read-Only Policy** | Maximum security | All 74 tools |
| **Cost-Only Policy** | Cost analysis only | 9 tools |

### Policy Files

- `iam-policies/finops-full-policy.json` - Complete permissions (recommended)
- `iam-policies/finops-minimal-policy.json` - Basic permissions
- `iam-policies/finops-readonly-policy.json` - Read-only access
- `iam-policies/finops-cost-only-policy.json` - Cost analysis only

### Setup Methods

**AWS Console**: Copy policy JSON → Create Policy → Attach to Role/User

**AWS CLI**:
```bash
aws iam create-policy \
  --policy-name FinOpsFullPolicy \
  --policy-document file://iam-policies/finops-full-policy.json
```

**Terraform**: See `iam-policies/examples/terraform-example.tf`

**CloudFormation**: See `iam-policies/examples/cloudformation-example.yaml`

📖 **Complete Guide**: See [IAM_SETUP_GUIDE.md](IAM_SETUP_GUIDE.md) for detailed instructions

## Architecture

```
src/aws_finops_mcp/
├── __main__.py        # Entry point (supports stdio and HTTP modes)
├── server.py          # FastMCP server with tool definitions
├── http_server.py     # HTTP server wrapper for remote access
├── session.py         # AWS session management
├── tools/
│   ├── cleanup.py     # Cleanup tools
│   ├── capacity.py    # Capacity analysis tools
│   ├── cost.py        # Cost optimization tools
│   ├── cost_explorer.py # Cost Explorer tools
│   ├── application.py # Application performance tools
│   └── upgrade.py     # Upgrade recommendation tools
└── utils/
    ├── helpers.py     # Helper functions
    └── metrics.py     # CloudWatch metrics utilities
```

### Deployment Modes

**stdio Mode** (Default):
```
MCP Client ←→ stdin/stdout ←→ MCP Server ←→ AWS APIs
```

**HTTP Mode** (Remote Access):
```
MCP Client ←→ HTTP/HTTPS ←→ MCP Server ←→ AWS APIs
           (REST API)
```

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/

# Lint
ruff check src/
```

## Environment Variables

### Server Configuration

```bash
# Server Mode
MCP_SERVER_MODE=http          # Enable HTTP server mode (default: stdio)
MCP_SERVER_HOST=0.0.0.0       # Host to bind to (default: 0.0.0.0)
MCP_SERVER_PORT=8000          # Port to listen on (default: 8000)

# AWS Configuration
AWS_REGION=us-east-1          # Default AWS region
AWS_PROFILE=default           # AWS profile name
AWS_ACCESS_KEY_ID=...         # AWS access key (not recommended)
AWS_SECRET_ACCESS_KEY=...     # AWS secret key (not recommended)

# Logging
PYTHONUNBUFFERED=1            # Enable unbuffered output
```

### Example Configurations

**stdio Mode** (Default):
```bash
python -m aws_finops_mcp
```

**HTTP Mode**:
```bash
export MCP_SERVER_MODE=http
export MCP_SERVER_HOST=0.0.0.0
export MCP_SERVER_PORT=8000
python -m aws_finops_mcp
```

**Docker HTTP Mode**:
```bash
docker run -e MCP_SERVER_MODE=http \
  -e MCP_SERVER_PORT=8000 \
  -p 8000:8000 \
  aws-finops-mcp-server
```

## License

MIT License

## Quick Reference

### Run Modes

| Mode | Command | Use Case |
|------|---------|----------|
| **stdio** | `python -m aws_finops_mcp` | Direct MCP client integration |
| **HTTP** | `MCP_SERVER_MODE=http python -m aws_finops_mcp` | Remote access, distributed deployments |

### Docker Commands

```bash
# stdio mode
docker-compose up -d

# HTTP mode
docker-compose -f docker-compose-http.yml up -d

# Test HTTP server
curl http://localhost:8000/health
```

### Remote Access

```bash
# SSH tunnel (development)
ssh -i key.pem -L 8000:localhost:8000 ec2-user@ec2-ip -N

# HTTPS setup (production)
./setup-ec2-remote.sh yes yes your-domain.com

# Test connection
./examples/test-remote-connection.sh http://localhost:8000
```

### Documentation

| Document | Description |
|----------|-------------|
| **[GETTING_STARTED.md](GETTING_STARTED.md)** | Complete setup guide with MCP configuration |
| **[TOOLS_REFERENCE.md](TOOLS_REFERENCE.md)** | All 74 tools documentation |
| **[DEPLOYMENT.md](DEPLOYMENT.md)** | Deployment options (EC2, ECS, Lambda, K8s) |
| **[REMOTE_ACCESS_GUIDE.md](REMOTE_ACCESS_GUIDE.md)** | HTTP mode and remote access setup |
| **[IAM_SETUP_GUIDE.md](IAM_SETUP_GUIDE.md)** | IAM permissions and policies |
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | System architecture and design |
| **[iam-policies/README.md](iam-policies/README.md)** | IAM policy templates |
