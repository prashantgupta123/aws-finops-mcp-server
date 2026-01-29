# AWS FinOps MCP Server - AgentCore Architecture

Visual guide to understanding the deployment architectures on Amazon Bedrock AgentCore.

## Overview

Amazon Bedrock AgentCore provides two deployment patterns for MCP servers:
1. **Gateway Pattern** - Lambda-based, serverless
2. **Runtime Pattern** - Container-based, always-on

---

## Gateway Architecture (Lambda-based)

### High-Level Architecture

```
┌─────────────────┐
│   AI Assistant  │
│  (Kiro/Cursor)  │
└────────┬────────┘
         │ MCP Protocol
         │ (HTTPS)
         ▼
┌─────────────────────────────────────────────────┐
│         Amazon Bedrock AgentCore                │
│                                                 │
│  ┌───────────────────────────────────────────┐  │
│  │          AgentCore Gateway                │  │
│  │                                           │  │
│  │  • Tool Discovery                         │  │
│  │  • Request Routing                        │  │
│  │  • Authentication (OAuth/IAM)             │  │
│  │  • Protocol Translation                   │  │
│  └──────────────┬────────────────────────────┘  │
│                 │                               │
└─────────────────┼───────────────────────────────┘
                  │ Invoke
                  ▼
         ┌────────────────┐
         │  AWS Lambda    │
         │                │
         │  FinOps MCP    │
         │  Server Code   │
         │                │
         │  • 76 Tools    │
         │  • Categories  │
         │  • Filtering   │
         └────────┬───────┘
                  │ AWS SDK
                  ▼
    ┌─────────────────────────────┐
    │       AWS Services          │
    │                             │
    │  • EC2  • Lambda  • S3      │
    │  • RDS  • EBS     • Cost    │
    │  • CloudWatch     • IAM     │
    └─────────────────────────────┘
```

### Detailed Flow

```
1. Request Flow
   ┌──────────┐
   │ AI Agent │
   └────┬─────┘
        │ 1. MCP Request
        │    (tools/list or tools/call)
        ▼
   ┌─────────────────┐
   │ AgentCore       │
   │ Gateway         │
   │                 │
   │ • Validates     │
   │ • Authenticates │
   │ • Routes        │
   └────┬────────────┘
        │ 2. Lambda Invoke
        │    (Event payload)
        ▼
   ┌─────────────────┐
   │ Lambda Function │
   │                 │
   │ • Parse request │
   │ • Execute tool  │
   │ • Return result │
   └────┬────────────┘
        │ 3. AWS API Calls
        ▼
   ┌─────────────────┐
   │ AWS Services    │
   └─────────────────┘

2. Response Flow
   ┌─────────────────┐
   │ AWS Services    │
   └────┬────────────┘
        │ 4. API Response
        ▼
   ┌─────────────────┐
   │ Lambda Function │
   │                 │
   │ • Format result │
   │ • Add metadata  │
   └────┬────────────┘
        │ 5. Lambda Response
        ▼
   ┌─────────────────┐
   │ AgentCore       │
   │ Gateway         │
   │                 │
   │ • Validates     │
   │ • Formats       │
   └────┬────────────┘
        │ 6. MCP Response
        ▼
   ┌──────────┐
   │ AI Agent │
   └──────────┘
```

### Component Details

```
┌─────────────────────────────────────────────────────┐
│              AgentCore Gateway                      │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────────────────────────────────────┐   │
│  │  Inbound Authorization                       │   │
│  │  • OAuth 2.0 (Cognito)                       │   │
│  │  • API Keys                                  │   │
│  │  • IAM SigV4                                 │   │
│  └──────────────────────────────────────────────┘   │
│                                                     │
│  ┌──────────────────────────────────────────────┐   │
│  │  Tool Discovery & Routing                    │   │
│  │  • Semantic search                           │   │
│  │  • Tool catalog                              │   │
│  │  • Request routing                           │   │
│  └──────────────────────────────────────────────┘   │
│                                                     │
│  ┌──────────────────────────────────────────────┐   │
│  │  Protocol Translation                        │   │
│  │  • MCP → Lambda Event                        │   │
│  │  • Lambda Response → MCP                     │   │
│  └──────────────────────────────────────────────┘   │
│                                                     │
│  ┌──────────────────────────────────────────────┐   │
│  │  Monitoring & Logging                        │   │
│  │  • CloudWatch Metrics                        │   │
│  │  • CloudTrail Audit                          │   │
│  └──────────────────────────────────────────────┘   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## Runtime Architecture (Container-based)

### High-Level Architecture

```
┌─────────────────┐
│   AI Assistant  │
│  (Kiro/Cursor)  │
└────────┬────────┘
         │ MCP Protocol
         │ (HTTPS)
         ▼
