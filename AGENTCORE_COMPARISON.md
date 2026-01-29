# Amazon Bedrock AgentCore Deployment Methods Comparison

This guide helps you choose the best deployment method for your AWS FinOps MCP Server on Amazon Bedrock AgentCore.

## Quick Decision Matrix

| Your Requirement | Recommended Method |
|-----------------|-------------------|
| Quick testing/POC | **Gateway (Lambda)** |
| Production workload | **Runtime (Container)** |
| Budget conscious | **Gateway (Lambda)** |
| Long-running operations (>15 min) | **Runtime (Container)** |
| Simple tool exposure | **Gateway (Lambda)** |
| Complex workflows | **Runtime (Container)** |
| No Docker experience | **Gateway (Lambda)** |
| Need full control | **Runtime (Container)** |
| Serverless preference | **Gateway (Lambda)** |
| Stateful operations | **Runtime (Container)** |

## Detailed Comparison

### 1. Gateway Method (Lambda-based)

#### Architecture
```
AI Agent → AgentCore Gateway → Lambda Function → AWS APIs
```

#### Pros ✅

**Simplicity**
- No container management required
- Simpler deployment process
- Less infrastructure to maintain
- Faster initial setup (5 minutes)

**Cost-Effective**
- Pay only for execution time
- No idle costs
- Lambda free tier: 1M requests/month
- Typical cost: $0.20 per 1M requests

**Serverless Benefits**
- Automatic scaling
- High availability built-in
- No server management
- Managed by AWS

**Quick Updates**
- Update code without rebuilding containers
- Instant deployment
- Easy rollback

#### Cons ❌

**Limitations**
- 15-minute maximum execution time
- 10GB memory limit
- Cold start latency (100-500ms)
- Limited to Lambda runtime environment

**Not Suitable For**
- Long-running analysis (>15 min)
- Stateful operations
- Custom system dependencies
- High-frequency real-time operations

#### Best Use Cases

1. **Development & Testing**
   - Quick prototyping
   - Feature testing
   - Development environments

2. **Individual Tool Exposure**
   - Single-purpose tools
   - Quick queries
   - Periodic checks

3. **Cost-Sensitive Deployments**
   - Low-volume usage
   - Intermittent access
   - Budget constraints

4. **Simple Workflows**
   - Single-step operations
   - Quick data retrieval
   - Basic automation

#### Cost Example

**Scenario**: 10,000 tool invocations/month, 2 seconds average execution, 512MB memory

```
Lambda Costs:
- Requests: 10,000 × $0.20/1M = $0.002
- Compute: 10,000 × 2s × 512MB × $0.0000166667 = $0.17
- Total: ~$0.17/month

AgentCore Gateway:
- Tool invocations: 10,000 × $0.001 = $10.00
- Total: ~$10.17/month
```

---

### 2. Runtime Method (Containerized)

#### Architecture
```
AI Agent → AgentCore Runtime → Docker Container → AWS APIs
```

#### Pros ✅

**Full Control**
- Custom runtime environment
- Any system dependencies
- Full Python ecosystem
- Custom configurations

**No Time Limits**
- Operations can run indefinitely
- Long-running analysis
- Batch processing
- Complex workflows

**Stateful Operations**
- Maintain state between calls
- Session management
- Caching capabilities
- Connection pooling

**Production-Ready**
- Designed for scale
- Better performance
- More predictable behavior
- Enterprise features

#### Cons ❌

**Complexity**
- Requires Docker knowledge
- More complex deployment
- Container management
- Longer setup time (10 minutes)

**Cost**
- Always-running container
- Higher baseline cost
- No free tier
- Pay for idle time

**Maintenance**
- Container updates required
- Image management
- More moving parts
- Monitoring complexity

#### Best Use Cases

1. **Production Deployments**
   - Mission-critical operations
   - High-volume usage
   - Enterprise environments
   - SLA requirements

2. **Complex Workflows**
   - Multi-step analysis
   - Data processing pipelines
   - Batch operations
   - Orchestration

3. **Long-Running Operations**
   - Comprehensive audits
   - Large-scale analysis
   - Report generation
   - Data aggregation

4. **Custom Requirements**
   - Special dependencies
   - Custom libraries
   - Specific configurations
   - Advanced features

#### Cost Example

**Scenario**: Same 10,000 invocations/month, but container runs 24/7

```
AgentCore Runtime:
- Container hours: 730 hours × $0.10/hour = $73.00
- Tool invocations: 10,000 × $0.001 = $10.00
- Total: ~$83.00/month

Note: More cost-effective at higher volumes
```

---

## Feature Comparison Table

| Feature | Gateway (Lambda) | Runtime (Container) |
|---------|-----------------|-------------------|
| **Setup Time** | 5 minutes | 10 minutes |
| **Deployment Complexity** | Low | Medium |
| **Max Execution Time** | 15 minutes | Unlimited |
| **Memory Limit** | 10GB | Configurable |
| **Cold Start** | Yes (100-500ms) | No |
| **Scaling** | Automatic | Automatic |
| **Cost Model** | Pay-per-use | Always-on |
| **Minimum Cost** | ~$0 (free tier) | ~$73/month |
| **State Management** | Limited | Full |
| **Custom Dependencies** | Limited | Full |
| **Docker Required** | No | Yes |
| **Update Speed** | Instant | Rebuild required |
| **Monitoring** | CloudWatch | CloudWatch + Container |
| **Best For** | Testing, Simple | Production, Complex |

