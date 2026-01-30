# Documentation Index

## 📚 Essential Documentation

### 🚀 Deployment Guides (AgentCore)

1. **[AGENTCORE_DEPLOYMENT_FINAL.md](AGENTCORE_DEPLOYMENT_FINAL.md)** ⭐ **START HERE**
   - Complete deployment guide with troubleshooting
   - Solutions for common errors
   - Manual deployment alternatives
   - Post-deployment testing

2. **[AGENTCORE_QUICKSTART.md](AGENTCORE_QUICKSTART.md)**
   - 5-minute quick deployment
   - Minimal steps to get started
   - Best for experienced users

3. **[AGENTCORE_RUNTIME_REVIEW.md](AGENTCORE_RUNTIME_REVIEW.md)**
   - Current deployment status
   - What's been fixed
   - Next steps guide
   - Monitoring and updates

4. **[QUICK_FIX_DEPLOYMENT.md](QUICK_FIX_DEPLOYMENT.md)**
   - Quick fixes for common issues
   - One-liner solutions
   - Troubleshooting tips

5. **[MANUAL_AGENTCORE_DEPLOY.md](MANUAL_AGENTCORE_DEPLOY.md)**
   - Manual Docker deployment
   - Step-by-step ECR push
   - Alternative to `agentcore launch`

### 🔧 Configuration & Setup

6. **[IAM_SETUP_GUIDE.md](IAM_SETUP_GUIDE.md)**
   - IAM policies and permissions
   - Role creation
   - Security best practices

7. **[TOOL_CATEGORIES.md](TOOL_CATEGORIES.md)**
   - Tool category filtering
   - Performance optimization
   - Category descriptions

8. **[TOOLS_REFERENCE.md](TOOLS_REFERENCE.md)**
   - Complete tool reference
   - All 76 tools documented
   - Parameters and examples

### 📖 Quick References

9. **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)**
   - Quick command reference
   - Common use cases
   - Cheat sheet

10. **[CATEGORY_QUICK_REFERENCE.md](CATEGORY_QUICK_REFERENCE.md)**
    - Category-based quick reference
    - Tool selection guide
    - Use case mapping

### 📋 Main Documentation

11. **[README.md](README.md)**
    - Project overview
    - Features and capabilities
    - Getting started
    - Installation instructions

## 🗂️ File Organization

### Configuration Files
- `.bedrock_agentcore.yaml` - AgentCore deployment configuration
- `Dockerfile.agentcore` - Container configuration for AgentCore
- `pyproject.toml` - Python project configuration

### Scripts
- `create-ecr-repo.sh` - Create ECR repository
- `verify-agentcore-ready.sh` - Pre-deployment verification
- `test-agentcore-compatibility.sh` - Test AgentCore compatibility

### IAM Policies
- `iam-policies/` - Ready-to-use IAM policies
  - `finops-full-policy.json` - Full access
  - `finops-readonly-policy.json` - Read-only access
  - `finops-minimal-policy.json` - Minimal permissions
  - `finops-cost-only-policy.json` - Cost tools only

### Examples
- `examples/` - Configuration examples
  - `category-configs/` - Category filtering examples
  - `client-configs/` - MCP client configurations
  - `mcp-client-configs/` - MCP-specific configs

## 🎯 Quick Navigation

### I want to...

**Deploy to AWS AgentCore**
→ Start with [AGENTCORE_DEPLOYMENT_FINAL.md](AGENTCORE_DEPLOYMENT_FINAL.md)

**Fix deployment errors**
→ Check [QUICK_FIX_DEPLOYMENT.md](QUICK_FIX_DEPLOYMENT.md)

**Set up IAM permissions**
→ Read [IAM_SETUP_GUIDE.md](IAM_SETUP_GUIDE.md)

**Filter tools by category**
→ See [TOOL_CATEGORIES.md](TOOL_CATEGORIES.md)

**Find a specific tool**
→ Browse [TOOLS_REFERENCE.md](TOOLS_REFERENCE.md)

**Quick command reference**
→ Use [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

**Understand the project**
→ Read [README.md](README.md)

## 📊 Documentation Status

| Document | Status | Purpose |
|----------|--------|---------|
| AGENTCORE_DEPLOYMENT_FINAL.md | ✅ Current | Primary deployment guide |
| AGENTCORE_QUICKSTART.md | ✅ Current | Quick deployment |
| AGENTCORE_RUNTIME_REVIEW.md | ✅ Current | Status & next steps |
| QUICK_FIX_DEPLOYMENT.md | ✅ Current | Troubleshooting |
| MANUAL_AGENTCORE_DEPLOY.md | ✅ Current | Manual deployment |
| IAM_SETUP_GUIDE.md | ✅ Current | IAM configuration |
| TOOL_CATEGORIES.md | ✅ Current | Category filtering |
| TOOLS_REFERENCE.md | ✅ Current | Tool documentation |
| QUICK_REFERENCE.md | ✅ Current | Command reference |
| CATEGORY_QUICK_REFERENCE.md | ✅ Current | Category reference |
| README.md | ✅ Current | Main documentation |

## 🔄 Recently Removed

The following files were removed as they were redundant or outdated:
- `AGENTCORE_ARCHITECTURE.md` - Merged into deployment guides
- `AGENTCORE_COMPARISON.md` - Info included in final guide
- `BEDROCK_AGENTCORE_DEPLOYMENT.md` - Replaced by final guide
- `DEPLOYMENT_SUMMARY.md` - Redundant
- `DEPLOYMENT_STEPS.md` - Consolidated
- `DEPLOYMENT_CHECKLIST.md` - Integrated into guides
- `DEPLOYMENT.md` - Outdated
- `ARCHITECTURE.md` - Not needed
- `GETTING_STARTED.md` - Replaced by quickstart
- `MIGRATION_GUIDE.md` - Not applicable
- `REMOTE_ACCESS_GUIDE.md` - Not needed for AgentCore
- `deploy-to-agentcore.sh` - Had API compatibility issues

---

**Last Updated**: January 30, 2026

**Need Help?** Start with [AGENTCORE_DEPLOYMENT_FINAL.md](AGENTCORE_DEPLOYMENT_FINAL.md) for the most comprehensive guide.