┌─────────────────────────────────────────────────┐
│         Amazon Bedrock AgentCore                │
│                                                 │
│  ┌───────────────────────────────────────────┐  │
│  │          AgentCore Runtime                │  │
│  │                                           │  │
│  │  • Container Orchestration                │  │
│  │  • Session Management                     │  │
│  │  • Authentication (OAuth/IAM)             │  │
│  │  • Load Balancing                         │  │
│  └──────────────┬────────────────────────────┘  │
│                 │                               │
└─────────────────┼───────────────────────────────┘
                  │ HTTP
                  ▼
    ┌──────────────────────────────┐
    │    Docker Container          │
    │    (ARM64, Always-On)        │
    │                              │
    │  ┌────────────────────────┐  │
    │  │  HTTP Server           │  │
    │  │  (0.0.0.0:8000/mcp)    │  │
    │  │                        │  │
    │  │  • MCP Protocol        │  │
    │  │  • Session State       │  │
    │  │  • Connection Pool     │  │
    │  └───────────┬────────────┘  │
    │              │               │
    │  ┌───────────▼────────────┐  │
    │  │  FinOps MCP Server     │  │
    │  │                        │  │
    │  │  • 76 Tools            │  │
    │  │  • Categories          │  │
    │  │  • Filtering           │  │
    │  │  • State Management    │  │
    │  └───────────┬────────────┘  │
    │              │               │
    └──────────────┼───────────────┘
                   │ AWS SDK
                   ▼
      ┌─────────────────────────────┐
      │       AWS Services          │
      │                             │
      │  • EC2  • Lambda  • S3      │
      │  • RDS  • EBS     • Cost    │
      │  • CloudWatch     • IAM     │
      └─────────────────────────────┘
```

### Detailed Flow

```
1. Request Flow (Stateful)
   ┌──────────┐
   │ AI Agent │
   └────┬─────┘
        │ 1. MCP Request
        │    + Mcp-Session-Id header
        ▼
   ┌─────────────────┐
   │ AgentCore       │
   │ Runtime         │
   │                 │
   │ • Session mgmt  │
   │ • Auth check    │
   │ • Route to      │
   │   container     │
   └────┬────────────┘
        │ 2. HTTP POST /mcp
        │    + Session header
        ▼
   ┌─────────────────┐
   │ Docker          │
   │ Container       │
   │                 │
   │ • HTTP Server   │
   │ • Session state │
   │ • Tool exec     │
   └────┬────────────┘
        │ 3. AWS API Calls
        ▼
   ┌─────────────────┐
   │ AWS Services    │
   └─────────────────┘

2. Session Management
   ┌──────────────────────────────┐
   │  AgentCore Runtime           │
   │                              │
   │  Session 1 ──┐               │
   │              │               │
   │  Session 2 ──┼──► Container  │
   │              │               │
   │  Session 3 ──┘               │
   │                              │
   │  • Isolates sessions         │
   │  • Maintains state           │
   │  • Routes by session ID      │
   └──────────────────────────────┘
```

### Container Details

```
┌────────────────────────────────────────────────────┐
│           Docker Container (ARM64)                 │
├────────────────────────────────────────────────────┤
│                                                    │
│  ┌──────────────────────────────────────────────┐  │
│  │  HTTP Server Layer                           │  │
│  │  • Host: 0.0.0.0                             │  │
│  │  • Port: 8000                                │  │
│  │  • Endpoint: /mcp                            │  │
│  │  • Protocol: HTTP/1.1                        │  │
│  └──────────────────────────────────────────────┘  │
│                                                    │
│  ┌──────────────────────────────────────────────┐  │
│  │  MCP Protocol Handler                        │  │
│  │  • JSON-RPC 2.0                              │  │
│  │  • tools/list                                │  │
│  │  • tools/call                                │  │
│  │  • Session management                        │  │
│  └──────────────────────────────────────────────┘  │
│                                                    │
│  ┌──────────────────────────────────────────────┐  │
│  │  Application Layer                           │  │
│  │  • FastMCP Server                            │  │
│  │  • Tool Registry                             │  │
│  │  • Category Filtering                        │  │
│  │  • AWS Session Management                    │  │
│  └──────────────────────────────────────────────┘  │
│                                                    │
│  ┌──────────────────────────────────────────────┐  │
│  │  State Management                            │  │
│  │  • Connection pooling                        │  │
│  │  • Cache management                          │  │
│  │  • Session data                              │  │
│  └──────────────────────────────────────────────┘  │
│                                                    │
└────────────────────────────────────────────────────┘
```

---

## Authentication Flow

### OAuth 2.0 with Cognito

```
┌──────────┐                   ┌─────────────┐
│ AI Agent │                   │   Cognito   │
└────┬─────┘                   │  User Pool  │
     │                         └──────┬──────┘
     │ 1. Request without token       │
     ▼                                │