---

## Cost Analysis

### Break-Even Point

**When Gateway becomes more expensive than Runtime:**

```
Gateway Cost = Runtime Cost
(Invocations × $0.001) + (Lambda costs) = $83/month

Break-even: ~80,000 invocations/month
```

**Recommendation:**
- < 50,000 invocations/month → **Gateway**
- > 100,000 invocations/month → **Runtime**
- 50,000-100,000 → Depends on execution time and complexity

### Cost Optimization Tips

**For Gateway:**
1. Use category filtering to reduce cold starts
2. Optimize Lambda memory allocation
3. Minimize execution time
4. Use Lambda reserved concurrency for predictable workloads

**For Runtime:**
1. Right-size container resources
2. Use spot instances if available
3. Implement auto-scaling
4. Consider scheduled scaling for predictable patterns

---

## Performance Comparison

### Latency

| Metric | Gateway (Lambda) | Runtime (Container) |
|--------|-----------------|-------------------|
| Cold Start | 100-500ms | N/A |
| Warm Start | 10-50ms | 10-50ms |
| Tool Execution | Same | Same |
| Total (Cold) | 110-550ms | 10-50ms |
| Total (Warm) | 10-50ms | 10-50ms |

### Throughput

| Metric | Gateway (Lambda) | Runtime (Container) |
|--------|-----------------|-------------------|
| Concurrent Requests | 1000 (default) | Depends on container |
| Max Throughput | Very High | High |
| Scaling Speed | Instant | Fast |

---

## Migration Path

### Start with Gateway, Move to Runtime

**Phase 1: Development (Gateway)**
```bash
# Quick setup for testing
./deploy-to-agentcore.sh
# Choose option 1 (Gateway)
```

**Phase 2: Production (Runtime)**
```bash
# When ready for production
./deploy-to-agentcore.sh
# Choose option 2 (Runtime)
```

**Benefits:**
- Fast initial development
- Learn the system with lower costs
- Smooth transition to production
- No code changes required

---

## Decision Flowchart

```
Start
  │
  ├─ Need to test quickly? ──────────────────────→ Gateway
  │
  ├─ Operations > 15 minutes? ───────────────────→ Runtime
  │
  ├─ Budget < $100/month? ──────────────────────→ Gateway
  │
  ├─ Need stateful operations? ─────────────────→ Runtime
  │
  ├─ < 50,000 invocations/month? ───────────────→ Gateway
  │
  ├─ > 100,000 invocations/month? ──────────────→ Runtime
  │
  ├─ No Docker experience? ─────────────────────→ Gateway
  │
  ├─ Production workload? ──────────────────────→ Runtime
  │
  └─ Simple tools only? ────────────────────────→ Gateway
```

---

## Hybrid Approach

You can use **both methods simultaneously**:

### Use Case: Development + Production

```
Development Environment:
├─ Gateway (Lambda) for testing
└─ Fast iteration, low cost

Production Environment:
├─ Runtime (Container) for production
└─ High performance, reliability
```

### Use Case: Tool Segregation

```
Simple Tools:
├─ Gateway (Lambda)
└─ Quick queries, status checks

Complex Tools:
├─ Runtime (Container)
└─ Analysis, reports, batch operations
```

---

## Recommendations by Organization Size

### Startups / Small Teams
- **Start with**: Gateway (Lambda)
- **Reason**: Lower costs, faster setup, less maintenance
- **Migrate when**: Volume increases or need advanced features

### Medium Organizations
- **Start with**: Gateway for dev, Runtime for prod
- **Reason**: Balance cost and performance
- **Strategy**: Use both methods strategically

### Enterprise
- **Start with**: Runtime (Container)
- **Reason**: Production-ready, full control, compliance
- **Strategy**: Multiple deployments across regions

---

## Summary

### Choose Gateway (Lambda) if:
- ✅ Quick testing or POC
- ✅ Budget < $100/month
- ✅ Simple tool exposure
- ✅ < 50,000 invocations/month
- ✅ Operations < 15 minutes
- ✅ No Docker experience

### Choose Runtime (Container) if:
- ✅ Production workload
- ✅ Long-running operations
- ✅ > 100,000 invocations/month
- ✅ Need stateful operations
- ✅ Custom dependencies required
- ✅ Enterprise requirements

### Can't Decide?
**Start with Gateway**, then migrate to Runtime when needed. The transition is straightforward and requires no code changes.

---

## Next Steps

1. **Review**: [AGENTCORE_QUICKSTART.md](./AGENTCORE_QUICKSTART.md) for deployment
2. **Deploy**: Run `./deploy-to-agentcore.sh` to get started
3. **Learn**: Read [BEDROCK_AGENTCORE_DEPLOYMENT.md](./BEDROCK_AGENTCORE_DEPLOYMENT.md) for details
4. **Optimize**: Monitor usage and adjust as needed

---

**Need Help Deciding?** Consider these questions:
1. What's your monthly budget?
2. How many tool invocations do you expect?
3. Do you need operations longer than 15 minutes?
4. Is this for development or production?
5. Do you have Docker experience?

Based on your answers, the right choice will be clear! 🎯
