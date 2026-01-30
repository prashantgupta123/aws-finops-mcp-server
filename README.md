# AWS FinOps MCP Server

> **Production-Ready Deployment**: This MCP server is optimized for deployment on Amazon Bedrock AgentCore Runtime

Model Context Protocol (MCP) server for AWS Financial Operations (FinOps) - providing comprehensive tools for cloud resource optimization, cost management, and performance monitoring.

## 🚀 Quick Start - Deploy to AWS

### Deploy to Amazon Bedrock AgentCore (Recommended)

Deploy your MCP server to production in minutes:

```bash
# 1. Create ECR repository
./create-ecr-repo.sh

# 2. Update configuration
sed -i 's/ecr: auto/ecr: aws-finops-mcp-server/' .bedrock_agentcore.yaml

# 3. Deploy to AWS
agentcore launch

# 4. Test your deployment
agentcore invoke '{"prompt": "find unused resources in us-east-1"}'
```

📖 **Complete Deployment Guides:**
- **[AGENTCORE_DEPLOYMENT_FINAL.md](AGENTCORE_DEPLOYMENT_FINAL.md)** - Complete deployment guide with troubleshooting
- **[AGENTCORE_QUICKSTART.md](AGENTCORE_QUICKSTART.md)** - Quick 5-minute deployment
- **[AGENTCORE_RUNTIME_REVIEW.md](AGENTCORE_RUNTIME_REVIEW.md)** - Status review and next steps
- **[QUICK_FIX_DEPLOYMENT.md](QUICK_FIX_DEPLOYMENT.md)** - Quick fixes for common issues
- **[MANUAL_AGENTCORE_DEPLOY.md](MANUAL_AGENTCORE_DEPLOY.md)** - Manual Docker deployment

### Local Development

```bash
# Install dependencies
pip install -e .

# Run locally
python -m aws_finops_mcp
```

## 🎯 Quick Overview

- **76 Tools** across 14 categories for comprehensive AWS optimization
- **Category Filtering** - Load only the tools you need (NEW!)
- **Dual Modes** - stdio for direct integration, HTTP for remote access
- **Cost Savings** - Identify unused resources and optimization opportunities
- **Security & Compliance** - Find unencrypted resources and security issues
- **Performance Analysis** - Analyze and optimize application performance
- **Ready-to-Use IAM Policies** - Get started in minutes

📊 **[View Architecture Diagrams](ARCHITECTURE_DIAGRAMS.md)** - Visual system architecture and data flows

## 🆕 What's New

### Category-Based Tool Filtering
**Problem**: Loading all 76 tools can be slow and overwhelming for MCP clients.

**Solution**: Use `MCP_TOOL_CATEGORIES` to enable only the categories you need!

```bash
# Load only cost and cleanup tools (25 tools instead of 76)
export MCP_TOOL_CATEGORIES="cleanup,cost"
python -m aws_finops_mcp

# 67% reduction in tool count, faster loading, easier navigation
```

**Benefits**:
- ⚡ **67-89% faster loading** for focused use cases
- 🎯 **Better organization** - see only relevant tools
- 🔧 **Flexible** - change categories without code changes
- ✅ **Backward compatible** - defaults to all tools

📖 See [TOOL_CATEGORIES.md](TOOL_CATEGORIES.md) for complete guide

### New Tools Added
- **Network**: NAT Gateways, VPC Endpoints, Internet Gateways, CloudFront, Route53
- **Storage**: S3 buckets, storage class recommendations
- **Containers**: ECS clusters/services, ECR images, launch templates
- **Messaging**: SQS queues, SNS topics, EventBridge rules
- **Database**: DynamoDB tables and utilization
- **Monitoring**: CloudWatch alarms and dashboards
- **Performance**: Lambda cold starts, API Gateway, DynamoDB throttling, RDS insights, CloudFront cache
- **Security**: Unencrypted resources, public S3 buckets, permissive security groups
- **Governance**: Untagged resources, tag compliance, cost allocation
- **Capacity**: ElastiCache, ECS services, Lambda utilization
- **Upgrade**: Lambda runtimes, EC2 generations, EBS types, RDS/ElastiCache engines, EKS versions
- **Cost**: Savings Plans, Reserved Instances, EBS optimization, snapshots, data transfer, NAT Gateway

## 📊 Tool Categories