┌─────────────┐                       │
│  AgentCore  │                       │
│  Gateway/   │                       │
│  Runtime    │                       │
└────┬────────┘                       │
     │ 2. 401 Unauthorized            │
     │    + WWW-Authenticate header   │
     ▼                                │
┌──────────┐                          │
│ AI Agent │                          │
└────┬─────┘                          │
     │ 3. Redirect to auth            │
     ├────────────────────────────────►
     │                                │
     │ 4. User authenticates          │
     │                                │
     │ 5. Return access token         │
     ◄────────────────────────────────┤
     │                                │
     │ 6. Request with token          │
     ▼                                │
┌─────────────┐                       │
│  AgentCore  │                       │
│  Gateway/   │ 7. Validate token     │
│  Runtime    ├───────────────────────►
└────┬────────┘                       │
     │ 8. Token valid                 │
     ◄────────────────────────────────┤
     │                                │
     │ 9. Process request             │
     ▼                                │
```

### IAM Role-based (Lambda)

```
┌──────────┐
│ AI Agent │
└────┬─────┘
     │ 1. Request
     ▼
┌─────────────┐
│  AgentCore  │
│  Gateway    │
└────┬────────┘
     │ 2. Invoke Lambda
     ▼
┌─────────────┐
│   Lambda    │
│             │
│  Execution  │
│  Role       │ ──► Assumes role
│             │     with permissions
└────┬────────┘
     │ 3. AWS API calls
     │    using role credentials
     ▼
┌─────────────┐
│ AWS Services│
└─────────────┘
```

---

## Data Flow Comparison

### Gateway (Lambda) - Stateless

```
Request 1:
AI Agent → Gateway → Lambda (Cold Start) → AWS → Response
         ↑                                         ↓
         └─────────────────────────────────────────┘
         
Request 2:
AI Agent → Gateway → Lambda (Warm) → AWS → Response
         ↑                                  ↓
         └──────────────────────────────────┘

Request 3 (after idle):
AI Agent → Gateway → Lambda (Cold Start) → AWS → Response
         ↑                                         ↓
         └─────────────────────────────────────────┘

• Each request is independent
• No state between requests
• Cold starts possible
• Scales automatically
```

### Runtime (Container) - Stateful

```
Session 1:
AI Agent → Runtime → Container (Always Warm) → AWS → Response
         ↑          ↓                                  ↓
         │          State maintained                   │
         └─────────────────────────────────────────────┘

Session 1 (continued):
AI Agent → Runtime → Container (Same Session) → AWS → Response
         ↑          ↓                                   ↓
         │          Uses cached state                   │
         └──────────────────────────────────────────────┘

Session 2 (parallel):
AI Agent → Runtime → Container (Different Session) → AWS → Response
         ↑          ↓                                      ↓
         │          Isolated state                         │
         └─────────────────────────────────────────────────┘

• Container always running
• State maintained per session
• No cold starts
• Connection pooling
```

---

## Scaling Patterns

### Gateway (Lambda) Scaling

```
Low Load:
┌─────────┐
│ Gateway │ ──► Lambda Instance 1
└─────────┘

Medium Load:
┌─────────┐     ┌─► Lambda Instance 1
│ Gateway │ ────┼─► Lambda Instance 2
└─────────┘     └─► Lambda Instance 3

High Load:
┌─────────┐     ┌─► Lambda Instance 1
│ Gateway │ ────┼─► Lambda Instance 2
└─────────┘     ├─► Lambda Instance 3
                ├─► Lambda Instance 4
                └─► ... (up to 1000)

• Automatic scaling
• No configuration needed
• Pay per invocation
```

### Runtime (Container) Scaling

```
Single Container:
┌─────────┐
│ Runtime │ ──► Container 1 (Always On)
└─────────┘

