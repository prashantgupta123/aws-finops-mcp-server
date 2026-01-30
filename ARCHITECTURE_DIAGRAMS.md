# AWS FinOps MCP Server - Architecture Diagrams

This document provides visual architecture diagrams for the AWS FinOps MCP Server project.

## 📊 Diagram Overview

1. **System Architecture** - Overall system components and interactions
2. **Deployment Flow** - AgentCore deployment process
3. **Tool Execution Flow** - How MCP tools execute and interact with AWS

---

## 1. System Architecture

The system architecture is available in multiple formats for different viewing preferences:

### Complete Architecture (Recommended) ⭐
![AWS FinOps MCP Server - Complete Architecture](./generated-diagrams/aws-finops-mcp-architecture-complete.png)

**Features**:
- AWS Cloud and Region boundaries clearly marked
- Amazon Bedrock AgentCore highlighted
- Complete observability stack (CloudWatch Logs, Metrics, X-Ray, Insights)
- All 76 tools organized by category with emojis
- DevOps services (CodeBuild, CodePipeline, ECR)
- Security services (IAM, Secrets Manager)
- Comprehensive AWS service coverage (30+ services)
- Color-coded service groups for easy identification

### Enhanced Architecture
![AWS FinOps MCP Server - Enhanced Architecture](./generated-diagrams/aws-finops-mcp-architecture-enhanced.png)

**Features**:
- AWS Cloud and Region boundaries
- Bedrock AgentCore service integration
- CloudWatch Observability suite
- Cost & Governance services
- Simplified view with essential services

### Horizontal Layout (Presentation-Ready)
![AWS FinOps MCP Server Architecture - Horizontal](./generated-diagrams/aws-finops-mcp-architecture-horizontal.png)

### Wide Layout (Compact View)
![AWS FinOps MCP Server Architecture - Wide](./generated-diagrams/aws-finops-mcp-architecture-wide.png)

### Vertical Layout (Detailed View)
![AWS FinOps MCP Server Architecture - Vertical](./generated-diagrams/aws-finops-mcp-architecture-vertical.png)

### Components

#### **Client Layer** (Outside AWS Cloud)
- **Developers/AI Agents**: End users including human developers and AI assistants
- **MCP Clients**: Applications that communicate with the MCP server
  - Claude (Anthropic)
  - Cline (VS Code extension)
  - Cursor (AI-powered IDE)
  - Other MCP-compatible clients

#### **AWS Cloud → Region: us-east-1**

##### **Amazon Bedrock AgentCore** (Purple Section)
- **Bedrock AgentCore Service**: Managed service for hosting AI agents
- **API Gateway**: HTTPS endpoint with JSON-RPC 2.0 protocol
- **Fargate Runtime**: Serverless container runtime (ARM64)
- **MCP Server Container**: 
  - HTTP Server (Port 8000)
  - Session Manager for stateful interactions
  - 76 tools organized into 14 categories with emoji indicators:
    - 💰 Cost Tools (16) & 🧹 Cleanup Tools (9)
    - 🔒 Security Tools (5) & ⚡ Performance Tools (5)
    - 📊 Capacity Tools (9) & 🔄 Upgrade Tools (8)
    - 🌐 Network (5), 💾 Storage (2), 📦 Containers (4)
    - 💬 Messaging (3), 🗄️ Database (2), 📈 Monitoring (3), 🏛️ Governance (3)

##### **DevOps & Container Services** (Blue Section)
- **AWS CodeBuild**: ARM64 container image builder
- **AWS CodePipeline**: Optional CI/CD automation
- **Amazon ECR**: Container image registry and storage
- **IAM Roles**: 
  - Execution Role (runtime permissions)
  - CodeBuild Role (build permissions)
- **AWS Secrets Manager**: Secure credential storage

##### **Observability & Monitoring** (Orange Section)
- **CloudWatch Logs**: Application logs and agent invocation logs
- **CloudWatch Metrics**: Performance metrics and resource utilization
- **CloudWatch Alarms**: Error alerts and threshold monitoring
- **CloudWatch Insights**: Log analytics and query capabilities
- **AWS X-Ray**: Distributed tracing and performance analysis
- **Amazon EventBridge**: Event routing and automation
- **Amazon SNS**: Notification delivery

##### **Target AWS Services** (Analysis Targets)