| Category | Tools | Description |
|----------|-------|-------------|
| 🧹 **Cleanup** | 9 | Find unused resources to delete |
| 💰 **Cost** | 16 | Cost optimization and analysis |
| 📊 **Capacity** | 9 | Resource utilization and right-sizing |
| 🔒 **Security** | 5 | Security compliance checks |
| ⚡ **Performance** | 5 | Performance analysis and tuning |
| 🔄 **Upgrade** | 8 | Outdated resource detection |
| 🌐 **Network** | 5 | Network resource optimization |
| 💾 **Storage** | 2 | Storage optimization |
| 📦 **Containers** | 4 | Container resource management |
| 💬 **Messaging** | 3 | Messaging service cleanup |
| 🗄️ **Database** | 2 | Database optimization |
| 📈 **Monitoring** | 3 | Monitoring resource cleanup |
| 🚀 **Application** | 2 | Application health monitoring |
| 🏛️ **Governance** | 3 | Tagging and compliance |

**Total: 76 tools** - Use category filtering to load only what you need!

```bash
# Load only cost and cleanup tools (25 tools instead of 76)
export MCP_TOOL_CATEGORIES="cost,cleanup"
python -m aws_finops_mcp
```

📖 See [TOOL_CATEGORIES.md](TOOL_CATEGORIES.md) for complete documentation

## Features

**76 Tools Across 14 Categories** - Use category filtering to load only what you need!

### 🧹 Cleanup Tools (9 tools)
Find unused AWS resources to reduce costs:
- `find_unused_lambda_functions` - Lambda functions with no invocations
- `find_unused_elastic_ips` - Unattached Elastic IPs ($3.60/month each)
- `find_unused_amis` - AMIs not used by instances or ASGs
- `find_unused_load_balancers` - Load balancers with no traffic ($22-32/month)
- `find_unused_target_groups` - Target groups with no targets or traffic
- `find_unused_log_groups` - CloudWatch Log Groups with no recent events
- `find_unused_snapshots` - EBS snapshots not associated with AMIs ($0.05/GB/month)
- `find_unused_security_groups` - Security groups not attached to resources
- `find_unused_volumes` - Unattached EBS volumes

### 💰 Cost Tools (16 tools)
Cost optimization, analysis, and savings recommendations:

**Cost Optimization Hub:**
- `get_all_cost_optimization_recommendations` - All 19 resource types
- `get_cost_optimization_ec2` - EC2 instance recommendations
- `get_cost_optimization_lambda` - Lambda function recommendations
- `get_cost_optimization_rds` - RDS instance recommendations
- `get_cost_optimization_ebs` - EBS volume recommendations

**Cost Explorer:**
- `get_cost_by_region` - Cost breakdown by AWS region
- `get_cost_by_service` - Cost breakdown by AWS service
- `get_cost_by_region_and_service` - Combined region and service breakdown
- `get_daily_cost_trend` - Daily cost trends with statistics

**Savings & Optimization:**
- `get_savings_plans_recommendations` - Savings Plans recommendations
- `get_reserved_instance_recommendations` - RI purchase recommendations
- `analyze_reserved_instance_utilization` - RI utilization and coverage
- `get_ebs_volume_type_recommendations` - EBS volume type optimization
- `get_snapshot_lifecycle_recommendations` - Snapshot lifecycle management
- `analyze_data_transfer_costs` - Data transfer cost analysis
- `get_nat_gateway_optimization_recommendations` - NAT Gateway optimization

### 📊 Capacity Tools (9 tools)
Resource utilization analysis for right-sizing:

**Compute:**
- `find_underutilized_ec2_instances` - EC2 with low CPU/memory (≤20%)
- `find_overutilized_ec2_instances` - EC2 with high CPU/memory (≥80%)
- `find_underutilized_lambda_functions` - Lambda with low invocations

**Database:**
- `find_underutilized_rds_instances` - RDS with low CPU (≤20%)
- `find_overutilized_rds_instances` - RDS with high CPU (≥80%)
- `find_underutilized_dynamodb_tables` - DynamoDB with low capacity
- `find_overutilized_dynamodb_tables` - DynamoDB with high capacity (>80%)
- `find_underutilized_elasticache_clusters` - ElastiCache with low CPU (<20%)
- `find_overutilized_elasticache_clusters` - ElastiCache with high CPU/memory (>80%)

**Containers:**
- `find_underutilized_ecs_services` - ECS services with low CPU/memory (<20%)

