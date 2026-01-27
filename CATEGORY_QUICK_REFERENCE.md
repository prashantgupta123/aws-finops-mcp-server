# Tool Categories - Quick Reference

## Quick Commands

```bash
# Cost optimization focus
export MCP_TOOL_CATEGORIES="cost,cleanup"

# Security audit
export MCP_TOOL_CATEGORIES="security,governance"

# Performance tuning
export MCP_TOOL_CATEGORIES="performance,capacity"

# Infrastructure cleanup
export MCP_TOOL_CATEGORIES="cleanup,network,storage,containers"

# All tools (default)
export MCP_TOOL_CATEGORIES="all"
```

## Category Cheat Sheet

| Category | Tools | Best For |
|----------|-------|----------|
| **cleanup** | 9 | Finding unused resources to delete |
| **cost** | 16 | Cost analysis and optimization |
| **capacity** | 9 | Right-sizing over/under-utilized resources |
| **security** | 5 | Security compliance and encryption |
| **performance** | 5 | Performance analysis and tuning |
| **upgrade** | 8 | Finding outdated resources |
| **network** | 5 | Network resource optimization |
| **storage** | 2 | Storage optimization |
| **containers** | 4 | ECS/ECR/EKS management |
| **database** | 2 | Database optimization |
| **messaging** | 3 | SQS/SNS/EventBridge cleanup |
| **monitoring** | 3 | CloudWatch resource cleanup |
| **application** | 2 | Application health monitoring |
| **governance** | 3 | Tagging and compliance |

## Common Use Cases

### Monthly Cost Review
```bash
MCP_TOOL_CATEGORIES="cost,cleanup,capacity"
# 34 tools: Cost analysis + unused resources + right-sizing
```

### Security Audit
```bash
MCP_TOOL_CATEGORIES="security,governance"
# 8 tools: Encryption checks + tagging compliance
```

### Performance Optimization
```bash
MCP_TOOL_CATEGORIES="performance,capacity,application"
# 16 tools: Performance metrics + utilization + health
```

### Quarterly Cleanup
```bash
MCP_TOOL_CATEGORIES="cleanup,network,storage,containers,messaging,monitoring"
# 26 tools: Comprehensive infrastructure cleanup
```

### Modernization Project
```bash
MCP_TOOL_CATEGORIES="upgrade,security"
# 13 tools: Outdated resources + security compliance
```

## MCP Client Configuration Examples

### Claude Desktop
`~/Library/Application Support/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "aws-finops-cost": {
      "command": "python",
      "args": ["-m", "aws_finops_mcp"],
      "env": {
        "MCP_TOOL_CATEGORIES": "cost,cleanup"
      }
    }
  }
}
```

### Cline
`.kiro/settings/mcp.json`:
```json
{
  "mcpServers": {
    "aws-finops": {
      "command": "uvx",
      "args": ["aws-finops-mcp"],
      "env": {
        "MCP_TOOL_CATEGORIES": "security,governance"
      }
    }
  }
}
```

### Multiple Configurations
You can configure multiple instances with different categories:

```json
{
  "mcpServers": {
    "aws-finops-cost": {
      "command": "python",
      "args": ["-m", "aws_finops_mcp"],
      "env": {
        "MCP_TOOL_CATEGORIES": "cost,cleanup"
      }
    },
    "aws-finops-security": {
      "command": "python",
      "args": ["-m", "aws_finops_mcp"],
      "env": {
        "MCP_TOOL_CATEGORIES": "security,governance"
      }
    }
  }
}
```

## Tool Count Impact

| Configuration | Tool Count | Reduction |
|---------------|------------|-----------|
| All tools | 76 | 0% |
| cost,cleanup | 25 | 67% |
| security,governance | 8 | 89% |
| cleanup only | 9 | 88% |
| cost only | 16 | 79% |

## Validation

Invalid categories will show an error:
```
ValueError: Invalid categories: {'typo'}. 
Valid categories are: application, capacity, cleanup, containers, 
cost, database, governance, messaging, monitoring, network, 
performance, security, storage, upgrade
```

## Documentation

- Full guide: [TOOL_CATEGORIES.md](TOOL_CATEGORIES.md)
- Tool reference: [TOOLS_REFERENCE.md](TOOLS_REFERENCE.md)
- Main README: [README.md](README.md)