**Compute & Container Services** (Red Section):
- Amazon EC2 (Instances)
- AWS Lambda (Functions)
- Amazon ECS (Clusters)
- Amazon EKS (Kubernetes)
- AWS Batch (Jobs)

**Storage Services** (Teal Section):
- Amazon S3 (Buckets)
- Amazon EBS (Volumes)
- Amazon EFS (File Systems)
- Amazon FSx (File Systems)
- AWS Backup (Backup Vaults)

**Database Services** (Light Green Section):
- Amazon RDS (Databases)
- Amazon Aurora (Clusters)
- Amazon DynamoDB (Tables)
- Amazon ElastiCache (Clusters)
- Amazon Neptune (Graph DB)

**Network & Content Delivery** (Indigo Section):
- Amazon VPC (Networks)
- Elastic Load Balancing
- Amazon Route 53 (DNS)
- Amazon CloudFront (CDN)
- API Gateway (APIs)

**Cost Management & Governance** (Yellow Section):
- AWS Cost Explorer (Cost Analysis)
- AWS Budgets (Cost Alerts)
- AWS Trusted Advisor (Best Practices)
- AWS Config (Compliance)
- AWS CloudTrail (Audit Logs)

### Data Flow

1. User/AI Agent sends request to MCP Client
2. MCP Client communicates with HTTP Server via JSON-RPC 2.0
3. HTTP Server routes request to appropriate tool category
4. Tools execute AWS API calls to analyze resources
5. Results are formatted and returned to the client
6. All activity is logged to CloudWatch

---

## 2. AgentCore Deployment Flow

![AgentCore Deployment Flow](./generated-diagrams/agentcore-deployment-flow.png)

### Deployment Steps

#### **1. Local Development**
- **Source Code**: Python-based MCP server implementation
- **Dockerfile.agentcore**: ARM64 container configuration
- **.bedrock_agentcore.yaml**: AgentCore deployment configuration

#### **2. Deployment Command**
```bash
agentcore launch
```

#### **3. AWS CodeBuild**
- Automatically triggered by AgentCore CLI
- Builds ARM64 container image
- No local Docker required
- Build logs sent to CloudWatch

#### **4. Amazon ECR**
- Container image pushed to ECR repository
- Repository: `aws-finops-mcp-server`
- Automatic image tagging with timestamps

#### **5. IAM Roles (Auto-created)**
- **Execution Role**: Runtime permissions for the container
- **CodeBuild Role**: Build and push permissions

#### **6. AgentCore Runtime**
- Serverless container runtime (Fargate-based)
- Pulls image from ECR
- Runs container on port 8000
- Health checks via `/health` endpoint

#### **7. Monitoring**
- CloudWatch Logs: Application logs
- CloudWatch Metrics: Performance metrics

#### **8. Agent Endpoint**
- HTTPS endpoint for MCP clients
- Secure communication
- Session management

### Deployment Timeline

- **Build Phase**: 2-5 minutes (CodeBuild)
- **Deploy Phase**: 3-5 minutes (AgentCore setup)
- **Validation Phase**: 1-2 minutes (Health checks)
- **Total**: 6-12 minutes

---

## 3. MCP Tool Execution Flow

![MCP Tool Execution Flow](./generated-diagrams/mcp-tool-execution-flow.png)

### Execution Steps

#### **1. Client Request**
- AI Agent or Developer initiates request
- MCP Client formats JSON-RPC request
- Request includes method and parameters

Example request:
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "find_unused_ec2_instances",
    "arguments": {
      "region": "us-east-1"
    }
  },
  "id": 1
}
```

#### **2. HTTP Server Processing**
- Receives request on port 8000
- **Session Manager**: Tracks session via `Mcp-Session-Id` header
- **OAuth Auth** (Optional): Validates authentication
- Routes to appropriate tool

#### **3. Tool Router**
- Applies category filtering (if configured)
- Selects appropriate tool based on request
- Validates parameters

#### **4. Tool Execution**
Tools are organized by category:
- **Cleanup Tools**: `find_unused_*`
- **Cost Tools**: `get_cost_*`, `analyze_*`
- **Security Tools**: `find_unencrypted_*`, `find_public_*`

#### **5. AWS SDK (boto3)**
- Tools use boto3 to interact with AWS
- IAM credentials from execution role
- Automatic credential management

#### **6. AWS Service APIs**
Tools call various AWS APIs:
- **EC2 API**: `DescribeInstances`, `DescribeVolumes`
- **S3 API**: `ListBuckets`, `GetBucketEncryption`
- **Cost Explorer API**: `GetCostAndUsage`, `GetCostForecast`
- **CloudWatch API**: `GetMetricStatistics`, `DescribeAlarms`

#### **7. Response Processing**
- Raw AWS API responses collected
- Data aggregated and analyzed
- Results formatted (JSON or Markdown)
- Response sent back through HTTP server

Example response:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Found 5 unused EC2 instances:\n- i-1234567890abcdef0 (t2.micro)\n- i-0987654321fedcba0 (t3.small)\n..."
      }
    ]
  },
  "id": 1
}
```