### 🔒 Security Tools (5 tools)
Security compliance and best practices:
- `find_unencrypted_ebs_volumes` - EBS volumes without encryption
- `find_unencrypted_s3_buckets` - S3 buckets without default encryption
- `find_unencrypted_rds_instances` - RDS instances without encryption
- `find_public_s3_buckets` - S3 buckets with public access enabled
- `find_overly_permissive_security_groups` - Security groups with 0.0.0.0/0 rules

### ⚡ Performance Tools (5 tools)
Performance analysis and optimization:
- `analyze_lambda_cold_starts` - Lambda cold start analysis
- `analyze_api_gateway_performance` - API Gateway performance metrics
- `analyze_dynamodb_throttling` - DynamoDB throttling issues
- `analyze_rds_performance_insights` - RDS Performance Insights data
- `analyze_cloudfront_cache_hit_ratio` - CloudFront cache performance

### 🔄 Upgrade Tools (8 tools)
Identify outdated resources needing upgrades:

**Compute:**
- `find_asgs_with_old_amis` - Auto Scaling Groups using old AMIs
- `find_outdated_lambda_runtimes` - Lambda with deprecated runtimes
- `find_ec2_instances_with_old_generations` - EC2 using previous generation types
- `find_ebs_volumes_with_old_types` - EBS using previous generation types
- `find_outdated_ecs_platform_versions` - ECS not on latest platform version

**Database:**
- `find_outdated_rds_engine_versions` - RDS not on latest engine version
- `find_outdated_elasticache_engine_versions` - ElastiCache not on latest version

**Containers:**
- `find_outdated_eks_cluster_versions` - EKS not on latest Kubernetes version

### 🌐 Network Tools (5 tools)
Network resource optimization:
- `find_unused_nat_gateways` - NAT Gateways with no traffic ($32.40/month)
- `find_unused_vpc_endpoints` - VPC Endpoints with no connections ($7.20/month per AZ)
- `find_unused_internet_gateways` - Unattached Internet Gateways
- `find_unused_cloudfront_distributions` - CloudFront with no requests
- `find_unused_route53_hosted_zones` - Route53 zones with no queries

### 💾 Storage Tools (2 tools)
Storage optimization:
- `find_unused_s3_buckets` - S3 buckets with no activity
- `get_s3_storage_class_recommendations` - S3 storage class optimization (30-95% savings)

### 📦 Container Tools (4 tools)
Container and orchestration resource management:
- `find_old_ecs_task_definitions` - Old ECS task definitions not in use
- `find_unused_ecr_images` - Unused ECR images ($0.10/GB/month)
- `find_unused_launch_templates` - EC2 launch templates not in use
- `find_unused_ecs_clusters_and_services` - ECS clusters/services with no activity

### 💬 Messaging Tools (3 tools)
Messaging service optimization:
- `find_unused_sqs_queues` - SQS queues with no messages
- `find_unused_sns_topics` - SNS topics with no subscriptions/messages
- `find_unused_eventbridge_rules` - EventBridge rules with no invocations

### 🗄️ Database Tools (2 tools)
Database resource analysis:
- `find_unused_dynamodb_tables` - DynamoDB tables with no read/write activity
- `find_underutilized_dynamodb_tables` - DynamoDB with low capacity utilization

### 📈 Monitoring Tools (3 tools)
Monitoring resource cleanup:
- `find_unused_cloudwatch_alarms` - CloudWatch alarms in INSUFFICIENT_DATA state
- `find_orphaned_cloudwatch_dashboards` - Dashboards referencing deleted resources
- `find_orphaned_cloudwatch_alarms` - Alarms not associated with active resources

### 🚀 Application Tools (2 tools)
Application health monitoring:
- `find_target_groups_with_high_error_rate` - Target groups with 5XX errors (>5%)
- `find_target_groups_with_high_response_time` - Target groups with slow response times (>1s)

### 🏛️ Governance Tools (3 tools)
Resource governance and compliance:
- `find_untagged_resources` - Resources missing required tags
- `analyze_tag_compliance` - Tag compliance analysis across resources
- `generate_cost_allocation_report` - Cost allocation by tags

---

### ✨ Tool Features

All tools include:
- ✅ **Comprehensive Details** - Full ARNs, configurations, and metadata
- ✅ **Cost Estimates** - Monthly cost savings potential
- ✅ **Complete Tags** - Cost allocation and ownership tracking
- ✅ **Age Calculations** - Prioritize cleanup efforts
- ✅ **Security Details** - Encryption, KMS keys, ownership
- ✅ **Total Savings** - Aggregate cost savings per tool

