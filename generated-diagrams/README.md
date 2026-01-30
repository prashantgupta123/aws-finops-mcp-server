# Architecture Diagrams

This folder contains visual architecture diagrams for the AWS FinOps MCP Server project.

## 📊 Available Diagrams

### 1. System Architecture (5 Layouts)

**Complete Architecture** ⭐ **RECOMMENDED** - `aws-finops-mcp-architecture-complete.png`  
Best for: Comprehensive documentation, executive presentations, architecture reviews

Features:
- AWS Cloud and Region boundaries clearly marked
- Amazon Bedrock AgentCore service highlighted
- Complete observability stack (CloudWatch Logs, Metrics, Alarms, Insights, X-Ray)
- All 76 tools with emoji indicators (💰🧹🔒⚡📊🔄🌐💾📦💬🗄️📈🏛️)
- 30+ AWS services across 5 categories
- DevOps pipeline (CodeBuild, CodePipeline, ECR)
- Security services (IAM, Secrets Manager)
- Color-coded service groups for easy identification

**Enhanced Architecture** - `aws-finops-mcp-architecture-enhanced.png`  
Best for: General presentations, team discussions, documentation

Features:
- AWS Cloud and Region boundaries
- Bedrock AgentCore integration
- CloudWatch Observability suite
- Essential AWS services
- Cleaner, balanced view

**Horizontal Layout** - `aws-finops-mcp-architecture-horizontal.png`  
Best for: Presentations, wide screens, documentation

**Wide Layout** - `aws-finops-mcp-architecture-wide.png`  
Best for: Compact view, quick reference, dashboards

**Vertical Layout** - `aws-finops-mcp-architecture-vertical.png`  
Best for: Detailed view, mobile devices, reports

---

### 2. Deployment Flow
**File**: `agentcore-deployment-flow.png`

Illustrates the deployment process:
- Local development (source code, Dockerfile, config)
- AgentCore CLI command (`agentcore launch`)
- AWS CodeBuild (ARM64 container build)
- Amazon ECR (container registry)
- IAM role creation (automatic)
- AgentCore Runtime deployment
- Monitoring setup (CloudWatch)
- Agent endpoint creation

**Use this diagram to**: Understand how to deploy the MCP server to AWS.

---

### 3. Tool Execution Flow
**File**: `mcp-tool-execution-flow.png`

Details the request/response flow:
- Client request (JSON-RPC 2.0)
- HTTP server processing
- Session management and authentication
- Tool routing and category filtering
- AWS SDK (boto3) interactions
- AWS service API calls
- Response formatting and delivery

**Use this diagram to**: Understand how MCP tools execute and interact with AWS services.

---

## 🎨 Diagram Generation

These diagrams were generated using the [AWS Diagram MCP Server](https://github.com/awslabs/aws-diagram-mcp-server) with the Python `diagrams` library.

### Regenerate Diagrams

To regenerate these diagrams, you need:

1. Install the diagrams package:
   ```bash
   pip install diagrams
   ```

2. Install Graphviz:
   ```bash
   # macOS
   brew install graphviz
   
   # Ubuntu/Debian
   sudo apt-get install graphviz
   
   # Windows
   choco install graphviz
   ```

3. Use the AWS Diagram MCP Server to generate diagrams from the code in `ARCHITECTURE_DIAGRAMS.md`

---

## 📖 Documentation

For detailed explanations of each diagram, see:
- **[ARCHITECTURE_DIAGRAMS.md](../ARCHITECTURE_DIAGRAMS.md)** - Complete architecture documentation with diagram descriptions

---

## 🔄 Updates

**Last Generated**: January 30, 2026  
**Tool Used**: AWS Diagram MCP Server  
**Format**: PNG (Portable Network Graphics)

---

## 📝 Notes

- All diagrams use AWS official icons
- Diagrams follow left-to-right (LR) or top-to-bottom (TB) flow
- Color coding and clustering used for logical grouping
- Edge labels indicate data flow and relationships
