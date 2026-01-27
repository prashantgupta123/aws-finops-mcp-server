# Migration Guide: Category-Based Tool Filtering

## For Existing Users

### No Action Required! 

The category filtering feature is **100% backward compatible**. Your existing configuration will continue to work exactly as before.

### What Changed?

**Before**: All 76 tools were always loaded
**After**: You can optionally filter tools by category

### Default Behavior

If you don't set `MCP_TOOL_CATEGORIES`, all 76 tools are loaded (same as before).

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
✅ This still works! No changes needed.

---

## Opting In to Category Filtering

### Step 1: Choose Your Categories

Review the available categories in [TOOL_CATEGORIES.md](TOOL_CATEGORIES.md) or check the README.

### Step 2: Update Your Configuration

Add `MCP_TOOL_CATEGORIES` to your MCP client config:

```json
{
  "mcpServers": {
    "aws-finops": {
      "command": "python",
      "args": ["-m", "aws_finops_mcp"],
      "env": {
        "MCP_TOOL_CATEGORIES": "cleanup,cost"
      }
    }
  }
}
```

### Step 3: Restart Your MCP Client

Restart your MCP client (Claude Desktop, Cline, etc.) to apply changes.

### Step 4: Verify

Check that only the expected tools are loaded. For example, with `"cleanup,cost"`, you should see 25 tools instead of 76.

---

## Common Migration Scenarios

### Scenario 1: "I only use cost tools"

**Before** (76 tools):
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

**After** (16 tools):
```json
{
  "mcpServers": {
    "aws-finops": {
      "command": "python",
      "args": ["-m", "aws_finops_mcp"],
      "env": {
        "MCP_TOOL_CATEGORIES": "cost"
      }
    }
  }
}
```

**Benefit**: 79% reduction in tool count, faster loading

---

### Scenario 2: "I use cost and cleanup tools"

**After** (25 tools):
```json
{
  "mcpServers": {
    "aws-finops": {
      "command": "python",
      "args": ["-m", "aws_finops_mcp"],
      "env": {
        "MCP_TOOL_CATEGORIES": "cleanup,cost"
      }
    }
  }
}
```

**Benefit**: 67% reduction in tool count

---

### Scenario 3: "I want everything (current behavior)"

**Option 1** - Omit the variable:
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

**Option 2** - Explicitly set to "all":
```json
{
  "mcpServers": {
    "aws-finops": {
      "command": "python",
      "args": ["-m", "aws_finops_mcp"],
      "env": {
        "MCP_TOOL_CATEGORIES": "all"
      }
    }
  }
}
```

Both work identically!

---

### Scenario 4: "Different teams need different tools"

Set up multiple MCP server instances:

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

---

## Troubleshooting

### "I don't see any tools!"

Check the available categories in [TOOL_CATEGORIES.md](TOOL_CATEGORIES.md).

Valid categories: application, capacity, cleanup, containers, cost, database, governance, messaging, monitoring, network, performance, security, storage, upgrade

### "I get an error about invalid categories"

The server validates category names. Check the error message for valid options.

### "I want to go back to all tools"

Remove the `MCP_TOOL_CATEGORIES` line from your config, or set it to `"all"`.

### "How do I know which tools are loaded?"

The server logs the category configuration on startup:
```
INFO:src.aws_finops_mcp.server_filtered:MCP Tool Categories: cleanup,cost
```

---

## Testing Before Migration

Test category filtering without changing your config:

```bash
# Test with cleanup only
MCP_TOOL_CATEGORIES="cleanup" python -m aws_finops_mcp

# Test with cost and cleanup
MCP_TOOL_CATEGORIES="cleanup,cost" python -m aws_finops_mcp

# Test with all (default)
MCP_TOOL_CATEGORIES="all" python -m aws_finops_mcp
```

---

## Rollback

To rollback, simply remove the `MCP_TOOL_CATEGORIES` environment variable from your config. The server will load all tools as before.

---

## Questions?

- See [TOOL_CATEGORIES.md](TOOL_CATEGORIES.md) for complete documentation
- See [CATEGORY_QUICK_REFERENCE.md](CATEGORY_QUICK_REFERENCE.md) for quick reference
- See [examples/CATEGORY_USE_CASES.md](examples/CATEGORY_USE_CASES.md) for use case examples