#### **8. Client Response**
- MCP Client receives formatted response
- Displays results to user
- User can take action based on findings

---

## 🔒 Security Architecture

### Authentication & Authorization

1. **IAM Execution Role**
   - Attached to AgentCore Runtime
   - Grants permissions to AWS services
   - Follows least-privilege principle

2. **OAuth Authentication** (Optional)
   - Cognito-based authentication
   - Bearer token validation
   - 401 + WWW-Authenticate header

3. **Session Management**
   - `Mcp-Session-Id` header tracking
   - Stateful session storage
   - Session isolation

### Network Security

1. **HTTPS Only**
   - All communication encrypted
   - TLS 1.2+ required

2. **VPC Integration** (Optional)
   - Private subnet deployment
   - Security group restrictions
   - No public internet access

3. **API Gateway**
   - Rate limiting
   - Request validation
   - DDoS protection

---

## 📊 Performance Characteristics

### Scalability

- **Serverless**: Auto-scales based on demand
- **Concurrent Requests**: Handles multiple simultaneous requests
- **Cold Start**: ~2-3 seconds for first request
- **Warm Requests**: <100ms response time

### Resource Usage

- **Memory**: 512MB - 2GB (configurable)
- **CPU**: ARM64 (Graviton2)
- **Storage**: Ephemeral (container-based)

### Optimization

1. **Category Filtering**
   - Load only needed tools
   - 67-89% reduction in tool count
   - Faster initialization

2. **Connection Pooling**
   - Reuse boto3 clients
   - Reduce API call overhead

3. **Caching** (Future)
   - Cache AWS API responses
   - Reduce redundant calls

---

## 🔄 Data Flow Summary

```
User Request
    ↓
MCP Client (JSON-RPC)
    ↓
AgentCore Runtime (HTTPS)
    ↓
HTTP Server (Port 8000)
    ↓
Session Manager + Auth
    ↓
Tool Router (Category Filter)
    ↓
Tool Execution (Python)
    ↓
AWS SDK (boto3)
    ↓
AWS Service APIs
    ↓
Response Processing
    ↓
Formatted Output
    ↓
MCP Client
    ↓
User
```

---

## 📈 Monitoring & Observability

### CloudWatch Logs

- **Application Logs**: Tool execution, errors, warnings
- **Access Logs**: HTTP requests and responses
- **Build Logs**: CodeBuild deployment logs

### CloudWatch Metrics

- **Invocations**: Number of tool calls
- **Duration**: Execution time per tool
- **Errors**: Failed requests and exceptions
- **Throttles**: Rate limiting events

### Health Checks

- **Endpoint**: `/health`
- **Interval**: 30 seconds
- **Timeout**: 10 seconds
- **Retries**: 3 attempts

---

## 🎯 Architecture Benefits

### 1. Serverless & Scalable
- No infrastructure management
- Auto-scaling based on demand
- Pay only for usage

### 2. Secure by Default
- IAM-based permissions
- Encrypted communication
- Session isolation

### 3. Easy Deployment
- One-command deployment
- Automatic resource creation
- Built-in monitoring

### 4. Flexible & Extensible
- Category-based filtering
- Easy to add new tools
- Framework-agnostic

### 5. Cost-Effective
- Serverless pricing model
- Efficient resource usage
- Cost optimization tools included

---

## 📚 Related Documentation

- **[README.md](README.md)** - Project overview
- **[AGENTCORE_DEPLOYMENT_FINAL.md](AGENTCORE_DEPLOYMENT_FINAL.md)** - Deployment guide
- **[TOOL_CATEGORIES.md](TOOL_CATEGORIES.md)** - Tool categories
- **[IAM_SETUP_GUIDE.md](IAM_SETUP_GUIDE.md)** - IAM configuration

---

**Generated**: January 30, 2026  
**Diagrams**: Created using AWS Diagram MCP Server