### 🌐 Deployment Modes

**Standard Mode (stdio)**: Direct integration with MCP clients  
**HTTP Server Mode**: Remote access via REST API for distributed deployments

- Run on EC2 and connect from anywhere
- SSH tunnel for secure development
- HTTPS with Nginx for production
- AWS Systems Manager for no-SSH access
- API endpoints: `/health`, `/tools`, `/mcp`

## Installation

### 🚀 NEW: Deploy to Amazon Bedrock AgentCore

Deploy this MCP server to AWS Bedrock AgentCore for production-ready, scalable agent integration:

```bash
# Quick deployment (recommended)
pip install bedrock-agentcore-starter-toolkit
agentcore launch
```

**Quick Links:**
- ⚡ [Quick Fix Deployment](./QUICK_FIX_DEPLOYMENT.md) - Deploy in 5 commands
- 📖 [Manual Deployment Guide](./MANUAL_AGENTCORE_DEPLOY.md) - Step-by-step manual process
- 📚 [Complete Documentation](./BEDROCK_AGENTCORE_DEPLOYMENT.md) - Full deployment guide
- ⚖️ [Deployment Comparison](./AGENTCORE_COMPARISON.md) - Choose the right method

**Two Deployment Methods:**
1. **Gateway (Lambda)** - Quick setup, serverless, cost-effective
2. **Runtime (Container)** - Production-ready, unlimited execution time (use `agentcore launch`)

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

### 🎯 Tool Category Filtering (NEW!)

**Problem**: Loading all 76 tools can be slow and overwhelming for clients.

**Solution**: Use `MCP_TOOL_CATEGORIES` to enable only the tools you need!

```bash
# Enable only cleanup and cost tools (25 tools instead of 76)
export MCP_TOOL_CATEGORIES="cleanup,cost"
python -m aws_finops_mcp

# Enable all tools (default)
export MCP_TOOL_CATEGORIES="all"
python -m aws_finops_mcp
```

**Available Categories** (14 total):
- `cleanup` (9 tools) - Find unused resources
- `cost` (16 tools) - Cost optimization and analysis
- `capacity` (9 tools) - Resource utilization analysis
- `security` (5 tools) - Security compliance checks
- `performance` (5 tools) - Performance analysis
- `upgrade` (8 tools) - Outdated resource detection
- `network` (5 tools) - Network resource optimization
- `storage` (2 tools) - Storage optimization
- `containers` (4 tools) - Container resource management
- `database` (2 tools) - Database optimization
- `messaging` (3 tools) - Messaging service cleanup
- `monitoring` (3 tools) - Monitoring resource cleanup
- `application` (2 tools) - Application health monitoring
- `governance` (3 tools) - Tagging and compliance

📖 **See [TOOL_CATEGORIES.md](TOOL_CATEGORIES.md) for complete documentation and examples**

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
        "AWS_REGION": "us-east-1",
        "MCP_TOOL_CATEGORIES": "cleanup,cost,security"
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
| **Full Policy** | Production (recommended) | All 76 tools |
| **Minimal Policy** | Testing/Development | All 76 tools (basic) |
| **Read-Only Policy** | Maximum security | All 76 tools |
| **Cost-Only Policy** | Cost analysis only | 16 cost tools |

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
├── __main__.py            # Entry point (supports stdio and HTTP modes)
├── server.py              # FastMCP server with all 76 tools
├── server_filtered.py     # Filtered server with category support (NEW!)
├── tool_categories.py     # Category definitions and filtering logic (NEW!)
├── http_server.py         # HTTP server wrapper for remote access
├── session.py             # AWS session management
├── tools/
│   ├── cleanup.py         # Cleanup tools (9 tools)
│   ├── capacity.py        # Capacity analysis tools (4 tools)
│   ├── capacity_compute.py # Compute capacity tools (1 tool)
│   ├── capacity_database.py # Database capacity tools (4 tools)
│   ├── cost.py            # Cost optimization tools (5 tools)
│   ├── cost_explorer.py   # Cost Explorer tools (4 tools)
│   ├── cost_savings.py    # Savings recommendations (3 tools)
│   ├── cost_storage.py    # Storage cost optimization (2 tools)
│   ├── cost_network.py    # Network cost optimization (2 tools)
│   ├── application.py     # Application performance tools (2 tools)
│   ├── upgrade.py         # Upgrade recommendations (1 tool)
│   ├── upgrade_compute.py # Compute upgrade tools (4 tools)
│   ├── upgrade_database.py # Database upgrade tools (2 tools)
│   ├── upgrade_containers.py # Container upgrade tools (1 tool)
│   ├── network.py         # Network optimization tools (5 tools)
│   ├── storage.py         # Storage optimization tools (2 tools)
│   ├── containers.py      # Container management tools (4 tools)
│   ├── messaging.py       # Messaging service tools (3 tools)
│   ├── database.py        # Database optimization tools (2 tools)
│   ├── monitoring.py      # Monitoring resource tools (3 tools)
│   ├── performance.py     # Performance analysis tools (5 tools)
│   ├── security.py        # Security compliance tools (5 tools)
│   └── governance.py      # Governance and tagging tools (3 tools)
└── utils/
    ├── helpers.py         # Helper functions
    └── metrics.py         # CloudWatch metrics utilities
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