Multi-Container (Optional):
┌─────────┐     ┌─► Container 1
│ Runtime │ ────┼─► Container 2
└─────────┘     └─► Container 3

Multi-Region:
┌──────────────┐     ┌─► us-east-1: Container
│ Load Balancer│ ────┼─► us-west-2: Container
└──────────────┘     └─► eu-west-1: Container

• Manual scaling configuration
• Always-on containers
• Pay for running time
```

---

## Cost Architecture

### Gateway (Lambda) Cost Components

```
┌─────────────────────────────────────┐
│         Total Cost                  │
├─────────────────────────────────────┤
│                                     │
│  ┌───────────────────────────────┐  │
│  │  AgentCore Gateway            │  │
│  │  $0.001 per tool invocation   │  │
│  └───────────────────────────────┘  │
│              +                      │
│  ┌───────────────────────────────┐  │
│  │  Lambda Compute               │  │
│  │  $0.0000166667 per GB-second  │  │
│  └───────────────────────────────┘  │
│              +                      │
│  ┌───────────────────────────────┐  │
│  │  Lambda Requests              │  │
│  │  $0.20 per 1M requests        │  │
│  └───────────────────────────────┘  │
│                                     │
└─────────────────────────────────────┘

Example: 10,000 invocations/month
• Gateway: 10,000 × $0.001 = $10.00
• Compute: 10,000 × 2s × 0.5GB × $0.0000166667 = $0.17
• Requests: 10,000 × $0.20/1M = $0.002
• Total: ~$10.17/month
```

### Runtime (Container) Cost Components

```
┌─────────────────────────────────────┐
│         Total Cost                  │
├─────────────────────────────────────┤
│                                     │
│  ┌───────────────────────────────┐  │
│  │  AgentCore Runtime            │  │
│  │  $0.10 per container-hour     │  │
│  │  730 hours/month              │  │
│  └───────────────────────────────┘  │
│              +                      │
│  ┌───────────────────────────────┐  │
│  │  Tool Invocations             │  │
│  │  $0.001 per invocation        │  │
│  └───────────────────────────────┘  │
│                                     │
└─────────────────────────────────────┘

Example: 10,000 invocations/month
• Runtime: 730 × $0.10 = $73.00
• Invocations: 10,000 × $0.001 = $10.00
• Total: ~$83.00/month

Note: More cost-effective at higher volumes
```

---

## Monitoring Architecture

### CloudWatch Integration

```
┌─────────────────────────────────────────────────┐
│              CloudWatch                         │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌───────────────────────────────────────────┐  │
│  │  Metrics                                  │  │
│  │  • Gateway invocations                    │  │
│  │  • Lambda duration                        │  │
│  │  • Container CPU/Memory                   │  │
│  │  • Error rates                            │  │
│  │  • Latency                                │  │
│  └───────────────────────────────────────────┘  │
│                                                 │
│  ┌───────────────────────────────────────────┐  │
│  │  Logs                                     │  │
│  │  • /aws/lambda/aws-finops-mcp-server      │  │
│  │  • /aws/bedrock-agentcore/gateway/...     │  │
│  │  • /aws/bedrock-agentcore/runtime/...     │  │
│  └───────────────────────────────────────────┘  │
│                                                 │
│  ┌───────────────────────────────────────────┐  │
│  │  Alarms                                   │  │
│  │  • High error rate                        │  │
│  │  • High latency                           │  │
│  │  • Cost threshold                         │  │
│  └───────────────────────────────────────────┘  │
│                                                 │
└─────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  CloudTrail     │
│  • API calls    │
│  • Audit logs   │
└─────────────────┘
```

---

## Summary

### Gateway Architecture
- **Pattern**: Serverless, event-driven
- **Best for**: Variable workloads, cost optimization
- **Scaling**: Automatic, unlimited
- **State**: Stateless
- **Cost**: Pay-per-use

### Runtime Architecture
- **Pattern**: Container-based, always-on
- **Best for**: Consistent workloads, complex operations
- **Scaling**: Configurable
- **State**: Stateful
- **Cost**: Fixed + per-use

Both architectures provide:
- ✅ Full MCP protocol support
- ✅ OAuth/IAM authentication
- ✅ CloudWatch monitoring
- ✅ High availability
- ✅ Automatic scaling
- ✅ Security best practices

Choose based on your specific requirements for cost, performance, and operational complexity.