### Category Filtering (NEW!)

```
User sets MCP_TOOL_CATEGORIES="cleanup,cost"
         ↓
__main__.py checks environment variable
         ↓
Loads server_filtered.py instead of server.py
         ↓
Only 25 tools registered (cleanup: 9 + cost: 16)
         ↓
Client sees only relevant tools
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

# Tool Filtering (NEW!)
MCP_TOOL_CATEGORIES=cleanup,cost  # Enable specific categories (default: all)
                                  # Options: cleanup, cost, capacity, security,
                                  #          performance, upgrade, network, storage,
                                  #          containers, messaging, database,
                                  #          monitoring, application, governance

# AWS Configuration
AWS_REGION=us-east-1          # Default AWS region
AWS_PROFILE=default           # AWS profile name
AWS_ACCESS_KEY_ID=...         # AWS access key (not recommended)
AWS_SECRET_ACCESS_KEY=...     # AWS secret key (not recommended)

# Logging
PYTHONUNBUFFERED=1            # Enable unbuffered output
```

### Example Configurations

**stdio Mode with Category Filtering** (Recommended):
```bash
export MCP_TOOL_CATEGORIES="cleanup,cost,security"
python -m aws_finops_mcp
```

**stdio Mode** (All Tools):
```bash
python -m aws_finops_mcp
```

**HTTP Mode with Category Filtering**:
```bash
export MCP_SERVER_MODE=http
export MCP_SERVER_HOST=0.0.0.0
export MCP_SERVER_PORT=8000
export MCP_TOOL_CATEGORIES="cost,capacity"
python -m aws_finops_mcp
```

**Docker HTTP Mode with Filtering**:
```bash
docker run -e MCP_SERVER_MODE=http \
  -e MCP_SERVER_PORT=8000 \
  -e MCP_TOOL_CATEGORIES="cleanup,cost" \
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
| **[AGENTCORE_QUICKSTART.md](AGENTCORE_QUICKSTART.md)** | 🆕 Deploy to Amazon Bedrock AgentCore in 5 minutes |
| **[BEDROCK_AGENTCORE_DEPLOYMENT.md](BEDROCK_AGENTCORE_DEPLOYMENT.md)** | 🆕 Complete AgentCore deployment guide |
| **[AGENTCORE_COMPARISON.md](AGENTCORE_COMPARISON.md)** | 🆕 Compare Gateway vs Runtime deployment |
| **[GETTING_STARTED.md](GETTING_STARTED.md)** | Complete setup guide with MCP configuration |
| **[TOOL_CATEGORIES.md](TOOL_CATEGORIES.md)** | Category filtering guide |
| **[CATEGORY_QUICK_REFERENCE.md](CATEGORY_QUICK_REFERENCE.md)** | Quick reference for categories |
| **[TOOLS_REFERENCE.md](TOOLS_REFERENCE.md)** | All 76 tools documentation |
| **[DEPLOYMENT.md](DEPLOYMENT.md)** | Deployment options (EC2, ECS, Lambda, K8s) |
| **[REMOTE_ACCESS_GUIDE.md](REMOTE_ACCESS_GUIDE.md)** | HTTP mode and remote access setup |
| **[IAM_SETUP_GUIDE.md](IAM_SETUP_GUIDE.md)** | IAM permissions and policies |
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | System architecture and design |
| **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** | Migration guide for category filtering |
| **[iam-policies/README.md](iam-policies/README.md)** | IAM policy templates |
